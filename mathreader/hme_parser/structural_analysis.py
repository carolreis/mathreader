
from mathreader.helpers import data_structures as DS
from mathreader import helpers
import re
import json
import numpy as np

helpers_labels = helpers.get_labels()
labels = helpers_labels['labels_parser']


class StructuralAnalysis:

    def __init__(self, symbol_list):
        self.symbols = symbol_list

    def analyze(self):

        symbols = self.symbols
        symbols = self.__preprocessing(symbols)
        tree = self.__main_parsing(symbols)
        if not tree:
            return
        tlist = self.__tree_to_list(tree)
        latex = self.__list_to_latex_obj(tlist)

        return {
            'latex': latex,
            'tree': tree,
            'tlist': tlist
        }

    def __preprocessing(self, symbols):
        helpers.debug('[parser.py] preprocessing()')
        xmin_sorted = sorted(symbols, key=lambda i: i['xmin'])
        symbols = xmin_sorted

        for i in range(0, len(symbols)):
            s = symbols[i]
            s['centroid'] = list(s['centroid'])
            s['checked'] = False

            if s['label'] in ['11', '13', '15']:
                s['type'] = 'Open'
            elif s['label'] in ['12', '14', '16']:
                s['type'] = 'Close'
            else:
                s['type'] = 'Normal'

            '''
                Centroid was too below or too above in these cases
                It was changed to: 1/3, 2/3
            '''

            '''
            [0-9] b
            s['ymin'] + (2/3) * (s['ymax'] - s['ymin'])

            y sqrt ()[]{}
            s['centroid'][1] = s['ymin'] + (1/3) * s['h']

            others
            s['centroid'][1] = s['ymin'] + ((s['ymax'] - s['ymin'])/2)
            '''

            '''
            Until validation:
                [0-9], b
            After validation:
                (), {}, [], sqrt
            '''
            if re.search("^[0-9]$", str(s['label'])) or \
                    s['label'] == '19' or s['label'] == '23' or \
                    s['type'] == 'Open' or s['type'] == 'Close':

                s['centroid_class'] = 'Ascending'
                s['centroid'][1] = s['ymin'] + (2/3) * (s['h'])  # 3/5

            elif s['label'] == '25':
                '''
                Until validation:
                    y sqrt ( { [
                After validation:
                    y sqrt
                '''
                s['centroid_class'] = 'Descending'
                s['centroid'][1] = s['ymin'] + (1/3) * s['h']

            else:
                s['centroid_class'] = 'Centred'
                s['centroid'][1] = s['ymin'] + ((s['h']) / 2)

            s['wall'] = {}
            s['wall']['top'] = -1
            s['wall']['bottom'] = 9999999999999
            s['wall']['left'] = -1
            s['wall']['right'] = 9999999999999

        return symbols

    def __main_parsing(self, symbols):
        helpers.debug('\n[parser.py] __main_parsing()')
        listin = symbols
        T = DS.Tree()
        Q = DS.Queue()
        S = DS.Stack()

        temp1 = 0
        temp2 = 0

        R = [[0, 0], [9999999999, 9999999999]]
        sstart = self.__sp(listin, R)

        if sstart == -1:
            return

        helpers.debug('\n[parser.py] __main_parsing() | \
            STARTING symbol index: %d ' % sstart)
        helpers.debug('[parser.py] __main_parsing() | \
            STARTING symbol label: %s ' % listin[sstart]['label'])

        s = listin[sstart]

        Q.enqueue(sstart)
        Q.enqueue(T.root_node)
        listin[sstart]['checked'] = True

        while not Q.is_empty():
            '''
            abc^{2-1}
            =============     ->    | EOBL  |
                        a            | c  |
            =============           | b |
                                    | a |
            '''

            '''
            abc^{2-1]
            =============     ->    |   |
                        2           |   |
            =============           | - |
                                    | 2 |
            '''

            helpers.debug('\n[parser.py] __main_parsing() \
                | find main baseline')

            while not Q.is_empty():
                temp1 = Q.dequeue()  # a, 2
                ParentNode = Q.dequeue()
                SymbolNode = DS.SymbolNode(listin[temp1])
                T.insert(SymbolNode, ParentNode, 'Node')
                S.push(temp1)  # a, 2
                S.push(SymbolNode)

                print('\n[parser.py] __main_parsing() | \
                    find baseline of symbol: ', temp1, listin[temp1]['label'])

                helpers.debug('\n[parser.py] __main_parsing() | \
                    temp2 hor...')
                temp2 = self.__hor(listin, temp1)  # b, -
                print('\n[parser.py] __main_parsing() | \
                    temp2: ', temp2, listin[temp2]['label'])

                while temp2 != -1:
                    print('[parser.py] __main_parsing() | \
                        ... while temp2')
                    listin[temp2]['checked'] = True
                    print('[parser.py] __main_parsing() | \
                        ... wall attributes of temp1: ', listin[temp1]['wall'])
                    listin[temp2]['wall'] = listin[temp1]['wall'].copy()
                    '''
                    a.wall = -1 -1 9999 9999

                    b.checked = true
                    b.wall = a.wall (-1 -1 9999 9999)

                    c.checked = true
                    c.wall = b.wall
                    ---------------------------------------------
                    -.checked = true
                    -.wall = 2.wall (wall da região super?)

                    '''

                    print('[parser.py] __main_parsing() | \
                        ...wall attributes of temp2: ', listin[temp2]['wall'])

                    SymbolNode = DS.SymbolNode(listin[temp2])
                    T.insert(SymbolNode, ParentNode, 'Node')
                    S.push(temp2)
                    S.push(SymbolNode)
                    listin[temp1]['wall']['right'] = listin[temp2]['xmin']

                    '''
                    a.wall.right = b.xmin
                    b.wall.right = c.xmin
                    '''

                    print('[parser.py] __main_parsing() | \
                        ...updated wall attributes \
                        of temp1: ', listin[temp1]['wall'])

                    temp1 = temp2  # b
                    temp2 = self.__hor(listin, temp1)  # c - 1
                    print('[parser.py] __main_parsing() | \
                        new temp2: ', temp2)

            S.push("EOBL")

            helpers.debug('\n[parser.py] __main_parsing() \
                | find secondary baseline')

            '''
            abc^2
            =============     ->    | EOBL  |
                        2           | c  |
            =============           | b |
                                    | a |
            '''
            while not S.is_empty():
                if S.peek() == "EOBL":
                    S.pop()
                SymbolNode = S.pop()
                temp1 = S.pop()  # c

                helpers.debug('[parser.py] __main_parsing() \
                    | symbol: %s ' % temp1)

                label = int(listin[temp1]['label'])
                helpers.debug('[parser.py] __main_parsing() \
                    | temp1 label: %s' % label)

                # 1/6
                upperThreshold = listin[temp1]['ymin'] + \
                    ((1/6.5) * listin[temp1]['h'])
                # 5/6
                lowerThreshold = listin[temp1]['ymin'] + \
                    ((5.5/6.5) * listin[temp1]['h'])

                '''
                    Changes in xmin and xmax because of the 'a'
                    When it overlaps the fraction
                '''
                leftThreshold = (
                        listin[temp1]['xmin'] + ((1/6) * listin[temp1]['w'])
                    ) \
                    if label != 10 else listin[temp1]['xmin']

                rightThreshold = (
                    listin[temp1]['xmax'] - ((1/6) * listin[temp1]['w'])
                    ) \
                    if label != 10 else listin[temp1]['xmax']

                R = [
                    {'above': [
                        [leftThreshold, listin[temp1]['wall']['top']],
                        [rightThreshold, upperThreshold]
                    ]},
                    {'below': [
                        [leftThreshold, lowerThreshold],
                        [rightThreshold, listin[temp1]['wall']['bottom']]
                    ]}
                ]

                for region in R:

                    # For each region, it looks for the initial symbol
                    reg = region[list(region.keys())[0]]
                    region_name = list(region.keys())[0]
                    helpers.debug('\n[parser.py] __main_parsing() | \
                        região: %s' % region_name)

                    # ( ) [ ] { } . * = neq + sqrt
                    operators = bool(label in range(11, 17) or
                    label in range(27, 31) or label == 17 or label == 23)

                    if (region_name == 'above' and not operators) or \
                    (region_name == 'below' and not operators):

                        temp2 = self.__start(listin, reg)

                        if temp2 != -1:
                            if not listin[temp2]['checked']:
                                listin[temp2]['checked'] = True
                                listin[temp2]['wall']['left'] = reg[0][0]
                                listin[temp2]['wall']['right'] = reg[1][0]
                                listin[temp2]['wall']['top'] = reg[0][1]
                                listin[temp2]['wall']['bottom'] = reg[1][1]

                                RelationNode = DS.RegionNode(list(region.keys())[0])
                                T.insert(RelationNode, SymbolNode, 'Node')
                                Q.enqueue(temp2)
                                Q.enqueue(RelationNode)

                '''
                    Changes in xmin and xmax because of the 'a'
                    When it overlaps the fraction
                '''
                R = [
                    {'contains': [
                        # left, top
                        [listin[temp1]['xmin'], listin[temp1]['ymin']],
                        # right, bottom
                        [listin[temp1]['xmax'], listin[temp1]['ymax']]
                    ]},
                    {'super': [
                        # left, top
                        [rightThreshold, listin[temp1]['wall']['top']],
                        # right, bottom
                        [listin[temp1]['wall']['right'], upperThreshold]
                    ]},
                    {'subsc': [
                        # left, top
                        [rightThreshold, lowerThreshold],
                        # right, bottom
                        [
                            listin[temp1]['wall']['right'],
                            listin[temp1]['wall']['bottom']
                        ]
                    ]}
                ]

                for region in R:
                    # Para cada região, busca o símbolo inicial
                    reg = region[list(region.keys())[0]]
                    region_name = list(region.keys())[0]
                    helpers.debug('\n[parser.py] __main_parsing() | \
                        região: %s' % region_name)

                    # - ( ) [ ] { } . * = neq +
                    operators = bool(label == 10 or
                    label in range(27, 31) or label == 17)

                    if (region_name == 'super' and not operators) or \
                    (region_name == 'subsc' and not operators) or \
                    (region_name == 'contains' and \
                    int(listin[temp1]['label']) == 23):

                        temp2 = self.__start(listin, reg)

                        if temp2 != -1:
                            if not listin[temp2]['checked']:
                                listin[temp2]['checked'] = True
                                listin[temp2]['wall']['left'] = reg[0][0]
                                listin[temp2]['wall']['right'] = reg[1][0]
                                listin[temp2]['wall']['top'] = reg[0][1]
                                listin[temp2]['wall']['bottom'] = reg[1][1]

                                RelationNode = DS.RegionNode(list(region.keys())[0])
                                T.insert(RelationNode, SymbolNode, 'Node')
                                Q.enqueue(temp2)
                                Q.enqueue(RelationNode)

        return T

    def __overlap(self, symbolIndex, top, bottom, listin):
        helpers.debug('\n\n[parser.py] __overlap()')
        listIndex = symbolIndex
        stop = False
        n = len(listin)

        helpers.debug('[parser.py] __overlap() | listIndex: %d ' % listIndex)

        if listin[symbolIndex]['label'] == '10':
            maxLength = listin[symbolIndex]['xmax'] - listin[symbolIndex]['xmin']
        else:
            maxLength = -1
        mainLine = -1

        helpers.debug('[parser.py] __overlap() | \
            mainLine: %d ' % mainLine)
        helpers.debug('[parser.py] __overlap() | \
            maxLength: %d ' % maxLength)

        while listIndex > 0 and stop == False:

            print('[parser.py] __overlap() | xmin, xmin',
                listin[listIndex-1]['xmin'],
                listin[symbolIndex]['xmin'])

            if listin[listIndex-1]['xmin'] <= listin[symbolIndex]['xmin']:
                listIndex = listIndex - 1  # stop = True
            else:
                stop = True  # listIndex = listIndex - 1

        helpers.debug('[parser.py] __overlap() | \
            listIndex: %d ' % listIndex)
        helpers.debug('[parser.py] __overlap() | \
            n: %d ' % n)
        helpers.debug('[parser.py] __overlap() | \
            top: %d ' % top)
        helpers.debug('[parser.py] __overlap() | \
            bottom: %d ' % bottom)

        line1x = range(listin[symbolIndex]['xmin'],
                        listin[symbolIndex]['xmax']+1)

        len_line1x = len(line1x)

        while listIndex < n and \
        listin[listIndex]['xmin'] < listin[symbolIndex]['xmax']:

            line2x = range(listin[listIndex]['xmin'],
                            listin[listIndex]['xmax']+1)
            len_line2x = len(line2x)
            x_set = set(line1x) if len_line1x < len_line2x else set(line2x)
            x_intersection = x_set.intersection(line1x if len_line1x >= len_line2x else line2x)
            min_line = min(len_line1x, len_line2x)

            print('\n[parser.py] __overlap() | ... \
                listIndex: ', listIndex)
            print('[parser.py] __overlap() | ... \
                label: ', listin[listIndex]['label'])
            print('[parser.py] __overlap() | ... \
                centroid: ', listin[listIndex]['centroid'])
            print('[parser.py] __overlap() | ... \
                xmin: ', listin[listIndex]['xmin'])
            print('[parser.py] __overlap() | ... \
                xmax: ', listin[listIndex]['xmax'])
            print('[parser.py] __overlap() | ... \
                max length: ', (
                    listin[listIndex]['xmax'] - listin[listIndex]['xmin']))
            print('[parser.py] __overlap() | ... \
                len(x_intersection): ', len(x_intersection))
            print('[parser.py] __overlap() | ... \
                min_line/2: ', min_line/2)

            if not listin[listIndex]['checked'] and \
                listin[listIndex]['label'] == '10' and \
                listin[listIndex]['centroid'][1] >= top and \
                listin[listIndex]['centroid'][1] <= bottom and \
                listin[listIndex]['xmin'] <= (listin[symbolIndex]['xmin'] + 8) and \
                len(x_intersection) > (min_line/2) and \
                (listin[listIndex]['xmax'] - listin[listIndex]['xmin']) > maxLength:
                    maxLength = (listin[listIndex]['xmax'] - listin[listIndex]['xmin'])
                    mainLine = listIndex

            listIndex += 1

        helpers.debug('[parser.py] __overlap() | listIndex: %d ' % listIndex)
        helpers.debug('[parser.py] __overlap() | mainLine: %d ' % mainLine)
        helpers.debug('[parser.py] __overlap() | maxLength: %d ' % maxLength)

        if mainLine == -1:
            return symbolIndex
        else:
            return mainLine

    def __start(self, listin, R):
        helpers.debug('\n[parser.py] __start()')
        print('[parser.py] __start() | region [R]: ', R)

        # Adicionei o round() | tirei o round
        left = R[0][0]
        top = R[0][1]
        right = R[1][0]
        bottom = R[1][1]

        helpers.debug('[parser.py] __start() | region [R]: \
            left: %d, right: %d,\
            top: %d, bottom: %d' %
            (left, right, top, bottom)
        )

        leftmostIndex = -1
        listIndex = 0
        overlapIndex = -1
        n = len(listin)

        while leftmostIndex == -1 and listIndex < n:
            helpers.debug('[parser.py] __start() | ... \
                symbol index: %d' % listIndex)
            helpers.debug('[parser.py] __start() | ... \
                symbol label: %s' % listin[listIndex]['label'])
            print('[parser.py]__start() | ... \
                symbol centroid: ', listin[listIndex]['centroid'])

            if not listin[listIndex]['checked'] and \
                listin[listIndex]['centroid'][0] >= left and \
                listin[listIndex]['centroid'][1] >= top and \
                listin[listIndex]['centroid'][0] <= right and \
                listin[listIndex]['centroid'][1] <= bottom:
                    leftmostIndex = listIndex
            else:
                listIndex = listIndex + 1

        helpers.debug('[parser.py] __start() | \
            leftmostIndex: %d' % leftmostIndex)

        if leftmostIndex == -1:
            return leftmostIndex
        else:
            return self.__overlap(leftmostIndex, top, bottom, listin)

    def __sp(self, listin, R):
        helpers.debug('\n[parser.py] __sp()')
        return self.__start(listin, R)

    def __hor(self, listin, index):
        print('\n[parser.py] __hor()')
        print('[parser.py] __hor() | symbol index: ',
            index)
        print('[parser.py] __hor() | symbol label: ',
            listin[index]['label'])

        global stop
        stop = False
        global a
        a = -1

        label = int(listin[index]['label'])

        right = listin[index]['wall']['right']

        # to avoid get symbols behind
        left = listin[index]['xmin']

        # to treat expoent and subscript
        # 1/6
        top = listin[index]['ymin'] + (listin[index]['h'] * (1/6.5))
        # 5/6
        bottom = listin[index]['ymin'] + (listin[index]['h'] * (5.5/6.5))

        # it doesn't have expoent and subscript
        if label == 10 or label in [27, 28, 29, 30]:
            top = listin[index]['wall']['top']
            bottom = listin[index]['wall']['bottom']

        # if it is square root, the left wall id xmax
        if label == 23:
            left = listin[index]['xmax']

        # if it is horizontal line or brackets
        if label in range(10, 17):
            R = [[listin[index]['xmax'], top], [right, bottom]]
            print('[parser.py] __hor() | R', R)
            a = self.__start(listin, R)
            stop = True

        else:

            helpers.debug('[parser.py] __hor() | top: %d, bottom: %d, \
                left: %d, right: %d' % (top, bottom, left, right))

            for s in range(0, len(listin)):

                checked = listin[s]['checked']

                if not checked:
                    symbol = listin[s]

                    helpers.debug('[parser.py] __hor() | ... \
                        symbol: %s' % symbol['label'])

                    helpers.debug('[parser.py] __hor() | ... \
                        symbol centroid: %s ' % symbol['centroid'])

                    helpers.debug('[parser.py] __hor() | ... \
                        symbol coordinates: xmin: %s xmax: %s \
                        ymin: %s ymax: %s' % (
                            symbol['xmin'], symbol['xmax'],
                            symbol['ymin'], symbol['ymax'])
                        )

                    if symbol['centroid'][0] >= left and \
                        symbol['centroid'][0] <= right and \
                        symbol['centroid'][1] <= bottom and \
                        symbol['centroid'][1] >= top:
                            helpers.debug('[parser.py] __hor() | \
                                ......... founded: %s' % s)
                            a = s
                            stop = True
                            break

                    helpers.debug('[parser.py] __hor() | a: %d ' % a)

        if a != -1:
            helpers.debug('[parser.py] __hor() | \
                a label: %s ' % listin[a]['label'])

        if stop and a != -1:
            helpers.debug('[parser.py] __hor() | ... before overlap')
            return self.__overlap(a, listin[a]['wall']['top'],
                                    listin[a]['wall']['bottom'], listin)
        else:
            return -1

    def __tree_to_list(self, tree, node=None):
        helpers.debug('[parser.py] __tree_to_list()')
        latex = []

        def recur(root_node):
            current = tree.root_node if not root_node else root_node

            if current is None:
                return

            if isinstance(current.data, str):
                latex.append(current.data)
            else:
                try:
                    real_label = labels[current.data['label']]

                    if real_label == '{':
                        real_label = '\\{'
                    if real_label == '}':
                        real_label = '\\}'

                    current.data['label'] = real_label
                    latex.append(current.data)
                except BaseException as e:
                    print('Exception: ', e)

            if current.node_type == 'RegionNode':
                latex.append('{')

            for node in current.children:
                recur(node)

            if current.node_type == 'RegionNode':
                latex.append('}')

        recur(node)

        if latex[0] == 'Expression':
            latex.remove('Expression')
            if latex[-1] == "}":
                latex.pop()
            if latex[0] == '{':
                latex.reverse()
                latex.pop()
                latex.reverse()

        return latex

    def __list_to_latex_obj(self, tlist):
        """ It turns the list into a dict:
            latex.append({
                'label': symbol[],
                'prediction': [],
                'type': ''
            })
        """

        helpers.debug('[parser.py] __list_to_latex_obj()')

        latex = []

        for symbol in tlist:
            if isinstance(symbol, dict):
                latex.append({
                    'label': symbol['label'],
                    'prediction': symbol['prediction'] \
                    if 'prediction' in symbol else [],
                    'type': symbol['type'] or ''
                })
            else:
                latex.append({
                    'label': symbol,
                    'prediction': [],
                    'type': 'context'
                })

        grammar = {
            '-': 'frac',
            'below': 'below',
            'sqrt': 'sqrt',
            'super': 'super',
            '*': 'mult',
            'subsc':  'subsc',
            'neq': 'neq'
        }

        subst = helpers.subst

        print('\n\n')
        latex = self.__token_substitution(latex, grammar, subst)
        print('\n\n')

        return latex

    def __token_substitution(self, latex, grammar, subst):

        def __list_substitution(i, nomatch, aux, initial_index, label,
                                substitution_list, substitution_index):

            for substitution in substitution_list[substitution_index]:
                helpers.debug('[parser.py] __list_to_latex_obj() | \
                    ......substitution: ')  # subsc
                helpers.debug('[parser.py] __list_to_latex_obj() | \
                    ......latex index: %d ' % i)  # subsc
                helpers.debug(substitution)  # subsc

                try:

                    helpers.debug('[parser.py] __list_to_latex_obj() | \
                        ......current latex: %s ' % latex[i]['label'])

                    # latex[i]['label'] = subst[subs][substitution]
                    if latex[i]['label'] == substitution:

                        helpers.debug('[parser.py] __list_to_latex_obj() | \
                            ......match ')

                        helpers.debug('[parser.py] __list_to_latex_obj() | \
                                    ......from: %s %s ' %
                                    (latex[i]['label'], substitution))

                        helpers.debug('[parser.py] __list_to_latex_obj() | \
                                    ......to: %s ' %
                                    substitution_list[substitution_index][substitution])

                        aux.append({
                            "index": i,
                            "label": substitution_list[substitution_index][substitution]
                        })

                        i += 1

                    else:

                        helpers.debug('[parser.py] __list_to_latex_obj() | \
                            ......no match ')

                        i -= 1
                        nomatch = True

                except IndexError as e:
                    helpers.debug('[parser.py] __list_to_latex_obj() | \
                        ......no match: IndexError ')
                    nomatch = True
                    break

                helpers.debug('[parser.py] __list_to_latex_obj() | \
                    ...... no match value: %s ' % nomatch)
                if nomatch:
                    i = initial_index
                    helpers.debug('[parser.py] __list_to_latex_obj() | \
                        ...... continue ......')
                    break
                helpers.debug('[parser.py] __list_to_latex_obj() | \
                    ...... next ......')
            return i, nomatch

        def __change_label(i, label, substitution_list):
            for substitution_index in range(0, len(substitution_list)):
                nomatch = False
                aux = []

                helpers.debug('[parser.py] __list_to_latex_obj() | \
                    ...substitutions: ')
                helpers.debug(substitution_list[substitution_index])

                initial_index = i

                i, nomatch = __list_substitution(i, nomatch, aux,
                                                initial_index,
                                                label, substitution_list,
                                                substitution_index)

                if not nomatch:
                    helpers.debug('[parser.py] __list_to_latex_obj() \
                        | match - updating value ')
                    for matched in aux:
                        latex[matched['index']]['label'] = matched['label']
            return i

        for i in range(0, len(latex)):
            if latex[i]['label'] in grammar:
                label = grammar[latex[i]['label']]

                if label in subst:
                    substitution_list = subst[label]  # list of substitutions
                    helpers.debug('[parser.py] __list_to_latex_obj() \
                        | substitution_list: ')
                    helpers.debug(substitution_list)

                    i = __change_label(i, label, substitution_list)

        return latex

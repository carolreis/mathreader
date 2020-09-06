import re
import json
import numpy as np
from rhme.helpers import data_structures as DS
from rhme.helpers.exceptions import GrammarError, LexicalError, SintaticError
from rhme.hme_parser import check_grammar as cg
from rhme.hme_parser import structural_analysis as sa
from rhme import helpers


class Parser:
    def __init__(self, expression):
        self.symbols = expression['symbols']

    def __remove_contains(self, tstring):
        if isinstance(tstring, str):
            tstring = tstring.replace('contains', '')
        elif isinstance(tstring, list) and "contains" in tstring:
            tstring = tstring.remove('contains')
        return tstring

    def organize_latex_data(self, tstring):
        latex = []
        latex_list = []

        for symbol in tstring:
            if symbol['label'] != '' and symbol['label'] != 'contains':
                latex.append(symbol)
                latex_list.append(symbol['label'])

        latex_string = "".join(latex_list)
        latex_string = self.__remove_contains(latex_string)
        lstring = latex_string

        return {
            'latex': latex,
            'latex_list': latex_list,
            'latex_string': latex_string,
            'lstring': lstring
        }

    def to_parse(self):
        """
        Returns:
            {
                'latex': self.latex,
                'latex_list': self.latex_list,
                'latex_string': self.latex_string,
                'yacc_errors_history': self.yacc_errors_history,
                'lex_errors_history': self.lex_errors_history,
                'yacc_pure_errors': self.pure_yacc_errors,
                'lex_pure_errors': self.pure_lex_errors # It is not being added here
                'latex_before_cg': latex_before_cg,
                'tree': ...,
                'tlist': ...
            }
        """

        helpers.debug('[parser.py] to_parse()')

        try:
            structural_analysis = sa.StructuralAnalysis(self.symbols)
            structured_data = structural_analysis.analyze()

            if not structured_data:
                return

            latex_data = self.organize_latex_data(structured_data['latex'])

            check_grammar = cg.CheckGrammar()
            check_grammar_data = check_grammar.check(latex_data)

            data = {}
            data.update(check_grammar_data)
            data.update({'latex_before_cg': structured_data['latex']})
            data.update({
                'tree': structured_data['tree'],
                'tlist': structured_data['tlist']
            })

            return data

        except Exception as e:
            print('error')
            raise e


# for debuggind
if __name__ == "__main__":

    obj1 = {
        'symbols': [
            {'index': 2, 'xmin': 36, 'xmax': 102, 'ymin': 83, 'ymax': 161, 'w': 66, 'h': 78, 'centroid': [69.0, 80.5], 'label': '2'},
            {'index': 3, 'xmin': 109, 'xmax': 148, 'ymin': 48, 'ymax': 96, 'w': 39, 'h': 48, 'centroid': [128.5, 48.0], 'label': '2'},
            {'index': 0, 'xmin': 205, 'xmax': 245, 'ymin': 100, 'ymax': 147, 'w': 40, 'h': 47, 'centroid': [225.0, 73.5], 'label': '18'},
            {'index': 1, 'xmin': 300, 'xmax': 344, 'ymin': 88, 'ymax': 158, 'w': 44, 'h': 70, 'centroid': [322.0, 79.0], 'label': '5'}
        ]
    }

    obj2 = {
        'symbols': [
            {'index': 1, 'xmin': 143, 'xmax': 588, 'ymin': 197, 'ymax': 216, 'w': 445, 'h': 19, 'centroid': [365.5, 108.0], 'label': '11'},
            {'index': 4, 'xmin': 174, 'xmax': 534, 'ymin': 32, 'ymax': 199, 'w': 360, 'h': 167, 'centroid': [354.0, 99.5], 'label': '25'},
            {'index': 2, 'xmin': 280, 'xmax': 364, 'ymin': 92, 'ymax': 173, 'w': 84, 'h': 81, 'centroid': [322.0, 86.5], 'label': '19'},
            {'index': 0, 'xmin': 302, 'xmax': 428, 'ymin': 254, 'ymax': 358, 'w': 126, 'h': 104, 'centroid': [365.0, 179.0], 'label': '27'},
            {'index': 3, 'xmin': 379, 'xmax': 477, 'ymin': 60, 'ymax': 166, 'w': 98, 'h': 106, 'centroid': [428.0, 83.0], 'label': '20'}
        ]
    }

    a = Parser(obj1)
    print(a.to_parse())

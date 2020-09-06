import numpy as np
from rhme import helpers
from rhme.hme_parser.grammar import lex as lex
from rhme.hme_parser.grammar import yacc as yacc

helpers_labels = helpers.get_labels()
labels = helpers_labels['labels_parser']


class CorrectGrammar():

    def __init__(self):
        pass

    def correct_grammar_lex(self, errors, latex, latex_list, index=0,
                            previous_errors=[]):
        """Fix grammar and lex errors.
        It tries to fix one error at the time.
        The error index is passed as parameter,
        otherwise, the first error (index=0) will be used.

        Args:
            errors (list): Errors found in previous step:
                either
                check_grammar_lex.py or check_grammar_sintax.py
            latex (list): First latex structure.
            latex_list (list): [description]
            index (int, optional): Index of error. Default to 0.
            previous_errors (list, optional):
                This list stores all previous symbol (index) attemptions
                to fix the error. Defaults to [].

        Returns:
            latex_string, errors, index: Updated data.
        """
        latex_string = ""

        helpers.debug("\n[base_grammar.py] correct_grammar_lex() | \
            List of errors: {0}".format(errors))

        previous_attemptions = []

        # It adds previous attempts to the array
        for error in previous_errors:
            helpers.debug('Previous error: {0}'.format(error))
            if error['attempts'] and len(error['attempts']) > 0:
                previous_attemptions.extend(error['attempts'])

        helpers.debug('Previous attemptions: {0}'.format(previous_attemptions))

        if len(errors) > 0:

            pos = errors[index]['pos']
            pos_list = errors[index]['pos_list']
            pred = errors[index]['prediction'].copy()

            subst = helpers.subst

            # When there's predictions it is a numpy array, not a list.
            if not isinstance(pred, list):

                json_label = 'labels_parser'

                def get_new_index(pred):
                    helpers.debug("[base_grammar.py] correct_grammar_lex() | \
                        Reset prediction of current symbol")
                    new_pred = pred.copy()
                    new_pred[0][np.argmax(pred)] = 0
                    helpers.debug("[base_grammar.py] correct_grammar_lex() | \
                        Gets new index and prediction from \
                        next index with higher prediction")
                    new_index = np.argmax(new_pred)
                    return new_index, new_pred

                def recur_get_new_index(pred):
                    new_index, pred = get_new_index(pred)
                    label_recog = helpers_labels[json_label][str(new_index)]
                    new_label = helpers_labels["labels_recognition"][label_recog]
                    new_identification = labels[new_label]

                    if new_identification in errors[index]['attempts'] or \
                    new_identification in previous_attemptions:

                        helpers.debug("[base_grammar.py] \
                            correct_grammar_lex() | \
                            New index is in previous attempts. Getting next.")

                        return recur_get_new_index(pred)

                    else:

                        if new_identification == '{':
                            new_identification = '\\{'
                        if new_identification == '}':
                            new_identification = '\\}'

                        return new_index, pred, new_identification

                new_index, new_pred, new_identification = recur_get_new_index(pred)
                helpers.debug("[base_grammar.py] correct_grammar_lex() | \
                    New symbol identification: %s " % new_identification)

                errors[index]['prediction'] = new_pred
                errors[index]['attempts'].append(new_identification)

                # Make it more 'Pythonic' later
                if new_identification in subst:

                    # list of substitutions
                    substitution_list = subst[new_identification]
                    for substitution_index in range(0, len(substitution_list)):
                        for substitution in substitution_list[substitution_index]:
                            if new_identification == substitution:
                                new_identification = substitution_list[substitution_index][substitution]

                '''
                    Updated 'latex' and 'latex_list'.
                    It is NOT a copy so, it is already updated.
                '''
                latex_list[pos_list] = new_identification
                latex[pos_list]['label'] = new_identification
                latex[pos_list]['prediction'] = new_pred
                latex_string = latex_string.join(latex_list)

        return {
            'latex_string': latex_string or "".join(latex_list),
            'errors': errors,
            'index': index
        }

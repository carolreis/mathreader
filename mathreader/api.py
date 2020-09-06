from mathreader import helpers
from mathreader.hme_parser import parser as parser
from mathreader.recognize import *
from mathreader.config import Configuration as config
import numpy as np
import cv2
import base64


class HME_Recognizer:

    def __init__(self):
        self.reset()

    def reset(self):
        self.image = None
        self.parsed_expression = ""
        self.processed_image = None
        self.predictions = None
        self.configurations = None
        self.expression_after_recognition = {}
        self.expression_after_parser = []
        self.expression_after_grammar = ""
        self.parser_tree = None
        self.parser_list = None
        self.yacc_errors_history = None
        self.yacc_pure_errors = None
        self.lex_errors_history = None
        self.lex_pure_errors = None

    def __to_parse(self, expression):
        try:
            parse = parser.Parser(expression)
            parsed_data = parse.to_parse()

            if not parsed_data:
                return

            self.yacc_errors_history = parsed_data['yacc_errors_history']
            self.yacc_pure_errors = parsed_data['yacc_pure_errors']
            self.lex_errors_history = parsed_data['lex_errors_history']
            self.lex_pure_errors = parsed_data['lex_pure_errors']
            self.latex_string_original = parsed_data['latex_string_original']
            self.expression_after_parser = parsed_data['latex_before_cg']
            self.expression_after_grammar = parsed_data['latex']
            self.parser_tree = parsed_data['tree']
            self.parser_list = parsed_data['tlist']

            return parsed_data['latex_string']

        except Exception as e:
            print("[api.py] __to_parse | Exception:")
            raise e

    def load_image(self, image, data_type='base64'):
        try:
            if data_type == 'base64':
                im_bytes = base64.b64decode(image)
                im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
                img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

            elif data_type == 'path':
                img = cv2.imread(image, 0)

            elif data_type == 'byte':
                im_arr = np.frombuffer(image, dtype=np.uint8)
                img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

            else:
                raise Exception('Wrong file format. Should be: \
                    base64, path, byte.')

            self.image = img

        except BaseException as e:
            self.image = None
            raise e

    def recognize(self):
        try:
            img = self.image
            print(type(img))
            if isinstance(img, np.ndarray) and len(img) > 0:
                hme = Recognize(img)

                expression, image = hme.to_recognize()

                self.expression_after_recognition = expression.copy()
                self.predictions = hme.prediction

                parsed_expression = self.__to_parse(expression)

                if not parsed_expression:
                    raise Exception("Error")

                self.parsed_expression = parsed_expression
                self.processed_image = image

                return parsed_expression, image
            else:
                print("[api.py] recognize | \
                    Exception: You must enter an image")
                raise Exception("You must enter an image.")
        except Exception as e:
            print("[api.py] recognize | Exception:", e)
            raise e

    def get_predictions(self):
        return self.predictions

    def get_labels(self):
        labels = helpers.get_labels()
        return labels

    def get_expression_before_parser(self):
        return self.expression_before_parser

    def get_expression_after_parser(self):
        return self.expression_after_parser

    def get_expression_before_grammar(self):
        return self.expression_before_grammar

    def get_expression_after_grammar(self):
        return self.expression_after_grammar

    def get_yacc_errors(self):
        return self.yacc_errors_history

    def get_yacc_pure_errors(self):
        return self.yacc_pure_errors

    def get_lex_errors(self):
        return self.lex_errors_history

    def get_lex_pure_errors(self):
        return self.lex_pure_errors

    def get_latex_string_original(self):
        return self.latex_string_original

    def configuration(self):
        return config

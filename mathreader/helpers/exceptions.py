import json


class GrammarError(Exception):
    def __init__(self, data=None, valor="Could not solve the grammar error"):
        self.valor = valor
        self.data = data

    def __repr__(self):
        return {
            'message': self.valor,
            'data': self.data
        }

    def __str__(self):
        return self.valor


class SintaticError(Exception):
    def __init__(self, data=None, valor="Could not solve the sintatic error"):
        self.valor = valor
        self.data = data

    def __repr__(self):
        return {
            'message': self.valor,
            'data': self.data
        }

    def __str__(self):
        return self.valor


class LexicalError(Exception):
    def __init__(self, data=None, valor="Could not solve the lexical error"):
        self.valor = valor
        self.data = data

    def __repr__(self):
        return {
            'message': self.valor,
            'data': self.data
        }

    def __str__(self):
        return self.valor

Lex errors:
    errors.append((t.value[0], t.lexpos))

lex_errors_history:
    {           
        'pos': latex_error_pos,
        'pos_list': count_list,
        'label': symbol['label'],
        'prediction': symbol['prediction'],
        'attempts': [latex_error_pos] # Stores the symbol attempts to restore the grammar
    }

Lexical Error Exception:
    raise LexicalError({
        'latex': self.latex,
        'latex_list': self.latex_list,
        'latex_string': self.latex_string,
        'error': self.lex_error_list, # Current error
        'errors_history': self.lex_errors_history,
        'pure_errors': self.pure_lex_errors
    })

Check Lex Return:
    return {
        'latex': self.latex,
        'latex_list': self.latex_list,
        'latex_string': self.latex_string, 
        'errors_history': self.lex_errors_history,
        'pure_errors': self.pure_lex_errors
    }

---------------------------------------------------------------------------------

Yacc errors:
    erro = {
        'lexpos': None,
        'lineno': None,
        'type': None,
        'value': None
    }

yacc_errors_history:
    yacc_errors.append({
        'pos': latex_error_pos,
        'pos_list': count_list,
        'label': symbol['label'],
        'prediction': symbol['prediction'],
        'attempts': [latex_error_pos]
    })

Yacc Error Exception:
    raise GrammarError({
        'latex': self.latex,
        'latex_list': self.latex_list,
        'latex_string': self.latex_string,
        'error': self.yacc_error_list, # Current error
        'errors_history': self.yacc_errors_history,
        'pure_errors': self.pure_yacc_errors
    })

Check Yacc Return
    return {
        'latex': self.latex,
        'latex_list': self.latex_list,
        'latex_string': self.latex_string, 
        'yacc_errors_history': self.yacc_errors_history,
        'lex_errors_history': self.lex_errors_history,
        'yacc_pure_errors': self.pure_yacc_errors,
        'lex_pure_errors': self.pure_lex_errors # Não está sendo adicionado aqui
    }

---------------------------------------------------------------------------------

Latex Data Types:
    Latex: {'label': symbol, 'prediction': [], 'type': 'context'}
    Latex List: ['\sqrt','{','9','}']
    Latex String: '\sqrt{9}'

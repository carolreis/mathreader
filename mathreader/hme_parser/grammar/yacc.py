from mathreader.hme_parser.grammar import lex
from mathreader.hme_parser.grammar.lex import tokens
import ply.yacc as yacc

def LatexParse(latex):
    error_list = []
    acceptance = []

    def p_gl(p):
        'GL : EL'
        # print('Aceita')
        acceptance.append('p_gl')

    def p_el_er_eq_er(p):
        'EL : ER EQ ER'
        acceptance.append('p_el_er_eq_er')

    def p_el_er_neq_er(p):
        'EL : ER NEQ ER'
        acceptance.append('p_el_er_neq_er')

    def p_el_er_eq(p):
        'EL : ER EQ'
        acceptance.append('p_el_er_eq')

    def p_el_er_neq(p):
        'EL : ER NEQ'
        acceptance.append('p_el_er_neq')

    def p_el_er(q):
        'EL : ER'
        acceptance.append('p_el_er')

    def p_er_er_plus_t(p):
        'ER : T PLUS ER'
        acceptance.append('p_er_er_plus_t')

    def p_er_er_min_t(p):
        'ER : T MIN ER'
        acceptance.append('p_er_er_min_t')

    def p_er_t(p):
        'ER : T'
        acceptance.append('p_er_t')

    def p_er_t_subsc_cdot_t(p):
        'T : SUBSC CDOT T'
        acceptance.append('p_er_t_subsc_cdot_t')

    def p_er_t_subsc(p):
        'T : SUBSC '
        acceptance.append('p_er_t_subsc')

    def p_er_subsc_pw_sub_subsc(p):
        'SUBSC : PW SUB SUBSC'
        acceptance.append('p_er_subsc_pw_sub_subsc')

    def p_er_subsc_pw(p):
        'SUBSC : PW'
        acceptance.append('p_er_subsc_pw')

    # def p_t_t_cdot_pw(p):
    #     'T : PW CDOT T'
    #     acceptance.append('p_t_t_cdot_pw')

    # def p_t_pw(p):
    #     'T : PW'
    #     acceptance.append('p_t_pw')

    def p_pw_pw_pow_fr(p):
        'PW : FR POW PW'
        acceptance.append('p_pw_pw_pow_fr')

    def p_pw_fr(p):
        'PW : FR'
        acceptance.append('p_pw_fr')

    def p_fr_lfrac(p):
        'FR : LFRAC OPENC ER CLOSEDC OPENC ER CLOSEDC'
        acceptance.append('p_fr_lfrac')

    def p_fr_s_lfrac(p):
        'FR : S LFRAC OPENC ER CLOSEDC OPENC ER CLOSEDC'
        acceptance.append('p_fr_s_lfrac')

    def p_fr_s(p):
        'FR : S'
        acceptance.append('p_fr_s')

    def p_s_sqrt(p):
        'S : SQRT OPENC ER CLOSEDC'
        acceptance.append('p_s_sqrt')

    def p_s_s_sqrt(p):
        'S : S SQRT OPENC ER CLOSEDC'
        acceptance.append('p_s_s_sqrt')

    def p_s_f_s (p):
        'S : S F'
        acceptance.append('p_s_f')

    def p_s_plus_f(p):
        'S : PLUS F'
        acceptance.append('p_s_lus_f')

    def p_s_min_f(p):
        'S : MIN F'
        acceptance.append('p_s_min_f')

    def p_s_f(p):
        'S : F'
        acceptance.append('p_s_f')

    def p_f_number(p):
        'F : NUMBER'
        acceptance.append('p_f_number')

    def p_f_var(p):
        'F : VAR'
        acceptance.append('p_f_var')

    def p_f_p(p):
        'F : P'
        acceptance.append('p_f_p')

    def p_p_openp(p):
        'P : OPENP ER CLOSEDP'
        acceptance.append('p_p_openp')

    def p_p_c(p):
        'P : C'
        acceptance.append('p_p_c')

    def p_c_openco(p):
        'C : OPENCO ER CLOSEDCO'
        acceptance.append('p_c_openco')

    def p_c_b(p):
        'C : B'
        acceptance.append('p_c_openc')

    def p_b_openc(p):
        'B : OPENC ER CLOSEDC'
        acceptance.append('p_b_openc')

    def p_error(p):
        global parser

        print("Syntax error in input!", p)

        erro = {
            'lexpos': None,
            'lineno': None,
            'type': None,
            'value': None
        }

        if p:
            erro.update({
                'lexpos': p.lexpos,
                'lineno': p.lineno,
                'type': p.type,
                'value': p.value
            })

        error_list.append(erro)

    parser = yacc.yacc()
    result = parser.parse(latex)

    if result:
        print("[yacc.py] Result: ", result)

    return error_list

if __name__ == "__main__":
    LatexParse(input(':'))
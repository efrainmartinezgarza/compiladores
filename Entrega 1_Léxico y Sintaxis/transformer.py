from lark import Transformer, v_args

@v_args(inline=True) 
class MyTransformer(Transformer):

    # ----------------------------------------------------------------------------------------------------------------------------

    """ID: LETTER (LETTER | DIGIT | UNDERSCORE)*"""
    def ID(self, id):
        return {"type": "id", "value": str(id)}
    
    def STRING(self, string):
        return {"type": "string", "value": str(string)[1:-1]}  # Eliminar comillas de inicio y fin
    
    # ----------------------------------------------------------------------------------------------------------------------------
    
    """?factor: L_PARENTHESIS expression R_PARENTHESIS -> factor_expression
    | ID -> factor_id
    | CTE -> factor_cte
    | MINUS factor -> factor_minus  
    | PLUS factor -> factor_plus  """

    def factor_expression(self, lpar, expression, rpar):
        return {"type": "factor_expression", "value": expression}

    def factor_id(self, id):
        return {"type": "factor_id", "value": id}

    def factor_cte(self, cte):
        return {"type": "factor_cte", "value": float(cte) if '.' in cte else int(cte)}

    def factor_minus(self, minus, factor):
        return {"type": "factor_minus", "value": -factor}

    def factor_plus(self, plus, factor):
        return {"type": "factor_plus", "value": -factor}
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """?term: factor -> term_simple
     | term (MULT_SIGN factor)+ -> term_mult_sign
     | term (DIV_SIGN factor)+ -> term_div_sign"""
    
    def term_simple(self, factor):
        return {"type": "term_simple", "value": factor}
    
    def _handle_term(self, term, rest, type):
        if isinstance(term, list):
            items = term
        else:
            items = [term]

        for i in range(0, len(rest), 2):
            operator = str(rest[i])
            next_term = rest[i + 1]
            items.append(operator)
            items.append(next_term)

        return {"type": "term", "value": items}
        
    def term_mult_sign(self, term, *rest):
        return self._handle_term(term, rest, "term_mult_sign")

    def term_div_sign(self, term, *rest):
        return self._handle_term(term, rest, "term_div_sign")
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """?exp: term -> exp_simple
     | exp (PLUS term)+ -> exp_plus
     | exp (MINUS term)+ -> exp_minus"""
    
    def exp_simple(self, term):
        return {"type": "exp_simple", "value": term}
    
    def _handle_exp(self, exp, rest, type):

        if isinstance(exp, list):
            items = self._flatten(exp)
        else:
            items = [exp]

        for i in range(0, len(rest), 2):
            operator = str(rest[i]) 
            next_term = rest[i + 1]
            
            next_term_flat = self._flatten(next_term)
            
            items.append(operator)
            items.extend(next_term_flat)  

        return {"type": "exp", "value": items}

    def _flatten(self, value):
        """ Aplana cualquier lista que contenga sublistas. """
        if isinstance(value, list):
            flat = []
            for item in value:
                flat.extend(self._flatten(item))  
            return flat
        else:
            return [value] 
    
    def exp_plus(self, exp, *rest):
        return self._handle_exp(exp, rest, "exp_plus")
    
    def exp_minus(self, exp, *rest):
        return self._handle_exp(exp, rest, "exp_minus")
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """expression: exp -> expression_simple
        | exp GREATER_THAN exp -> expression_greater_than
        | exp LESS_THAN exp -> expression_less_than
        | exp NOT_EQUAL exp -> expression_not_equal"""
    
    def expression_simple(self, exp):
        return {"type": "expression_simple", "value": exp}
    
    def expression_greater_than(self, exp1, gt, exp2):
        return {"type": "expression_greater_than", "value": [exp1, str(gt), exp2]}
    
    def expression_less_than(self, exp1, lt, exp2):
        return {"type": "expression_less_than", "value": [exp1, str(lt), exp2]}
    
    def expression_not_equal(self, exp1, ne, exp2):
        return {"type": "expression_not_equal", "value": [exp1, str(ne), exp2]}
    
    # ----------------------------------------------------------------------------------------------------------------------------

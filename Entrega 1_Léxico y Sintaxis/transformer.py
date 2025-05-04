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

    """print: PRINT_KWORD L_PARENTHESIS STRING R_PARENTHESIS SEMICOLON -> print_string
        | PRINT_KWORD L_PARENTHESIS expression R_PARENTHESIS SEMICOLON -> print_expression
        | PRINT_KWORD L_PARENTHESIS expression (COMMA expression)+ R_PARENTHESIS SEMICOLON -> print_multiple_expressions
    """
    
    def print_string(self, print_kw, lpar, string, rpar, semicolon):
        return {"type": "print_string", "value": string}  
    
    def print_expression(self, print_kw, lpar, expression, rpar, semicolon):
        return {"type": "print_expression", "value": expression}  
    
    def print_multiple_expressions(self, print_kw, lpar, first_expr, *rest):
        expressions = [first_expr] 

        for i in range(0, len(rest)-2, 2):
            
            next_item = rest[i + 1]
            expressions.append(next_item) 

        return {
            "type": "print_multiple_expressions",
            "value": expressions
        }
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """f_call: ID L_PARENTHESIS R_PARENTHESIS SEMICOLON -> f_call_simple
        | ID L_PARENTHESIS expression R_PARENTHESIS SEMICOLON -> f_call_one_expression
        | ID L_PARENTHESIS expression (COMMA expression)+ R_PARENTHESIS SEMICOLON -> f_call_multiple_expressions"""
    
    def f_call_simple(self, id, lpar, rpar, semicolon):
        return {"type": "f_call_simple", "value": str(id)}
    
    def f_call_one_expression(self, id, lpar, expression, rpar, semicolon):
        return {"type": "f_call_one_expression", "function": str(id), "value": expression}
    
    def f_call_multiple_expressions(self, id, lpar, expression, *rest):
        
        expressions = [expression]
        for i in range(0, len(rest)-2, 2):
            next_item = rest[i + 1]
            expressions.append(next_item)
        return {"type": "f_call_multiple_expressions", "function": str(id), "value": expressions
        }
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """assign: ID EQUAL expression SEMICOLON"""

    def assign(self, id, equal, expression, semicolon):
        return {
            "type": "assign",
            "id": id,
            "value": expression
        }
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """statement: assign | condition | cycle | f_call | print"""
    def statement(self, assign):
        return {
            "type": "statement",
            "value": assign
        }
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """body: L_CURLY_BRACE R_CURLY_BRACE -> body_simple
        | L_CURLY_BRACE statement+ R_CURLY_BRACE -> body_statement"""
    
    def body_simple(self, lcurly, rcurly):
        return {
            "type": "body_simple",
            "value": []
        }
    
    def body_statement(self, lcurly, *rest):
        statements = []
        for i in range(0, len(rest)-1, 1):
            statement = rest[i]
            statements.append(statement)
        return {
            "type": "body_statement",
            "value": statements
        } 
      
    # ----------------------------------------------------------------------------------------------------------------------------

    """cycle: WHILE_KWORD L_PARENTHESIS expression R_PARENTHESIS DO_KWORD body SEMICOLON"""

    def cycle(self, while_kw, lpar, expression, rpar, do_kw, body, semicolon):
        return {
            "type": "cycle",
            "condition": expression,
            "body": body
        }
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """condition: IF_KWORD L_PARENTHESIS expression R_PARENTHESIS body SEMICOLON -> condition_if
        | IF_KWORD L_PARENTHESIS expression R_PARENTHESIS body ELSE_KWORD body SEMICOLON -> condition_if_else"""
    
    def condition_if(self, if_kw, lpar, expression, rpar, body, semicolon):
        return {
            "type": "condition_if",
            "condition": expression,
            "body": body
        }
    
    def condition_if_else(self, if_kw, lpar, expression, rpar, body1, else_kw, body2, semicolon):
        return {
            "type": "condition_if_else",
            "condition": expression,
            "body1": body1,
            "body2": body2
        }
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """type: INT_KWORD -> type_int
    | FLOAT_KWORD -> type_float"""

    def type_int(self, int_kword):
        return {"type": "type_int", "value": "int"}

    def type_float(self, float_kword):
        return {"type": "type_float", "value": "float"}
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """vars: VAR_KWORD (ID COLON type SEMICOLON)+ -> vars_one_id
        | VAR_KWORD (ID (COMMA ID)* COLON type SEMICOLON)+ -> vars_multiple_ids"""
    
    def vars_one_id(self, var_kw, *rest):
        declarations = []
        i = 0

        while i < len(rest):
            # ID
            id_token = rest[i]
            i += 1

            # COLON
            if i < len(rest) and rest[i] == ':':
                i += 1

            # type
            type_token = rest[i]
            i += 1

            # SEMICOLON
            if i < len(rest) and rest[i] == ';':
                i += 1

            # Guardar declaración
            declarations.append({
                "id": str(id_token),
                "type": str(type_token)
            })

        return {
            "type": "vars_one_id",
            "declarations": declarations
        }
    
    def vars_multiple_ids(self, var_kw, *rest):
        declarations = []
        i = 0

        while i < len(rest):
            ids = []

            ids.append(str(rest[i]))
            i += 1

            while i < len(rest) and rest[i] == ',':
                i += 1  # Saltamos la coma
                ids.append(str(rest[i]))
                i += 1

            if i < len(rest) and rest[i] == ':':
                i += 1  # Saltamos el :

            var_type = str(rest[i])
            i += 1

            if i < len(rest) and rest[i] == ';':
                i += 1

            declarations.append({
                "ids": ids,
                "type": var_type
            })

        return {
            "type": "vars_multiple_ids",
            "declarations": declarations
        }
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """funcs: VOID_KWORD ID L_PARENTHESIS R_PARENTHESIS L_BRACKET vars body R_BRACKET SEMICOLON -> funcs_simple
        | VOID_KWORD ID L_PARENTHESIS ID COLON type R_PARENTHESIS L_BRACKET vars body R_BRACKET SEMICOLON -> funcs_id
        | VOID_KWORD ID L_PARENTHESIS ID COLON type (COMMA ID COLON type)+ R_PARENTHESIS L_BRACKET vars body R_BRACKET SEMICOLON -> funcs_multiple_ids"""
    
    def funcs_simple(self, void_kw, id, lpar, rpar, lbracket, vars, body, rbracket, semicolon):
        return {
            "type": "funcs_simple",
            "funcs_name": str(id),
            "vars": vars,
            "body": body
        }
    
    def funcs_id(self, void_kw, id, lpar, param, colon, param_type, rpar, lbracket, vars, body, rbracket, semicolon):
        return {
            "type": "funcs_id",
            "funcs_name": str(id),
            "param": str(param),
            "param_type": str(param_type),
            "vars": vars,
            "body": body
        }
    
    def funcs_multiple_ids(self, void_kw, id, lpar, param, colon, param_type, *rest):
        
        parameters = [{"id": str(param), "type": str(param_type)}]
        i = 0

        for i in range(0, len(rest)-6, 4):
            
            param_id = rest[i + 1]
            param_type = rest[i + 3]

            parameters.append({
                "id": str(param_id),
                "type": str(param_type)
            })

        vars_node = rest[-4]
        body_node = rest[-3]

        return {
            "type": "funcs_multiple_ids",
            "funcs_name": str(id),
            "parameters": parameters,
            "vars": vars_node,
            "body": body_node
        }
    
    # ----------------------------------------------------------------------------------------------------------------------------

    """program: PROGRAM_KWORD ID SEMICOLON MAIN_KWORD body END_KWORD -> program_simple
        | PROGRAM_KWORD ID SEMICOLON vars MAIN_KWORD body END_KWORD -> program_vars
        | PROGRAM_KWORD ID SEMICOLON vars funcs+ MAIN_KWORD body END_KWORD -> program_vars_funcs
        | PROGRAM_KWORD ID SEMICOLON funcs+ MAIN_KWORD body END_KWORD -> program_funcs"""
    
    def program_simple(self, program_kw, id, semicolon, main_kw, body, end_kw):
        return {
            "type": "program_simple",
            "program_name": id,
            "body": body
        }
    
    def program_vars(self, program_kw, id, semicolon, vars, main_kw, body, end_kw):
        return {
            "type": "program_vars",
            "program_name": id,
            "vars": vars,
            "body": body
        }
    
    def program_vars_funcs(self, program_kw, id, semicolon, vars, *rest):
        
        funcs = []

        for i in range(0, len(rest)-3, 1):
            func = rest[i]
            funcs.append(func)

        body = rest[-2]

        return {
            "type": "program_vars_funcs",
            "program_name": id,
            "vars": vars,
            "funcs": funcs,
            "body": body
        }
    
    def program_funcs(self, program_kw, id, semicolon, *rest):
            
            funcs = []
    
            for i in range(0, len(rest)-3, 1):
                func = rest[i]
                funcs.append(func)
    
            body = rest[-2]
    
            return {
                "type": "program_funcs",
                "program_name": id,
                "funcs": funcs,
                "body": body
            }
    

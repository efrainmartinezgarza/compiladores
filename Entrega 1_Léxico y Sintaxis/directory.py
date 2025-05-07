from semantic_cube import SemanticCube

class Directory:

    # Palabras reservadas del lenguaje BabyDuck.
    RESERVED_WORDS = {
        "program", "var", "int", "float", "void",
        "main", "if", "else", "while", "do", "print"
    }
    
    # Constructor de la clase Directory. Inicializa el cubo semántico, el directorio de funciones y el scope actual.
    def __init__(self):
        self.cube = SemanticCube()
        self.func_dir = {
            "global": {
                "params": [],
                "vars": {}
            }
        }
        self.built_in_functions = {"print": {"params": []}}
        self.current_scope = "global"
        self.program_ast = None  
        self.is_executing = False  

    # ----------------------------------------------------------------------------------------------------------------------------
    # Gestión de funciones en el directorio de funciones. Se pueden agregar funciones y establecer el scope actual.

    def add_function(self, func_name, params=None, var_table=None, body=None):
        if func_name in Directory.RESERVED_WORDS:
            raise NameError(f"El nombre '{func_name}' es una palabra reservada.")
        if func_name in self.func_dir:
            raise NameError(f"La función '{func_name}' ya está declarada.")
        self.func_dir[func_name] = {
            "params": params or [],
            "vars": var_table or {},
            "body": body  
        }

    def set_current_scope(self, scope_name):
        if scope_name not in self.func_dir:
            raise NameError(f"El scope '{scope_name}' no existe.")
        self.current_scope = scope_name

    def get_current_vars(self):
        return self.func_dir[self.current_scope]["vars"]

    # ----------------------------------------------------------------------------------------------------------------------------
    # Gestión de variables en el scope actual (global o función).

    def declare_variable(self, var_id, var_type):
        if var_id in Directory.RESERVED_WORDS:
            raise NameError(f"El nombre '{var_id}' es una palabra reservada.")
        current_vars = self.get_current_vars()
        if var_id in current_vars:
            raise NameError(f"La variable '{var_id}' ya está declarada en el scope '{self.current_scope}'.")
        current_vars[var_id] = {
            "type": var_type,
            "assigned": False
        }

    def assign_variable(self, var_id, expr_node):
        if self.is_executing:
            value = self.evaluate_expression(expr_node)
            var_info = self.func_dir[self.current_scope]["vars"][var_id]
            self.validate_type_match(var_id, var_info["type"], value)
            var_info.update({
                "assigned": True,
                "value": value
            })
        else:
            self.validate_expression_uses(expr_node)

    def use_variable(self, var_id):
        var = self.find_variable(var_id)
        if var is None:
            raise NameError(f"La variable '{var_id}' no está declarada.")
        if not var["assigned"]:
            raise ValueError(f"La variable '{var_id}' se usa sin haber sido inicializada.")

    def find_variable(self, var_id):
        current_vars = self.get_current_vars()
        if var_id in current_vars:
            return current_vars[var_id]
        elif var_id in self.func_dir["global"]["vars"]:
            return self.func_dir["global"]["vars"][var_id]
        else:
            return None

    # ----------------------------------------------------------------------------------------------------------------------------
    # Validaciones de expresiones y asignaciones en el AST.
   
    def validate_expression_uses(self, expression_node):
        if isinstance(expression_node, dict):
            expr_type = expression_node.get("type")
            if expr_type == "factor_id":
                var_id = expression_node["value"]["value"]
                var = self.find_variable(var_id)
                if var is None:
                    raise NameError(f"Variable '{var_id}' no declarada.")
            else:
                for key, value in expression_node.items():
                    self.validate_expression_uses(value)
        elif isinstance(expression_node, list):
            for item in expression_node:
                self.validate_expression_uses(item)

    def validate_assign(self, assign_node):
        var_id = assign_node["id"]["value"]
        var = self.find_variable(var_id)
        if var is None:
            raise NameError(f"La variable '{var_id}' no está declarada.")
        self.assign_variable(var_id, assign_node.get("value"))

    def validate_function_call(self, call_node):
        if call_node.get("type") == "f_call_simple":
            func_name = call_node["value"]["value"]
            args = []
        elif call_node.get("type") == "f_call_one_expression":
            func_name = call_node["function"]["value"]
            args = [call_node["value"]]
        elif call_node.get("type") == "f_call_multiple_expressions":
            func_name = call_node["function"]["value"]
            args = call_node.get("value", [])
        else:
            raise ValueError("Tipo de llamada a función desconocido.")

        if func_name in self.built_in_functions:
            return
        if func_name not in self.func_dir:
            raise NameError(f"Función '{func_name}' no definida.")

        expected_params = self.func_dir[func_name]["params"]
        for i, param in enumerate(expected_params):
            arg_value = self.evaluate_expression(args[i])
            self.validate_type_match(param["id"], param["type"], arg_value)

        if len(args) != len(expected_params):
            raise TypeError(f"Función '{func_name}' espera {len(expected_params)} argumentos, pero se recibieron {len(args)}.")

    # ----------------------------------------------------------------------------------------------------------------------------
   # Extras: Impresión de la tabla de funciones y variables para depuración.

    def print_func_dir(self):
        for scope, info in self.func_dir.items():
            print(f"Scope: {scope}")
            
            # Mostrar parámetros si existen
            if info["params"]:
                print("  Parámetros:")
                for param in info["params"]:
                    print(f"    {param['id']} : {param['type']}")

            # Mostrar variables locales/globales
            vars_info = info["vars"]
            if isinstance(vars_info, dict):
                print("  Variables:")
                for var_id, var_data in vars_info.items():
                    # Saltar elementos que no sean información de variable
                    if not isinstance(var_data, dict):
                        continue
                    value_str = f"= {var_data['value']}" if var_data.get("assigned") else "(sin valor)"
                    print(f"    {var_id} : {var_data['type']} {value_str}")
            print()  # Salto entre scopes

    # ----------------------------------------------------------------------------------------------------------------------------
    # Evaluación de expresiones aritméticas y lógicas en el AST.

    def evaluate_expression(self, expr):
        if not isinstance(expr, dict):
            return expr  # Si es un número o Token, devolver directamente

        expr_type = expr.get("type")

        # Caso base: constante numérica
        if expr_type == "factor_cte":
            return expr["value"]

        # Variable
        if expr_type == "factor_id":
            var_name = expr["value"]["value"]
            return self.get_variable_value(var_name)

        # Expresión entre paréntesis
        if expr_type == "factor_expression":
            return self.evaluate_expression(expr["value"])

        if expr_type == "factor_minus":
            value = self.evaluate_expression(expr["value"])
            return -value

        # Término simple (ej. factor)
        if expr_type == "term_simple":
            return self.evaluate_expression(expr["value"])

        # Expresión simple (ej. exp_simple)
        if expr_type == "exp_simple":
            return self.evaluate_expression(expr["value"])

        # Soportar expression_simple
        if expr_type == "expression_simple":
            return self.evaluate_expression(expr["value"])  

        # Operaciones binarias aritméticas
        if expr_type in ["term", "exp"]:
            items = expr["value"]
            left = self.evaluate_expression(items[0])
            for i in range(1, len(items), 2):
                op = items[i]
                right = self.evaluate_expression(items[i + 1])
                self.validate_operation(left, right, op)
                if op == "+": left += right
                elif op == "-": left -= right
                elif op == "*": left *= right
                elif op == "/": left = left // right
                else:
                    raise ValueError(f"Operador desconocido: {op}")
            return left

        # Comparaciones
        if expr_type == "expression_greater_than":
            left = self.evaluate_expression(expr["value"][0])
            right = self.evaluate_expression(expr["value"][2])
            return int(left > right)  # 0 = false, 1 = true

        if expr_type == "expression_less_than":
            left = self.evaluate_expression(expr["value"][0])
            right = self.evaluate_expression(expr["value"][2])
            return int(left < right)  # 0 = false, 1 = true

        if expr_type == "expression_not_equal":
            left = self.evaluate_expression(expr["value"][0])
            right = self.evaluate_expression(expr["value"][2])
            return int(left != right)  # 0 = false, 1 = true

        raise ValueError(f"No se puede evaluar la expresión: {expr_type}")

    def get_variable_value(self, var_name):
        var = self.find_variable(var_name)
        if var is None or not var["assigned"]:
            raise NameError(f"Variable '{var_name}' no tiene valor asignado.")
        return var["value"]

    def validate_type_match(self, var_id, var_type, value):
        if isinstance(value, int):
            value_type = "int"
        elif isinstance(value, float):
            value_type = "float"
        else:
            raise TypeError(f"Tipo no soportado para el valor de '{var_id}'")

        if var_type == "int" and value_type != "int":
            raise TypeError(f"No se puede asignar {value_type} a variable int '{var_id}'")
        elif var_type == "float" and value_type not in ("int", "float"):
            raise TypeError(f"No se puede asignar {value_type} a variable float '{var_id}'")

    def validate_operation(self, left_value, right_value, operator):
        left_type = "int" if isinstance(left_value, int) else "float"
        right_type = "int" if isinstance(right_value, int) else "float"
        try:
            result_type = self.cube.get_result_type(left_type, right_type, operator)
            return result_type
        except TypeError as e:
            raise TypeError(f"Error en operación '{operator}': {e}")

    # ----------------------------------------------------------------------------------------------------------------------------
    # Análisis semántico del AST

    def analyze(self, ast):
        self.is_executing = False
        if not isinstance(ast, dict):
            raise ValueError("AST inválido o vacío.")

        program_type = ast.get("type")
        if program_type == "program_simple":
            self.analyze_body(ast["body"])
        elif program_type == "program_vars":
            self.analyze_vars(ast["vars"], is_global=True)
            self.analyze_body(ast["body"])
        elif program_type == "program_funcs":
            for func in ast.get("funcs", []):
                self.analyze_function(func)
            self.analyze_body(ast["body"])
        elif program_type == "program_vars_funcs":
            self.analyze_vars(ast["vars"], is_global=True)
            for func in ast.get("funcs", []):
                self.analyze_function(func)
            self.analyze_body(ast["body"])
        else:
            raise ValueError(f"Tipo de programa desconocido: {program_type}")
        print("Análisis semántico completado correctamente.")

    def analyze_function(self, func_node):
        func_name = func_node["funcs_name"].get("value", func_node["funcs_name"]["value"])

        params = []
        if func_node["type"] == "funcs_id":
            param = func_node["param"]
            param_type = func_node["param_type"]["value"]
            params.append({"id": param["value"], "type": param_type})
        elif func_node["type"] == "funcs_multiple_ids":
            for p in func_node.get("parameters", []):
                params.append({
                    "id": p["id"]["value"],
                    "type": p["type"]["value"]
                })

        self.add_function(
            func_name,
            params=params,
            var_table=func_node.get("vars"),            
            body=func_node.get("body")
        )

        self.set_current_scope(func_name)

        for param in params:
            self.declare_variable(param["id"], param["type"])

        if "vars" in func_node and func_node["vars"]:
            self.analyze_vars(func_node["vars"])

        if "body" in func_node:
            self.analyze_body(func_node["body"])
        else:
            print(f"La función '{func_name}' no tiene cuerpo definido.")

        self.set_current_scope("global")

    def analyze_vars(self, vars_node, is_global=False):
        declarations = []
        if vars_node["type"] == "vars_one_id":
            declarations = vars_node["declarations"]
        elif vars_node["type"] == "vars_multiple_ids":
            for d in vars_node["declarations"]:
                for id_token in d["ids"]:
                    declarations.append({"id": id_token, "type": d["type"]})

        for decl in declarations:
            var_id = decl["id"]["value"]
            var_type = decl["type"]["value"]
            if is_global:
                self.set_current_scope("global")
            self.declare_variable(var_id, var_type)

    def analyze_body(self, body_node):
        if body_node is None:
            return

        if body_node.get("type") == "body_statement":
            for stmt in body_node.get("value", []):
                self.analyze_statement(stmt)
        else:
            raise ValueError(f"Tipo de cuerpo desconocido: {body_node.get('type')}")

    def analyze_statement(self, stmt_node):
        if not isinstance(stmt_node, dict):
            raise ValueError("Nodo de sentencia inválido.")
        stmt_type = stmt_node.get("type")
        if stmt_type == "statement":
            inner_stmt = stmt_node.get("value")
            self.analyze_statement(inner_stmt)
        elif stmt_type == "assign":
            self.validate_assign(stmt_node)
        elif stmt_type in ["print_expression", "print_string", "print_multiple_expressions"]:
            for expr in stmt_node.get("value", [stmt_node]):
                self.validate_expression_uses(expr)
        elif "f_call" in stmt_type:
            self.validate_function_call(stmt_node)
        elif "condition" in stmt_type:
            self.analyze_condition(stmt_node)
        elif stmt_type == "cycle":
            self.analyze_cycle(stmt_node)
        else:
            raise ValueError(f"Sentencia desconocida: {stmt_type}")

    def analyze_condition(self, cond_node):
        self.validate_expression_uses(cond_node.get("condition"))

        if "body" in cond_node:
            self.analyze_body(cond_node["body"])
        elif "body1" in cond_node:
            self.analyze_body(cond_node["body1"])

        if cond_node["type"] == "condition_if_else":
            if "body2" in cond_node:
                self.analyze_body(cond_node["body2"])
            elif "else_block" in cond_node:
                self.analyze_body(cond_node["else_block"])

    def analyze_cycle(self, cycle_node):
        self.validate_expression_uses(cycle_node["condition"])
        self.analyze_body(cycle_node["body"])

    def validate_assign(self, assign_node):
        var_id = assign_node["id"]["value"]
        var = self.find_variable(var_id)
        if var is None:
            raise NameError(f"La variable '{var_id}' no está declarada.")
        self.assign_variable(var_id, assign_node.get("value"))

    def set_program_ast(self, ast):
        self.program_ast = ast

    # ----------------------------------------------------------------------------------------------------------------------------
    #Ejecución del programa

    def execute_program(self):
        if not hasattr(self, "program_ast"):
            raise RuntimeError("No hay AST cargado para ejecutar.")
        self.is_executing = True
        program_type = self.program_ast.get("type")
        body = None
        if program_type in ["program_simple", "program_vars"]:
            body = self.program_ast["body"]
        elif program_type == "program_funcs":
            body = self.program_ast["body"]
        elif program_type == "program_vars_funcs":
            body = self.program_ast["body"]
        else:
            raise ValueError(f"Tipo de programa desconocido: {program_type}")

        print("Iniciando ejecución del cuerpo principal...")
        self.set_current_scope("global")
        self.execute_body(body)

    def execute_body(self, body_node):
        if body_node is None:
            print("Cuerpo vacío o nulo.")
            return

        if body_node.get("type") == "body_statement":
            for stmt in body_node.get("value", []):
                self.execute_statement(stmt)
        else:
            raise ValueError(f"Tipo de cuerpo desconocido: {body_node.get('type')}")

    def execute_statement(self, stmt_node):
        if not isinstance(stmt_node, dict):
            raise ValueError("Nodo de sentencia inválido.")
        
        stmt_type = stmt_node.get("type")
        
        if stmt_type == "statement":
            inner_stmt = stmt_node.get("value")
            self.execute_statement(inner_stmt)
        elif stmt_type == "assign":
            self.execute_assign(stmt_node)
        elif stmt_type in ["print_expression", "print_string", "print_multiple_expressions"]:
            self.execute_print(stmt_node)
        elif "f_call" in stmt_type:
            self.execute_function_call(stmt_node)
        elif "condition" in stmt_type:
            self.execute_condition(stmt_node)
        elif stmt_type == "cycle":
            self.execute_cycle(stmt_node)
        else:
            raise ValueError(f"Sentencia desconocida: {stmt_type}")

    def execute_assign(self, assign_node):
        var_id = assign_node["id"]["value"]
        expr_node = assign_node["value"]
        value = self.evaluate_expression(expr_node)
        if var_id not in self.func_dir[self.current_scope]["vars"]:
            raise NameError(f"Variable '{var_id}' no declarada.")
        var_info = self.func_dir[self.current_scope]["vars"][var_id]
        self.validate_type_match(var_id, var_info["type"], value)
        var_info.update({
            "assigned": True,
            "value": value
        })
    
    def execute_print(self, print_node):
        expr_list = []
        
        if print_node["type"] == "print_expression":
            expr_list.append(print_node["value"])
        elif print_node["type"] == "print_multiple_expressions":
            expr_list.extend(print_node["value"])
        elif print_node["type"] == "print_string":
            message = print_node["value"]["value"]
            print(message)
            return
        else:
            raise ValueError(f"Sentencia de impresión desconocida: {print_node['type']}")

        output = []
        for expr in expr_list:
            value = self.evaluate_expression(expr)
            output.append(str(value))
        
        print(", ".join(output))

    def execute_function_call(self, call_node):
        if call_node.get("type") == "f_call_simple":
            func_name = call_node["value"]["value"]
            args = []
        elif call_node.get("type") == "f_call_one_expression":
            func_name = call_node["function"]["value"]
            args = [call_node["value"]]
        elif call_node.get("type") == "f_call_multiple_expressions":
            func_name = call_node["function"]["value"]
            args = call_node.get("value", [])
        else:
            raise ValueError(f"Tipo de llamada a función desconocida: {call_node.get('type')}")

        if func_name in self.built_in_functions:
            return

        if func_name not in self.func_dir:
            raise NameError(f"Función '{func_name}' no definida.")

        expected_params = self.func_dir[func_name]["params"]
        if len(args) != len(expected_params):
            raise TypeError(f"Función '{func_name}' espera {len(expected_params)} argumentos, pero se recibieron {len(args)}.")
        
        self.set_current_scope(func_name)

        for i, param in enumerate(expected_params):
            var_id = param["id"]
            expr_node = args[i]
            value = self.evaluate_expression(expr_node)
            var_info = self.func_dir[func_name]["vars"][var_id]
            self.validate_type_match(var_id, var_info["type"], value)
            var_info.update({
                "assigned": True,
                "value": value
            })

        self.execute_body(self.func_dir[func_name]["body"])

        self.set_current_scope("global")

    def execute_condition(self, cond_node):
        condition = self.evaluate_expression(cond_node.get("condition"))
        if condition:

            if "body" in cond_node:
                self.execute_body(cond_node["body"])
            elif "body1" in cond_node:
                self.execute_body(cond_node["body1"])
            else:
                raise ValueError("Nodo de condición no contiene cuerpo válido.")
        else:
            if "body2" in cond_node:
                self.execute_body(cond_node["body2"])
            elif "else_block" in cond_node:
                self.execute_body(cond_node["else_block"])
        
    def execute_cycle(self, cycle_node):
        while True:
            condition = self.evaluate_expression(cycle_node["condition"])
            if not condition:
                break
            self.execute_body(cycle_node["body"])

    def simplify_value_structure(self, data):
        """
        Limpia recursivamente las estructuras del AST para mostrar solo valores útiles.
        """
        if isinstance(data, dict):
            if "value" in data and len(data) == 2 and "type" in data:
                return self.simplify_value_structure(data["value"])
            
            simplified = {}
            for key, value in data.items():
                if key == "type":
                    continue
                simplified[key] = self.simplify_value_structure(value)
            return simplified
        
        elif isinstance(data, list):
            return [self.simplify_value_structure(item) for item in data]
        
        else:
            return data

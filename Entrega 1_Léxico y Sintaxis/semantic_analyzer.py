"""Verifica la semántica del programa.
Permite examinar cosas como que las variables están declaradas antes de usarse,
que las funciones están definidas antes de llamarse, y que los tipos de datos son correctos.
"""

from lark.lexer import Token
class SemanticAnalyzer:

    def __init__(self, directory, quad_gen, memory_manager):
        self.dir = directory # Acceso al directorio de funciones y variables
        self.quad_gen = quad_gen
        self.memory_manager = memory_manager # Acceso al generador de cuádruplos

    # Método principal para analizar el AST (árbol de sintaxis abstracta) del programa.
    def analyze(self, ast):

        # Obtiene el tipo de programa (program_simple, program_vars, etc.) y llama al método correspondiente.
        t = ast.get("type")

        self.quad_gen.generate_go("goTo")
        jump_start = self.quad_gen.jumps_stack.pop() # Se guarda la posición del goTo al inicio del programa

        if t == "program_simple": # Programa simple (sin variables ni funciones)
            self.quad_gen.fill_jump(jump_start)
            self.analyze_body(ast["body"])
        elif t == "program_vars": # Programa con variables (sin funciones)
            self.analyze_vars(ast["vars"], True)
            self.quad_gen.fill_jump(jump_start)
            self.analyze_body(ast["body"])
        elif t == "program_funcs": # Programa con funciones (sin variables)
            for f in ast.get("funcs", []):
                self.analyze_function(f)
                self.quad_gen.generate_ENDFUNC_quad()
            self.quad_gen.fill_jump(jump_start)
            self.analyze_body(ast["body"]) 
        elif t == "program_vars_funcs": # Programa con variables y funciones
            self.analyze_vars(ast["vars"], True) # Se pone "True" para indicar que son variables globales
            for f in ast.get("funcs", []):
                self.analyze_function(f)
                self.quad_gen.generate_ENDFUNC_quad()
            self.quad_gen.fill_jump(jump_start)
            self.analyze_body(ast["body"])
        else:
            raise ValueError(f"Tipo de programa desconocido: {t}")

    # Analiza una función específica dentro del programa.
    def analyze_function(self, func_node):

        # Obtención del nombre de la función.
        func_name = func_node["funcs_name"]["value"]

        # Creación de una lista para almacenar los parámetros de la función.
        params = []

        # Dependiendo del tipo de función, se obtienen los parámetros y el tipo de cada uno.
        if func_node["type"] == "funcs_id": # Función con un solo parámetro 

            # Se obtiene el nombre del parámetro
            param = func_node["param"]

            # Se obtiene el tipo del parámetro
            ptype = func_node["param_type"]["value"]

            # Se agrega el parámetro a la lista de parámetros
            params.append({"id": param["value"], "type": ptype})
        
        elif func_node["type"] == "funcs_multiple_ids": # Función con múltiples parámetros

            # Se recorre la lista de parámetros y se almacena su nombre y tipo en la lista de parámetros
            for p in func_node.get("parameters", []):
                params.append({
                    "id": p["id"]["value"],
                    "type": p["type"]["value"]
                })
           
        # Se guarda la posición del cuádruplo de inicio de la función
        start_point = len(self.quad_gen.filaCuadruplos)

        # Almacena la función en el directorio de funciones.
        # Guarda el nombre de la función, los parámetros y el cuerpo de la función.
        self.dir.add_function(func_name, start_point, params, func_node.get("vars"), func_node.get("body"))

        # Establece la función como el ámbito actual (scope)
        self.dir.set_current_scope(func_name)

        # Declaración de los parámetros de la función como variables dentro del ámbito de la función.
        for p in params:
            address = self.memory_manager.generate_address(p["type"], "local")
            self.dir.declare_variable(p["id"], p["type"], address, True) # True indica que es un parámetro

            # Se actualiza el número de recursos utilizados (parámetros) en el directorio de funciones.
            self.dir.update_resource(func_name, "params", p["type"])

        # Si la función tiene variables locales, se declaran también.
        # Se recorre la lista de variables y se declaran en el ámbito de la función.
        if func_node.get("vars"):
            self.analyze_vars(func_node["vars"])
        
        # Se analiza el cuerpo de la función.
        self.analyze_body(func_node["body"])

        # Al finalizar el análisis de la función, se vuelve al ámbito global.
        self.dir.set_current_scope("global")


    # Función para analizar las variables dentro de una función o en el ámbito global.
    def analyze_vars(self, vars_node, is_global=False):

        # Crea una lista para almacenar las declaraciones de variables.
        declarations = []

        # Dependiendo del tipo de declaración de variables, se obtienen los identificadores y tipos.
        if vars_node["type"] == "vars_one_id": # Declaración de una sola variable
            declarations = vars_node["declarations"]

        elif vars_node["type"] == "vars_multiple_ids": # Declaración de múltiples variables
            for d in vars_node["declarations"]:
                for id_token in d["ids"]:
                    declarations.append({"id": id_token, "type": d["type"]})
        
        # Se recorre la lista de declaraciones y se declaran las variables en el directorio.
        for decl in declarations:

            # Se obtiene el identificador y el tipo de la variable.
            var_id = decl["id"]["value"]
            var_type = decl["type"]["value"]

            # Si se hizo un análisis de variables globales, se establece el ámbito como "global".
            # En caso contrario, se establece el ámbito actual de la función en el que se están declarando las variables.
            if is_global:
                self.dir.set_current_scope("global")
                address = self.memory_manager.generate_address(var_type, "global")
            else:
                address = self.memory_manager.generate_address(var_type, "local")

            # Se declara la variable en el directorio de funciones.
            self.dir.declare_variable(var_id, var_type, address)

            # Se actualiza el numero de recursos utilizados (variables) en el directorio de funciones.
            self.dir.update_resource(self.dir.current_scope, "vars", var_type)

    # Método para analizar el cuerpo de una función o del programa principal.
    def analyze_body(self, body_node):

        # Si el cuerpo está vacío, no se hace nada.
        if body_node is None:
            return
        
        # Dependiendo del tipo de cuerpo, se analizan las declaraciones de variables o las sentencias.
        if body_node["type"] == "body_statement":

            # Recorre la lista de sentencias y las analiza una por una
            for stmt in body_node["value"]:
                self.analyze_statement(stmt)
        else:
            raise ValueError(f"Tipo de cuerpo desconocido: {body_node.get('type')}") 
    
    # Método para analizar una sentencia específica dentro del cuerpo.
    def analyze_statement(self, stmt_node):
        t = stmt_node.get("type")

        if t == "statement":
            self.analyze_statement(stmt_node["value"])

        elif t == "assign":
            self.validate_assign(stmt_node) 
            var_id = stmt_node["id"]["value"]
            self.analyze_expression(stmt_node["value"])
            self.quad_gen.generate_assignment_quad(var_id)
            # Se marca la variable como asignada
            self.dir.find_variable(var_id)["assigned"] = True

        elif "f_call" in t:
            self.validate_function_call(stmt_node)

        elif t == "print_expression":
            # Si hay multiples valores a imprimir
            if isinstance(stmt_node["value"], list):
                count = len(stmt_node["value"])
                for i in stmt_node["value"]:
                    self.validate_expression_uses(i)
                    self.analyze_expression(i)
                    self.quad_gen.generate_print_quad()

            else:
                # Si solo hay un valor a imprimir
                self.validate_expression_uses(stmt_node["value"])
                self.analyze_expression(stmt_node["value"])                
                self.quad_gen.generate_print_quad()

        elif t == "print_string":
            #self.validate_expression_uses(stmt_node["value"])
            value = stmt_node["value"]["value"]
            # Se genera un address para la cadena
            if(self.memory_manager.get_constant_address(value, "string") == None):
                address = self.memory_manager.add_constant(value, "string")
            else:
                address = self.memory_manager.get_constant_address(value, "string")

            self.quad_gen.push_operand(address, "string")
            self.quad_gen.generate_print_quad()

        elif "condition" in t:
            self.analyze_expression(stmt_node["condition"])  
            self.quad_gen.generate_go("goToFalse")
            false_jump = self.quad_gen.jumps_stack.pop()

            # Analiza body del if
            if t == "condition_if":
                self.analyze_body(stmt_node["body"])

                # No hay else, llena salto falso directamente
                self.quad_gen.fill_jump(false_jump)

            elif t == "condition_if_else":
                self.analyze_body(stmt_node["body1"])  # Cuerpo del if

                # Hay else, entonces genero un goTo al final
                self.quad_gen.generate_go("goTo")
                end_jump = self.quad_gen.jumps_stack.pop()

                self.quad_gen.fill_jump(false_jump)  # Falso va al else
                self.analyze_body(stmt_node["body2"])  # Cuerpo del else

                self.quad_gen.fill_jump(end_jump)  # Fin del else

        elif t == "cycle":
            # Se guarda la ubicación del inicio del ciclo
            loop_start = len(self.quad_gen.filaCuadruplos)

            # Se valúa la condición
            self.analyze_expression(stmt_node["condition"])

            # Se genera un salto si la condición es falsa
            self.quad_gen.generate_go("goToFalse")
            false_jump = self.quad_gen.jumps_stack.pop() #se guarda posición del goToFalse (-1)

            # Analizar el body del while
            self.analyze_body(stmt_node["body"])

            # Se genera salto para volver a checar la condición del while
            self.quad_gen.generate_go("goTo")
            back_jump = self.quad_gen.jumps_stack.pop() #se guarda la posición del goTo (-1)

            # Se rellena el salto hacia el inicio 
            self.quad_gen.fill_jump(back_jump, loop_start)

            # Se rellena el salto falso para salir del ciclo 
            self.quad_gen.fill_jump(false_jump)

          

    # Verifica que las variables utilizadas en las expresiones estén declaradas.
    def validate_expression_uses(self, node):
        
        # Si el nodo es un diccionario.
        if isinstance(node, dict):
            t = node.get("type") 

            # Si el nodo es un identificador, se busca su valor en el directorio.
            # Si no se encuentra, se lanza un error indicando que la variable no está declarada.
            if t == "factor_id":
                var_id = node["value"]["value"]
                var = self.dir.find_variable(var_id)
                if var is None:
                    raise NameError(f"Variable '{var_id}' no declarada.")
            else: # Si el nodo es más complejo, se recorre su contenido.
                for v in node.values():
                    self.validate_expression_uses(v)

        # Si el nodo es una lista, se recorre cada elemento de la lista.            
        elif isinstance(node, list):
            for i in node:
                self.validate_expression_uses(i)

    # Se asegura de que la variable esté declarada.
    def validate_assign(self, assign_node):

        # Obtención del nombre de la variable.
        var_id = assign_node["id"]["value"]

        # Se busca la variable en el directorio de funciones.
        var = self.dir.find_variable(var_id)

        # Si no se encuentra, se lanza un error indicando que la variable no está declarada.
        if var is None:
            raise NameError(f"La variable '{var_id}' no está declarada.")
    
        self.validate_expression_uses(assign_node["value"])

    # Método para validar la llamada a una función.
    # Verifica que la función esté definida y que los tipos de los argumentos sean correctos.
    def validate_function_call(self, call_node):
        
        func_name = ""
        args = []
        
        # Dependiendo del tipo de llamada a función, se obtienen el nombre de la función y los argumentos.
        if call_node.get("type") == "f_call_simple":
            func_name = call_node["value"]["value"]
        elif call_node.get("type") == "f_call_one_expression":
            func_name = call_node["function"]["value"]
            args = [call_node["value"]]
        elif call_node.get("type") == "f_call_multiple_expressions":
            func_name = call_node["function"]["value"]
            args = call_node.get("value", [])
        
        # Si la función es una función predeterminada se omite la validación (eje. print).
        if func_name in self.dir.built_in_functions:
            return
        
        # Si la función no está definida en el directorio de funciones, se lanza un error.
        if func_name not in self.dir.func_dir:
            raise NameError(f"Función '{func_name}' no definida.")
        
        # Se genera el cuádruplo de llamada a la función.
        self.quad_gen.generate_functionCall_quad("ERA", func_name)

        # Almacena los parámetros esperados de la función.
        expected = self.dir.func_dir[func_name]["params"]
        print(f"Parámetros esperados: {expected}")

        # Si el número de argumentos no coincide con el número de parámetros esperados, se lanza un error.
        if len(args) != len(expected):
            raise TypeError(f"Función '{func_name}' espera {len(expected)} args, recibió {len(args)}.")
        
        for i, param in enumerate(expected):
            arg_expr = args[i]
            
            # Analiza la expresión del argumento para obtener su tipo
            self.analyze_expression(arg_expr)
            
            # Obtiene el tipo desde pilaTipos 
            arg_type = self.quad_gen.pilaTipos[-1]  # No quitar aún, solo leer  
    
            if arg_type != param["type"]:
                raise TypeError(f"Argumento '{param['id']}' debe ser '{param['type']}', recibido '{arg_type}'")
            
            # Se genera el cuádruplo del parametro
            self.quad_gen.generate_param_quad()
        
        # Se genera el cuádruplo que marca el fin de la función llamada.
        self.quad_gen.generate_functionCall_quad("goSub", func_name)
    
    def analyze_expression(self, expr):
        if isinstance(expr, dict):
            t = expr.get("type")

            if t == "factor_cte":
                value = expr["value"]
                value_type = "int" if isinstance(value, int) else "float"

                # Generación de address para la constante
                if(self.memory_manager.get_constant_address(value, value_type) == None):
                    address = self.memory_manager.add_constant(value, value_type)
                else:
                    address = self.memory_manager.get_constant_address(value, value_type)

                self.quad_gen.push_operand(address, value_type)

            elif t == "factor_id":
                    var_id = expr["value"]["value"]

                    # Buscar información de la variable (tipo, dirección, asignada, etc.)
                    var_info = self.dir.find_variable(var_id)
                    if var_info is None:
                        raise Exception(f"Error semántico: la variable '{var_id}' no está declarada.")

                    var_type = var_info["type"]  # Obtener el tipo desde el directorio

                    # Verificar que haya sido inicializada antes de usarse
                    if not var_info.get("assigned", False):
                        raise Exception(f"Error semántico: la variable '{var_id}' se usa antes de ser inicializada.")

                    # Obtener la dirección desde el directorio (ya está asignada durante declaración)
                    address = var_info.get("address")
                    if address is None:
                        raise Exception(f"Error interno: la variable '{var_id}' no tiene dirección asignada.")

                    # Empujar operando y tipo a las pilas del generador de cuádruplos
                    self.quad_gen.push_operand(address, var_type)

            elif t == "factor_expression":
                self.analyze_expression(expr["value"])

            elif t == "factor_minus":
                self.analyze_expression(expr["value"])

            elif t in ["term_simple", "exp_simple", "expression_simple"]:
                self.analyze_expression(expr["value"])

            elif t in ["term", "exp"]:
                items = expr["value"]
                self.analyze_expression(items[0])
                i = 1
                while i < len(items):
                    token_or_op = items[i]
                    if isinstance(token_or_op, Token):
                        self.quad_gen.push_operator(token_or_op.value)
                        i += 1
                        self.analyze_expression(items[i])
                        self.quad_gen.generate_quad_if_applicable()
                    else:
                        self.analyze_expression(token_or_op)
                    i += 1

            elif t in ["expression_greater_than", "expression_less_than", "expression_not_equal"]:
                op_map = {
                    "expression_greater_than": ">",
                    "expression_less_than": "<",
                    "expression_not_equal": "!="
                }
                self.analyze_expression(expr["value"][0])
                self.analyze_expression(expr["value"][2])
                self.quad_gen.push_operator(op_map[t])
                self.quad_gen.generate_quad_if_applicable()

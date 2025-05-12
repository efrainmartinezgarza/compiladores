"""Verifica la semántica del programa.
Permite examinar cosas como que las variables están declaradas antes de usarse,
que las funciones están definidas antes de llamarse, y que los tipos de datos son correctos.
"""

class SemanticAnalyzer:

    def __init__(self, directory, evaluator):
        self.dir = directory # Acceso al directorio de funciones y variables
        self.eval = evaluator # Acceso al evaluador de expresiones
        self.is_executing = False # Indica si se está ejecutando el programa

    # Método principal para analizar el AST (árbol de sintaxis abstracta) del programa.
    def analyze(self, ast):

        # Se asegura de que el programa no esté en ejecución antes de comenzar el análisis.
        self.is_executing = False

        # Obtiene el tipo de programa (program_simple, program_vars, etc.) y llama al método correspondiente.
        t = ast.get("type")
        if t == "program_simple": # Programa simple (sin variables ni funciones)
            self.analyze_body(ast["body"])
        elif t == "program_vars": # Programa con variables (sin funciones)
            self.analyze_vars(ast["vars"], True)
            self.analyze_body(ast["body"])
        elif t == "program_funcs": # Programa con funciones (sin variables)
            for f in ast.get("funcs", []):
                self.analyze_function(f)
            self.analyze_body(ast["body"]) 
        elif t == "program_vars_funcs": # Programa con variables y funciones
            self.analyze_vars(ast["vars"], True) # Se pone "True" para indicar que son variables globales
            for f in ast.get("funcs", []):
                self.analyze_function(f)
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
        
        # Almacena la función en el directorio de funciones.
        # Guarda el nombre de la función, los parámetros y el cuerpo de la función.
        self.dir.add_function(func_name, params, func_node.get("vars"), func_node.get("body"))

        # Establece la función como el ámbito actual (scope)
        self.dir.set_current_scope(func_name)

        # Declaración de los parámetros de la función como variables dentro del ámbito de la función.
        for p in params:
            self.dir.declare_variable(p["id"], p["type"])

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
            
            # Se declara la variable en el directorio de funciones.
            self.dir.declare_variable(var_id, var_type)

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

        # Almacena el tipo de sentencia que se está analizando.
        t = stmt_node.get("type")

        # Dependiendo del tipo de sentencia, se realizan diferentes validaciones.
        if t == "assign":
            self.validate_assign(stmt_node) 
        elif "f_call" in t:
            self.validate_function_call(stmt_node)
        elif "print" in t:
            # Se valida la expresión dentro de los print
            for expr in stmt_node.get("value", [stmt_node]):
                self.validate_expression_uses(expr)
        elif "condition" in t:
            self.analyze_body(stmt_node.get("body"))
        elif t == "cycle":
            self.analyze_body(stmt_node.get("body"))

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

    # Se asegura de que la variable esté declarada y que el tipo de dato sea correcto.
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

        # Almacena los parámetros esperados de la función.
        expected = self.dir.func_dir[func_name]["params"]

        # Si el número de argumentos no coincide con el número de parámetros esperados, se lanza un error.
        if len(args) != len(expected):
            raise TypeError(f"Función '{func_name}' espera {len(expected)} args, recibió {len(args)}.")
        
        # Se recorre la lista de parámetros esperados y se valida el tipo de cada argumento.
        for i, param in enumerate(expected):

            # Se obtiene el valor del argumento evaluando la expresión.
            val = self.eval.evaluate(args[i])

            # Se valida que el tipo del argumento coincida con el tipo esperado.
            self.eval.validate_type_match(param["id"], param["type"], val)

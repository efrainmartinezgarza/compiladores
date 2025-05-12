"""Evaluador de expresiones para el lenguaje de programación.
Este módulo se encarga de evaluar expresiones aritméticas y lógicas,
así como de validar tipos y operaciones entre variables."""

class ExpressionEvaluator:

    # Constructor de la clase ExpressionEvaluator.
    def __init__(self, directory):
        self.dir = directory # Acceso al directorio de funciones y variables
        self.cube = directory.cube # Acceso al cubo semántico para validar operaciones

    # Método para evaluar una expresión.
    # Recibe una expresión en forma de árbol sintáctico y devuelve su valor.
    def evaluate(self, expr):

        # En caso de que la expresión sea un valor literal (int o float), se devuelve directamente.
        if not isinstance(expr, dict):
            return expr

        # Se obtiene el tipo de la expresión (factor, término, expresión, etc.).
        expr_type = expr.get("type")
        
        # Dependiendo del tipo de expresión, se evalúa de diferentes formas:

        # Si es un valor constante (int o float), se devuelve directamente.
        if expr_type == "factor_cte": # Constante (1, 2.5)
            return expr["value"]
        
        # Si es un identificador (nombre de variable), se busca su valor en el directorio.
        if expr_type == "factor_id": 
            var_name = expr["value"]["value"]
            return self.dir.get_variable_value(var_name)
        
        # Si es una llamada a función, se evalúa la función y se devuelve su valor.
        if expr_type == "factor_expression": 
            return self.evaluate(expr["value"])
        
        # Si es un factor negativo (expresión con signo menos), se evalúa la expresión y se devuelve su valor negativo.
        if expr_type == "factor_minus": 
            return -self.evaluate(expr["value"])
        
        # Si es una expresión simple se evalúa y se devuelve su valor.
        if expr_type in ["term_simple", "exp_simple", "expression_simple"]: # Expresión simple (x + y, x - y) 
            return self.evaluate(expr["value"])
        
        # Si es una expresión compuesta se evalúa cada parte y se aplica la operación correspondiente.
        if expr_type in ["term", "exp"]: 

            items = expr["value"] # Lista de elementos (valores y operadores)
            left = self.evaluate(items[0]) # Almacena el primer valor (izquierda)

            # Itera sobre los elementos de la expresión, evaluando cada operación.
            for i in range(1, len(items), 2):

                op = items[i] # Guarda el operador (suma, resta, etc.)
                right = self.evaluate(items[i + 1]) # Almacena el segundo valor (derecha)
                
                # Valida que los tipos de los operandos sean compatibles para la operación (cubo semántico).
                self.validate_operation(left, right, op)

                # Según el operador, se realiza la operación correspondiente.
                if op == "+": left += right
                elif op == "-": left -= right
                elif op == "*": left *= right
                elif op == "/": left = left // right # División entera (genera un entero si ambos son enteros, y un float si existen floats)

            return left # Devuelve el resultado de la operación
        
        # Si es una expresión lógica (<, >, =!) se evalúa la expresión y se devuelve su valor (0 o 1).
        if expr_type == "expression_greater_than": # >
            left = self.evaluate(expr["value"][0])
            right = self.evaluate(expr["value"][2])
            return int(left > right)
        
        if expr_type == "expression_less_than": # <
            left = self.evaluate(expr["value"][0])
            right = self.evaluate(expr["value"][2])
            return int(left < right)
        
        if expr_type == "expression_not_equal": # !=
            left = self.evaluate(expr["value"][0])
            right = self.evaluate(expr["value"][2])
            return int(left != right)

        raise ValueError(f"No se puede evaluar la expresión: {expr_type}")

    # Método para validar el tipo de una variable y su valor.
    # Verifica que el tipo de la variable coincida con el tipo del valor asignado.
    def validate_type_match(self, var_id, var_type, value):

        # Se obtiene el tipo del valor asignado (int o float).
        if isinstance(value, int):
            value_type = "int"
        elif isinstance(value, float):
            value_type = "float"
        else:
            raise TypeError(f"Tipo no soportado para el valor de '{var_id}'")

        # Se verifica que el tipo de la variable coincida con el tipo del valor.
        if var_type == "int" and value_type != "int":
            raise TypeError(f"No se puede asignar {value_type} a variable int '{var_id}'")
        elif var_type == "float" and value_type not in ("int", "float"):
            raise TypeError(f"No se puede asignar {value_type} a variable float '{var_id}'")
    
    # Función para validar operaciones entre dos operandos.
    # Verifica que los tipos de los operandos sean compatibles según el cubo semántico.
    def validate_operation(self, left_value, right_value, operator):

        # Almacena el tipo de los operandos (int o float).
        left_type = "int" if isinstance(left_value, int) else "float"
        right_type = "int" if isinstance(right_value, int) else "float"

        # Acude al cubo semántico para validar la operación.
        try:
            self.cube.get_result_type(left_type, right_type, operator)
        except TypeError as e:
            raise TypeError(f"Error en operación '{operator}': {e}")

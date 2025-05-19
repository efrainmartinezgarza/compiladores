from semantic_cube import SemanticCube

"""Clase que representa el directorio de funciones y variables del programa.
   Permite agregar funciones, declarar variables, asignar valores y buscar variables en el ámbito actual o global."""

class FunctionDirectory:

    # Lista de palabras reservadas en el lenguaje BabyDuck (ayuda a evitar conflictos de nombres).
    RESERVED_WORDS = {
        "program", "var", "int", "float", "void",
        "main", "if", "else", "while", "do", "print"
    }
    
    # Creación del directorio de funciones y variables
    def __init__(self):

        self.func_dir = {
            "global": {   # Scope global
                "params": [],
                "vars": {}
            }
        }
        self.built_in_functions = {"print": {"params": []}}
        self.current_scope = "global"
        self.cube = SemanticCube()

    # Permite agregar una nueva función al directorio de funciones.
    # Si la función ya existe o es una palabra reservada, lanza un error.
    def add_function(self, func_name, params=None, var_table=None, body=None):

        if func_name in FunctionDirectory.RESERVED_WORDS: # Verifica si la función es una palabra reservada
            raise NameError(f"El nombre '{func_name}' es una palabra reservada.")
        if func_name in self.func_dir: # Verifica si la función ya está declarada
            raise NameError(f"La función '{func_name}' ya está declarada.")
        self.func_dir[func_name] = {
            "params": params or [],
            "vars": var_table or {},
            "body": body
        }

    # Permite definir el ámbito actual (scope) en el que se están declarando variables o funciones
    def set_current_scope(self, scope_name):
        if scope_name not in self.func_dir:
            raise NameError(f"El scope '{scope_name}' no existe.")
        self.current_scope = scope_name

    # Permite recuperar el ámbito actual (scope) en el que se están declarando variables o funciones
    def get_current_vars(self):
        return self.func_dir[self.current_scope]["vars"]

    # Declara una nueva variable dentro del scope actual.
    # Si la variable ya existe o es una palabra reservada, lanza un error.
    def declare_variable(self, var_id, var_type, address):
        if var_id in FunctionDirectory.RESERVED_WORDS: # Verifica si la variable es una palabra reservada
            raise NameError(f"El nombre '{var_id}' es una palabra reservada.")
        current_vars = self.get_current_vars()
        if var_id in current_vars: # Verifica si la variable ya está declarada
            raise NameError(f"La variable '{var_id}' ya está declarada en el scope '{self.current_scope}'.")
        current_vars[var_id] = {
            "type": var_type,
            "assigned": False,
            "address": address
        }

    # Permite asignar un valor a una variable ya declarada.
    def assign_variable_value(self, var_id, value):
        var_info = self.func_dir[self.current_scope]["vars"][var_id]
        var_info.update({
            "assigned": True,
            "value": value,
        })

    # Permite encontrar una variable en el ámbito actual o global.
    # Si la variable no existe, devuelve None.
    def find_variable(self, var_id):
        current_vars = self.get_current_vars()
        if var_id in current_vars:
            return current_vars[var_id]
        elif var_id in self.func_dir["global"]["vars"]:
            return self.func_dir["global"]["vars"][var_id]
        return None

    # Permite recuperar el valor actual de una variable ya asignada.
    def get_variable_value(self, var_id):
        var = self.find_variable(var_id)
        if var is None or not var["assigned"]:
            raise NameError(f"Variable '{var_id}' no tiene valor asignado.")
        return var["value"]

   # Función auxiliar: Imprime el directorio de funciones y variables en un formato legible.
    def print_func_dir(self):
        for scope, info in self.func_dir.items():
            print(f"Scope: {scope}")
            if info["params"]:
                print("  Parámetros:")
                for param in info["params"]:
                    print(f"    {param['id']} : {param['type']}")
            if isinstance(info["vars"], dict):
                print("  Variables:")
                for var_id, var_data in info["vars"].items():
                    if not isinstance(var_data, dict):
                        continue
                    # Mostrar la dirección en lugar del valor
                    address = var_data.get('address', 'Sin dirección asignada')
                    print(f"    {var_id} : {var_data['type']} | Dirección: {address}")
            print()
# quad_generator.py

from semantic_cube import SemanticCube

class QuadGenerator:

    # 
    def __init__(self):
        self.pilaOperandos = []        # Pila de operandos
        self.filaOperadores = []        # Pila de operadores
        self.pilaTipos = []       # Pila de tipos
        self.filaCuadruplos = []   # Fila de cuádruplos
        self.temp_count = 0    # Contador de variables temporales
        self.cube = SemanticCube()  # Acceso al cubo semántico
        self.var_table = {}    # Tabla de símbolos temporal para lookup de tipos

    # Agregar OPERANDO y TIPO en sus respectivas pilas
    def push_operand(self, operand, var_type):
        self.pilaOperandos.append(operand)
        self.pilaTipos.append(var_type)

    # Agregar OPERADOR 
    def push_operator(self, operator):
        self.filaOperadores.append(operator)
    
    # 
    def new_temp(self):
        temp_name = f"t{self.temp_count}"
        self.temp_count += 1
        return temp_name

    # Generación de cuádruplos
    def generate_quad_if_applicable(self):

        # Si el número de operadores es mayor a cero
        if len(self.filaOperadores) > 0:

            # Guardar el primer 
            op = self.filaOperadores[-1]
            if op in ['+', '-', '*', '/', '>', '<', '!=']:
                right = self.pilaOperandos.pop()
                left = self.pilaOperandos.pop()
                right_type = self.pilaTipos.pop()
                left_type = self.pilaTipos.pop()
                operator = self.filaOperadores.pop()

                # Validación con cubo semántico
                result_type = self.cube.get_result_type(left_type, right_type, operator)

                temp = self.new_temp()
                self.filaCuadruplos.append((operator, left, right, temp))
                self.pilaOperandos.append(temp)
                self.pilaTipos.append(result_type)

    def generate_assignment_quad(self, target):
        value = self.pilaOperandos.pop()
        self.pilaTipos.pop()
        self.filaCuadruplos.append(('=', value, '', target))

    def generate_print_quad(self):
        value = self.pilaOperandos.pop()
        self.pilaTipos.pop()
        self.filaCuadruplos.append(('print', '', '', value))

    def print_filaCuadruplos(self):
        print("\nCuádruplos generados:")
        print("---------------------------------")
        for idx, quad in enumerate(self.filaCuadruplos):
            print(f"[{idx}] {quad}")

    def reset(self):
        self.pilaOperandos.clear()
        self.filaOperadores.clear()
        self.pilaTipos.clear()
        self.filaCuadruplos.clear()
        self.temp_count = 0
        self.var_table.clear()

    def register_variable(self, var_id, var_type):
        self.var_table[var_id] = var_type

    def get_var_type(self, var_id):
        return self.var_table.get(var_id, None)

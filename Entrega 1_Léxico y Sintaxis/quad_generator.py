# quad_generator.py

from semantic_cube import SemanticCube
class QuadGenerator:

    debug_mode = True

    def __init__(self, memory_manager, directory):
        self.pilaOperandos = []        # Pila de operandos
        self.pilaOperadores = []        # Pila de operadores
        self.pilaTipos = []       # Pila de tipos
        self.filaCuadruplos = []   # Fila de cuádruplos
        self.temp_count = 1    # Contador de variables temporales
        self.param_count = 1     # Contador de parámetros temporales
        self.cube = SemanticCube()  # Acceso al cubo semántico
        self.jumps_stack = []  # Pila de saltos
        self.memory_manager = memory_manager  # Acceso al gestor de memoria
        self.dir = directory  # Acceso al directorio de funciones y variables

    # Agregar OPERANDO y TIPO en sus respectivas pilas
    def push_operand(self, operand, var_type):
        self.pilaOperandos.append(operand)
        self.pilaTipos.append(var_type)

    # Agregar OPERADOR 
    def push_operator(self, operator):
               
        # Inserción del operador en la pila de operadores
        self.pilaOperadores.append(operator)

    # Generación de etiqueta de temporal (T0, T1, T2)
    def new_temp(self):
        temp_name = f"t{self.temp_count}"
        self.temp_count += 1
        return temp_name

    # Generación de cuádruplos
    def generate_quad_if_applicable(self):

        if len(self.pilaOperadores) > 0:
            
            # Acceso al útimo operador de la pila de operadores
            op = self.pilaOperadores[-1]

            if op in ['+', '-', '*', '/', '>', '<', '!=']:
                right = self.pilaOperandos.pop()
                left = self.pilaOperandos.pop()
                right_type = self.pilaTipos.pop()
                left_type = self.pilaTipos.pop()
                operator = self.pilaOperadores.pop()

                # Validación con cubo semántico
                result_type = self.cube.get_result_type(left_type, right_type, operator)  

                # Creación de la dirección del temporal
                address_temp = self.memory_manager.generate_address(result_type, 'temporal')

                # Aumento del contador de temporales en el scope actual
                self.dir.update_resource(self.dir.current_scope, "temporals", result_type)

                # Transformación del operador a número
                if (self.debug_mode == False):
                    operator = self.transform_operador_to_number(operator)
                
                #temp = self.new_temp()
                
                self.filaCuadruplos.append((operator, left, right, address_temp))
                self.pilaOperandos.append(address_temp)
                self.pilaTipos.append(result_type)                  
                
    def generate_assignment_quad(self, target):
        value = self.pilaOperandos.pop()
        value_type = self.pilaTipos.pop()

        # Validar si el tipo de la variable de destino coincide con el tipo del valor
        target_type = self.get_var_type(target)

        if target_type is None:
            raise ValueError(f"La variable '{target}' no está declarada.")

        # Validación de tipo
        if target_type != value_type:
            raise TypeError(f"No se puede asignar un valor de tipo '{value_type}' a la variable '{target}' de tipo '{target_type}'")

        # Generación del cuádruplo de asignación
        operator = '='

        # Obtención de dirección para la variable que va a recibir el valor
        address = self.memory_manager.get_variable_address(target, self.dir.current_scope, self.dir)
        
        # Transformación del operador a número
        if (self.debug_mode == False):
            operator = self.transform_operador_to_number(operator)

        self.filaCuadruplos.append((operator, value, '', address))

    def generate_print_quad(self):
        value = self.pilaOperandos.pop()
        self.pilaTipos.pop()
        operator = "print"

        # Transformación del operador a número
        if (self.debug_mode == False):
            operator = self.transform_operador_to_number(operator)

        # Generación del cuádruplo de impresión
        self.filaCuadruplos.append((operator, '', '', value))

    def print_filaCuadruplos(self):     
        for i, cuad in enumerate(self.filaCuadruplos):
            op, left, right, res = cuad
            print(f"{i:<3} {op:<10} {left:<10} {right:<10} {res:<10}")

    def reset(self):
        self.pilaOperandos.clear()
        self.pilaOperadores.clear()
        self.pilaTipos.clear()
        self.filaCuadruplos.clear()
        self.temp_count = 0

    def get_var_type(self, var_id):
        var_type = self.dir.find_variable(var_id)
        return var_type["type"] if var_type else None
    
    def generate_go(self, operator):
         # Extrae el último temporal de la pila de operandos (aquello que se evalúa para el salto)

        if(operator == "goTo"):
            condition = ""
        else:
            condition = self.pilaOperandos.pop()

        # Transformación del operador a número
        if (self.debug_mode == False):
            operator = self.transform_operador_to_number(operator)

        # Generación del cuádruplo de salto condicional
        self.filaCuadruplos.append((operator, condition, "", None))

        # Almacena el índice del cuádruplo de salto (para llenarlo después)
        self.jumps_stack.append(len(self.filaCuadruplos) - 1)
    
    def fill_jump(self, jump_index, target=None):
        if target is None:
            target = len(self.filaCuadruplos)
        
        quad = self.filaCuadruplos[jump_index]
        self.filaCuadruplos[jump_index] = (quad[0], quad[1], quad[2], target)

    def generate_ENDFUNC_quad(self):
        operator = "ENDFUNC"

        # Transformación del operador a número
        if (self.debug_mode == False):
            operator = self.transform_operador_to_number(operator)

        # Generación del cuádruplo de fin de función
        self.filaCuadruplos.append((operator, '', '', ''))

    def generate_functionCall_quad(self, quadType, func_name):
        
        if(quadType == "ERA"):
            operator = "ERA"
        elif(quadType == "goSub"):
            operator = "goSub"
            self.param_count = 1 # Se reinicia el contador de parámetros finalizada la llamada a la función

        # Transformación del operador a número
        if (self.debug_mode == False):
            operator = self.transform_operador_to_number(operator)

        # Generación del cuádruplo de ERA
        self.filaCuadruplos.append((operator, func_name, '', ''))

    def new_param(self):
        param_name = f"p{self.param_count}"
        self.param_count += 1
        return param_name

    def generate_param_quad(self):
        
        operator = "param"
        param = self.new_param()  # Genera un nuevo parámetro temporal (p1, p2, p3, ...)

        # Transformación del operador a número
        if (self.debug_mode == False):
            operator = self.transform_operador_to_number(operator)

        # Extrae el último temporal de la pila de operandos (aquello que se evalúa para el parámetro)
        temp = self.pilaOperandos.pop()
        self.pilaTipos.pop()

        # Generación del cuádruplo de parámetro
        self.filaCuadruplos.append((operator, temp, '', param))

    def transform_operador_to_number(self, operator):

        if operator == '+':
            return 1
        elif operator == '-':
            return 2
        elif operator == '*':
            return 3
        elif operator == '/':
            return 4
        elif operator == '>':
            return 5
        elif operator == '<':
            return 6
        elif operator == '=':
            return 7
        elif operator == "!=":
            return 8
        elif operator == "print":
            return 9
        elif operator == "goTo":
            return 10
        elif operator == "goToFalse":
            return 11
        elif operator == "goToTrue":
            return 12
        elif operator == "ERA":
            return 13
        elif operator == "goSub":
            return 14
        elif operator == "param":
            return 15
        elif operator == "ENDFUNC":
            return 16
        elif operator == "goToMain":
            return 17       
        else:
            raise ValueError(f"Operador desconocido: {operator}")



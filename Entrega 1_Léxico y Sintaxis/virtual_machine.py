class VirtualMachine:

    def __init__(self, quadruples, function_directory, constants_table):

        # Contenido recibido por la máquina virtual
        self.quadruples = quadruples                            # Lista de cuádruplos a ejecutar
        self.function_directory = function_directory            # Directorio de funciones y variables
        self.constants_table = constants_table                  # Tabla de constantes
        
        # Variables gloables de la máquina virtual
        self.current_scope = "global"                           # Ámbito actual (scope) de ejecución
        self.instruction_pointer = 0                            # Puntero de instrucción (índice del cuádruplo actual)
        self.call_stack = []                                    # Pila de llamadas (almacena los contextos previos (de los que nos movimos))
        self.pending_local_memory = None                        # Memoria local para una función pendiente de ejecución (espacio reservado)

        # Memoria segmentada por scope y tipo 
        # ----------------------------------------------------------------------------------------------------------------
        
        # Memoria global
        self.memory_global = {
            'int': {},
            'float': {}
        }

        # Memoria para variables temporales
        self.memory_temporal = {
            'int': {},
            'float': {}
        }

        # Memoria para constantes
        self.memory_constant = {
            'int': {},
            'float': {},
            'string': {}
        }

        # Memoria local actual (para la función actual)
        self.current_local_memory = {
            'int': {},
            'float': {},
            'string': {}
        }

        # Inicialización de la memoria global con variables globales
        # Se colocan las direcciones con valores nulos
        if "global" in self.function_directory and "vars" in self.function_directory["global"]:
            for var_name, var_info in self.function_directory["global"]["vars"].items():
                if "address" in var_info:
                    var_type = self.get_type(var_info["address"])
                    self.memory_global[var_type][var_info["address"]] = None

        # Inicialización de la memoria de constantes 
        # Cargar constantes en memoria 
        for (val, const_type), addr in constants_table.items():
            if const_type not in ['int', 'float', 'string']:
                raise ValueError(f"Tipo constante no soportado: {const_type}")
            self.memory_constant[const_type][addr] = val

    # Funciones auxiliares para manejar segmentos y tipos de memoria
    # -------------------------------------------------------------------------------------------------------------

    # Determina el segmento de memoria al que pertenece una dirección dada 
    def get_segment(self, address):
        if 1000 <= address < 3000:
            return "local"
        elif 3000 <= address < 5000:
            return "global"
        elif 5000 <= address < 7000:
            return "temporal"
        elif 7000 <= address < 10000:
            return "constant"
        else:
            raise ValueError(f"Dirección inválida: {address}")

    # Determina el tipo de dato al que pertenece una dirección dada
    def get_type(self, address):
        if 1000 <= address < 2000 or 3000 <= address < 4000 or 5000 <= address < 6000 or 7000 <= address < 8000:
            return "int"
        elif 2000 <= address < 3000 or 4000 <= address < 5000 or 6000 <= address < 7000 or 8000 <= address < 9000:
            return "float"
        elif 9000 <= address < 10000:
            return "string"
        else:
            raise ValueError(f"No se pudo inferir tipo de dirección: {address}")

    # Obtiención del valor almacenado en una dirección dada, considerando su segmento y tipo
    def get_value(self, address):
        if address is None:
            return None
        segment = self.get_segment(address)
        data_type = self.get_type(address)

        if segment == "constant":
            return self.memory_constant[data_type].get(address)
        elif segment == "global":
            return self.memory_global[data_type].get(address)
        elif segment == "local":
            return self.current_local_memory[data_type].get(address)
        elif segment == "temporal":
            return self.memory_temporal[data_type].get(address)
        else:
            raise ValueError(f"Dirección inválida: {address}")

    # Almacenamiento de un valor en una dirección dada, considerando su segmento y tipo
    def set_value(self, address, value):
        if address is None:
            return
        segment = self.get_segment(address)
        data_type = self.get_type(address)

        if segment == "constant":
            raise ValueError(f"No se puede escribir en memoria constante: {address}")
        elif segment == "global":
            self.memory_global[data_type][address] = value
        elif segment == "local":
            self.current_local_memory[data_type][address] = value
        elif segment == "temporal":
            self.memory_temporal[data_type][address] = value
        else:
            raise ValueError(f"Dirección inválida: {address}")
    
    # Conversión de operadores a sus identificadores numéricos
    def operator_to_id(self, operator):
        mapping = {
            '+': 1,
            '-': 2,
            '*': 3,
            '/': 4,
            '>': 5,
            '<': 6,
            '=': 7,
            '!=': 8,
            'print': 9,
            'goTo': 10,
            'goToFalse': 11,
            'goToTrue': 12,
            'ERA': 13,
            'goSub': 14,
            'param': 15,
            'ENDFUNC': 16
        }

        # Si se recibió un número entero, solo se verifica si es un ID válido
        if isinstance(operator, int):
            if operator in mapping.values():
                return operator
            else:
                return None
        # Si se recibió un string, se obtiene su ID equivalente
        elif isinstance(operator, str):
            return mapping.get(operator, None)
        else:
            return None

    # Función principal: Realiza la ejecución de los cuádruplos
    # -------------------------------------------------------------------------------------------------------------

    def run(self):

        # Se ejecutan los cuádruplos hasta que se alcance el final de la lista
        while self.instruction_pointer < len(self.quadruples):

            # Obtención del cuádruplo actual
            quad = self.quadruples[self.instruction_pointer]

            # Descomposición del cuádruplo en sus componentes
            op, left, right, result = quad

            # Validación: ¿Se ha realizado un salto?
            jumped = False

            # Operador del cuádruplo a examinar (convertido a ID numérico)
            op_id = self.operator_to_id(op) 

            # Opciones de ejecución según el ID del operador
            match op_id:

                case 1:  # Suma (+)
                    val = self.get_value(left) + self.get_value(right)
                    self.set_value(result, val)

                case 2:  # Resta (-)
                    val = self.get_value(left) - self.get_value(right)
                    self.set_value(result, val)

                case 3:  # Multiplicación (*)
                    val = self.get_value(left) * self.get_value(right)
                    self.set_value(result, val)

                case 4:  # División (/)
                    
                    # Obtención de los valores de los operandos
                    left_val = self.get_value(left)
                    right_val = self.get_value(right)

                    # Validación: Si el divisor es cero, se lanza un error
                    if right_val == 0:
                        raise ZeroDivisionError("Error: Se intenta hacer una división por cero.")
                    
                    # Obtención de los tipos de los operandos (ayuda a determinar el tipo de división (entera o flotante))
                    left_type = self.get_type(left)
                    right_type = self.get_type(right)

                    # Se realiza división entera o flotante según los tipos de los operandos
                    val = left_val // right_val if left_type == "int" and right_type == "int" else left_val / right_val

                    # Se almacena el resultado en la memoria
                    self.set_value(result, val)

                case 5:  # Mayor que (>)
                    val = int(self.get_value(left) > self.get_value(right)) # Convierte el resultado a entero (1 o 0)
                    self.set_value(result, val)

                case 6:  # Menor que (<)
                    val = int(self.get_value(left) < self.get_value(right)) # Convierte el resultado a entero (1 o 0)
                    self.set_value(result, val)

                case 7:  # Asignación (=)
                    value = self.get_value(left)
                    self.set_value(result, value)

                case 8:  # Diferente de (!=)
                    val = int(self.get_value(left) != self.get_value(right))
                    self.set_value(result, val)

                case 9:  # Imprimir (print)
                    val = self.get_value(result)
                    print(val)

                case 10:  # Salto incondicional (goTo)

                    # Validación: Si el salto está fuera de rango, se lanza un error
                    if not (0 <= result < len(self.quadruples)):
                        raise IndexError(f"Error: IP={result} se encuentra fuera de rango permitido")
                    
                    # Actualización del puntero de instrucción al cuádruplo de destino
                    self.instruction_pointer = result

                    # Se marca que se ha realizado un salto (evita avanzar al siguiente cuádruplo)
                    jumped = True

                case 11:  # Salto condicional falso (goToFalse)

                    # Obtención de la condición a evaluar
                    cond = self.get_value(left)

                    # Si la condición es falsa, se salta al cuádruplo indicado por 'result'
                    if cond is not None and cond == False:

                        # Validación: Si el salto está fuera de rango, se lanza un error
                        if not (0 <= result < (len(self.quadruples) + 1)):
                            raise IndexError(f"Error: IP={result} se encuentra fuera de rango permitido")
                        
                        # Actualización del puntero de instrucción al cuádruplo de destino
                        self.instruction_pointer = result

                        # Se marca que se ha realizado un salto (evita avanzar al siguiente cuádruplo)
                        jumped = True

                case 12:  # Salto condicional verdadero (goToTrue)

                    # Obtención de la condición a evaluar
                    cond = self.get_value(left)

                    # Si la condición es verdadera, se salta al cuádruplo indicado por 'result'
                    if cond is not None and cond == True:
                        if not (0 <= result < len(self.quadruples)):
                            raise IndexError(f"Error: IP={result} se encuentra fuera de rango permitido")
                        self.instruction_pointer = result
                        jumped = True

                case 13:  # ERA: Establece el contexto de la función llamada

                    # Inicialización del contexto de la función (diccionario vacío)
                    self.pending_local_memory = {'int': {}, 'float': {}, 'string': {}}

                    # Obtención del nombre de la función a ejecutar
                    self.current_scope = left

                    # Extracción de los nombres de los parámetros de la función actual (los guarda en una lista ordenada)
                    self.param_names = [param["id"] for param in self.function_directory[self.current_scope]["params"]]

                    # Se inicializa el contador de parámetros
                    self.contador_parametros = 0

                    # Definición de las direcciones base locales para cada tipo de dato
                    local_base_addresses = {'int': 1000, 'float': 2000, 'string': 9000}

                    # Obtiene la cantidad de recursos necesarios para la función actual (variables, parametros y temporales)
                    resources = self.function_directory[self.current_scope].get("resources", {})

                    # Copia de las direcciones base locales para cada tipo de dato 
                    current_address = local_base_addresses.copy()

                    # Función auxiliar para reservar memoria local para los tipos de datos
                    def reservar(tipo, cantidad):
                        for _ in range(cantidad):

                            # Crea una dirección vacía para el tipo de dato especificado
                            self.pending_local_memory[tipo][current_address[tipo]] = None
                            current_address[tipo] += 1

                    # Proceso de reserva de memoria local para los recursos necesarios
                    for scope_name in ["params", "vars", "temporals"]:
                        if scope_name in resources:
                            for tipo, cantidad in resources[scope_name].items():
                                reservar(tipo, cantidad)
                
                case 14:  # goSub: Guarda el contexto actual y salta al inicio de la función

                    # Creación de copia del contexto actual en la pila de llamadas
                    context = {
                        'ip': self.instruction_pointer + 1,  # Posición del siguiente cuádruplo a ejecutar
                        'scope': self.current_scope,         # Ámbito actual
                        'local_memory': {                    # Memoria local actual
                            'int': self.current_local_memory['int'].copy(),
                            'float': self.current_local_memory['float'].copy()
                        }
                    }
                    self.call_stack.append(context) # Almacenamiento del contexto

                    # Traslado a la memoria local pendiente (para la función llamada)
                    self.current_local_memory = self.pending_local_memory

                    # Se vacía la memoria local pendiente para evitar conflictos en futuras llamadas
                    self.pending_local_memory = None

                    # Se localiza el puntero de instrucción al inicio de la función llamada
                    self.instruction_pointer = self.function_directory[left]['start_point']

                    # Se actualiza el ámbito actual al de la función llamada
                    self.current_scope = left

                    # Se registra un salto
                    jumped = True

                case 15:  # param: Asigna un valor a un parámetro de la función actual

                    # Obtención del valor a asignar al parámetro
                    val = self.get_value(left)

                    # Validación: El número de parámetros recibidos no debe exceder el número de parámetros definidos en la función	
                    if self.contador_parametros >= len(self.param_names):
                        raise IndexError(f"Demasiados parámetros enviados a '{self.current_scope}'")
                    
                    # Obtención del nombre del parámetro actual 
                    param_name = self.param_names[self.contador_parametros]

                    # Obtención de la dirección del parámetro en el directorio de funciones
                    param_address = self.function_directory[self.current_scope]["vars"][param_name]["address"]

                    # Obtención del tipo del parámetro (para asignarlo en la memoria local)
                    param_type = self.get_type(param_address)

                    # Se guarda el valor del parámetro en la memoria local pendiente
                    self.pending_local_memory[param_type][param_address] = val

                    # Aumenta el número de parámetros recibidos
                    self.contador_parametros += 1

                case 16:  # Fin de función (ENDFUNC): Restaura el contexto anterior y retorna al punto de llamada

                    # No hay contexto previo para restaurar (Error)
                    if not self.call_stack:
                        raise RuntimeError("Intentando retornar sin haber llamado a ninguna función")
                    
                    # Se restaura el contexto anterior desde la pila de llamadas
                    context = self.call_stack.pop()

                    # Se actualizan los componentes de la máquina virtual con el contexto restaurado
                    self.instruction_pointer = context['ip']
                    self.current_scope = context['scope']
                    self.current_local_memory = context['local_memory'] 
                    jumped = True

                case _: # Operación no reconocida (Error)
                    raise ValueError(f"Operación no reconocida: {op}")

            # Si no se ha realizado un salto, se avanza al siguiente cuádruplo
            if not jumped:
                self.instruction_pointer += 1

    # FuncIión auxiliar: Imprime el estado actual de la memoria y otros componentes de la máquina virtual
    def print_memory_state(vm):

        def print_section(name, mem):
            print(f"\n{name}:")
            for dtype, addr_dict in mem.items():
                print(f"  Tipo {dtype}:")
                if not addr_dict:
                    print("    (vacío)")
                    continue
                for addr, val in sorted(addr_dict.items()):
                    print(f"    Dirección {addr}: {val}")

        print_section("Memoria Global", vm.memory_global)
        print_section("Memoria Local", vm.current_local_memory)
        print_section("Memoria Temporal", vm.memory_temporal)
        print_section("Memoria Constante", vm.memory_constant)

        print(f"\nPila de Llamadas: {vm.call_stack}")
        print(f"Puntero de Instrucción Final: {vm.instruction_pointer}")
        print(f"Pending Local Memory: {vm.pending_local_memory}")
        print("---------------------")
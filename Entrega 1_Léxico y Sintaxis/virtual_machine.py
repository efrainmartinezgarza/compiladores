class VirtualMachine:
    def __init__(self, quadruples, function_directory, constants_table):
        self.quadruples = quadruples
        self.function_directory = function_directory
        self.constants_table = constants_table
        self.current_scope = "global"

        # Memoria segmentada por scope y tipo (solo int y float)
        self.memory_global = {
            'int': {},
            'float': {}
        }
        self.memory_local_stack = []  # para pilas de locales en llamadas

        self.memory_temporal = {
            'int': {},
            'float': {}
        }
        self.memory_constant = {
            'int': {},
            'float': {},
            'string': {}
        }

        # Inicializar memoria global
        if "global" in self.function_directory and "vars" in self.function_directory["global"]:
            for var_name, var_info in self.function_directory["global"]["vars"].items():
                if "address" in var_info:
                    var_type = self.get_type(var_info["address"])
                    self.memory_global[var_type][var_info["address"]] = None

        self.instruction_pointer = 0
        self.call_stack = []
        self.current_local_memory = {
            'int': {},
            'float': {},
            'string': {}
        }

        self.pending_local_memory = None  # Para preparar parámetros antes de goSub

        # Cargar constantes en memoria
        for (val, const_type), addr in constants_table.items():
            if const_type not in ['int', 'float', 'string']:
                raise ValueError(f"Tipo constante no soportado: {const_type}")
            self.memory_constant[const_type][addr] = val

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

    def get_type(self, address):
        if 1000 <= address < 2000 or 3000 <= address < 4000 or 5000 <= address < 6000 or 7000 <= address < 8000:
            return "int"
        elif 2000 <= address < 3000 or 4000 <= address < 5000 or 6000 <= address < 7000 or 8000 <= address < 9000:
            return "float"
        elif 9000 <= address < 10000:
            return "string"
        else:
            raise ValueError(f"No se pudo inferir tipo de dirección: {address}")


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

        # Si es int, lo devolvemos si es válido
        if isinstance(operator, int):
            if operator in mapping.values():
                return operator
            else:
                return None
        # Si es string, buscamos el ID
        elif isinstance(operator, str):
            return mapping.get(operator, None)
        else:
            return None

    def run(self):
        while self.instruction_pointer < len(self.quadruples):
            quad = self.quadruples[self.instruction_pointer]
            op, left, right, result = quad
            jumped = False

            op_id = self.operator_to_id(op) 

            match op_id:
                case 1:  # +
                    val = self.get_value(left) + self.get_value(right)
                    self.set_value(result, val)

                case 2:  # -
                    val = self.get_value(left) - self.get_value(right)
                    self.set_value(result, val)

                case 3:  # *
                    val = self.get_value(left) * self.get_value(right)
                    self.set_value(result, val)

                case 4:  # /
                    divisor = self.get_value(right)
                    if divisor == 0:
                        raise ZeroDivisionError("División por cero")
                    left_val = self.get_value(left)
                    left_type = self.get_type(left)
                    right_type = self.get_type(right)
                    val = left_val // divisor if left_type == "int" and right_type == "int" else left_val / divisor
                    self.set_value(result, val)

                case 5:  # >
                    val = int(self.get_value(left) > self.get_value(right))
                    self.set_value(result, val)

                case 6:  # <
                    val = int(self.get_value(left) < self.get_value(right))
                    self.set_value(result, val)

                case 7:  # =
                    value = self.get_value(left)
                    self.set_value(result, value)

                case 8:  # !=
                    val = int(self.get_value(left) != self.get_value(right))
                    self.set_value(result, val)

                case 9:  # print
                    val = self.get_value(result)
                    print(val)

                case 10:  # goTo
                    if not (0 <= result < len(self.quadruples)):
                        raise IndexError(f"SALTO INVÁLIDO: IP={result} fuera de rango")
                    self.instruction_pointer = result
                    jumped = True

                case 11:  # goToFalse
                    cond = self.get_value(left)
                    if cond is not None and not cond:
                        if not (0 <= result < len(self.quadruples)):
                            raise IndexError(f"SALTO INVÁLIDO: IP={result} fuera de rango")
                        self.instruction_pointer = result
                        jumped = True

                case 12:  # goToTrue
                    cond = self.get_value(left)
                    if cond is not None and cond:
                        if not (0 <= result < len(self.quadruples)):
                            raise IndexError(f"SALTO INVÁLIDO: IP={result} fuera de rango")
                        self.instruction_pointer = result
                        jumped = True

                case 13:  # ERA
                    self.pending_local_memory = {'int': {}, 'float': {}, 'string': {}}
                    self.current_scope = left
                    self.param_names = [param["id"] for param in self.function_directory[self.current_scope]["params"]]
                    self.contador_parametros = 0
                    local_base_addresses = {'int': 1000, 'float': 2000, 'string': 9000}
                    resources = self.function_directory[self.current_scope].get("resources", {})
                    current_address = local_base_addresses.copy()

                    def reservar(tipo, cantidad):
                        for _ in range(cantidad):
                            self.pending_local_memory[tipo][current_address[tipo]] = None
                            current_address[tipo] += 1

                    for scope_name in ["params", "vars", "temporals"]:
                        if scope_name in resources:
                            for tipo, cantidad in resources[scope_name].items():
                                reservar(tipo, cantidad)
                
                case 14:  # goSub
                    context = {
                        'ip': self.instruction_pointer + 1,
                        'scope': self.current_scope,
                        'local_memory': {
                            'int': self.current_local_memory['int'].copy(),
                            'float': self.current_local_memory['float'].copy()
                        }
                    }
                    self.call_stack.append(context)
                    self.current_local_memory = self.pending_local_memory
                    self.pending_local_memory = None
                    self.instruction_pointer = self.function_directory[left]['start_point']
                    self.current_scope = left
                    jumped = True

                case 15:  # param
                    val = self.get_value(left)
                    if self.contador_parametros >= len(self.param_names):
                        raise IndexError(f"Demasiados parámetros enviados a '{self.current_scope}'")
                    param_name = self.param_names[self.contador_parametros]
                    param_address = self.function_directory[self.current_scope]["vars"][param_name]["address"]
                    param_type = self.get_type(param_address)
                    self.pending_local_memory[param_type][param_address] = val
                    self.contador_parametros += 1

                case 16:  # ENDFUNC
                    if not self.call_stack:
                        raise RuntimeError("Intentando retornar sin haber llamado a ninguna función")
                    context = self.call_stack.pop()
                    self.instruction_pointer = context['ip']
                    self.current_scope = context['scope']
                    self.current_local_memory = context['local_memory']
                    jumped = True

                case _:
                    print(f"[DEBUG] Operación no reconocida: {op}")

            if not jumped:
                self.instruction_pointer += 1


    # Impresión final de estado
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


class VirtualMachine:
    def __init__(self, quadruples, function_directory, constants_table):
        self.quadruples = quadruples
        self.function_directory = function_directory
        self.constants_table = constants_table
        self.current_scope = "global"

        # Memoria segmentada
        self.memory_global = {}
        self.memory_local_stack = []
        self.memory_temporal = {}
        self.memory_constant = {}

        # Inicializar memoria global
        if "global" in self.function_directory and "vars" in self.function_directory["global"]:
            for var_name, var_info in self.function_directory["global"]["vars"].items():
                if "address" in var_info:
                    self.memory_global[var_info["address"]] = None

        self.instruction_pointer = 0
        self.call_stack = []
        self.current_local_memory = {}

        self.pending_local_memory = None  # Para preparar parámetros antes de goSub

        # Cargar constantes en memoria
        for (val, const_type), addr in constants_table.items():
            self.memory_constant[addr] = val

    def get_segment(self, address):
        addr = address  # Ya no usamos tuplas

        if 1000 <= addr < 3000:
            return "local"
        elif 3000 <= addr < 5000:
            return "global"
        elif 5000 <= addr < 7000:
            return "temporal"
        elif 7000 <= addr < 10000:
            return "constant"
        else:
            raise ValueError(f"Dirección inválida: {addr}")

    def get_type(self, address):
        addr = address

        if 1000 <= addr < 2000 or 3000 <= addr < 4000 or 5000 <= addr < 6000 or 7000 <= addr < 8000:
            return "int"
        elif 2000 <= addr < 3000 or 4000 <= addr < 5000 or 6000 <= addr < 7000 or 8000 <= addr < 9000:
            return "float"
        elif 9000 <= addr < 10000:
            return "string"
        else:
            raise ValueError(f"No se pudo inferir tipo de dirección: {addr}")

    def get_value(self, address):
        if address is None:
            return None
        segment = self.get_segment(address)
        if segment == "constant":
            return self.memory_constant.get(address)
        elif segment == "global":
            return self.memory_global.get(address)
        elif segment == "local":
            return self.current_local_memory.get(address)
        elif segment == "temporal":
            return self.memory_temporal.get(address)
        else:
            raise ValueError(f"Dirección inválida: {address}")

    def set_value(self, address, value):
        if address is None:
            return
        segment = self.get_segment(address)
        if segment == "constant":
            raise ValueError(f"No se puede escribir en memoria constante: {address}")
        elif segment == "global":
            self.memory_global[address] = value
        elif segment == "local":
            self.current_local_memory[address] = value
        elif segment == "temporal":
            self.memory_temporal[address] = value
        else:
            raise ValueError(f"Dirección inválida: {address}")

    def run(self):
        while self.instruction_pointer < len(self.quadruples):
            quad = self.quadruples[self.instruction_pointer]
            op, left, right, result = quad
            jumped = False

            try:
                if op in {"=", "+", "-", "*", "/", "<", ">", "print"}:
                    if op != "print" and (left is None or (right is None and op != "=")):
                        raise ValueError(f"Se está usando una variable no inicializada: {left} o {right}")

                if op == "=":
                    value = self.get_value(left)
                    self.set_value(result, value)

                elif op == "+":
                    val = self.get_value(left) + self.get_value(right)
                    self.set_value(result, val)

                elif op == "-":
                    val = self.get_value(left) - self.get_value(right)
                    self.set_value(result, val)

                elif op == "*":
                    val = self.get_value(left) * self.get_value(right)
                    self.set_value(result, val)

                elif op == "/":
                    divisor = self.get_value(right)
                    if divisor == 0:
                        raise ZeroDivisionError("División por cero")
                    left_val = self.get_value(left)
                    left_type = self.get_type(left)
                    right_type = self.get_type(right)
                    val = left_val // divisor if left_type == "int" and right_type == "int" else left_val / divisor
                    self.set_value(result, val)

                elif op == "<":
                    val = self.get_value(left) < self.get_value(right)
                    self.set_value(result, val)

                elif op == ">":
                    val = self.get_value(left) > self.get_value(right)
                    self.set_value(result, val)

                elif op == "print":
                    val = self.get_value(result)
                    print(val)

                elif op == "goTo":
                    if not (0 <= result < len(self.quadruples)):
                        raise IndexError(f"SALTO INVÁLIDO: IP={result} fuera de rango")
                    self.instruction_pointer = result
                    jumped = True

                elif op == "goToFalse":
                    cond = self.get_value(left)
                    if cond is not None and not cond:
                        if not (0 <= result < len(self.quadruples)):
                            raise IndexError(f"SALTO INVÁLIDO: IP={result} fuera de rango")
                        self.instruction_pointer = result
                        jumped = True

                elif op == "goToTrue":
                    cond = self.get_value(left)
                    if cond is not None and cond:
                        if not (0 <= result < len(self.quadruples)):
                            raise IndexError(f"SALTO INVÁLIDO: IP={result} fuera de rango")
                        self.instruction_pointer = result
                        jumped = True

                elif op == "ERA":
                    self.pending_local_memory = {}
                    self.current_scope = left
                    self.param_names = [
                        param["id"]
                        for param in self.function_directory[self.current_scope]["params"]
                    ]
                    self.contador_parametros = 0

                elif op == "param":
                    val = self.get_value(left)
                    if self.contador_parametros >= len(self.param_names):
                        raise IndexError(f"Demasiados parámetros enviados a '{self.current_scope}'")

                    param_name = self.param_names[self.contador_parametros]
                    param_address = self.function_directory[self.current_scope]["vars"][param_name]["address"]

                    self.pending_local_memory[param_address] = val
                    self.contador_parametros += 1

                elif op == "goSub":
                    context = {
                        'ip': self.instruction_pointer + 1,
                        'scope': self.current_scope,
                        'local_memory': self.current_local_memory.copy()
                    }
                    self.call_stack.append(context)

                    self.current_local_memory = self.pending_local_memory
                    self.pending_local_memory = None

                    self.instruction_pointer = self.function_directory[left]['start_point']
                    self.current_scope = left
                    jumped = True

                elif op == "ENDFUNC":
                    if not self.call_stack:
                        raise RuntimeError("Intentando retornar sin haber llamado a ninguna función")
                    context = self.call_stack.pop()
                    self.instruction_pointer = context['ip']
                    self.current_scope = context['scope']
                    self.current_local_memory = context['local_memory']
                    jumped = True

                else:
                    print(f"[DEBUG] Operación no reconocida: {op}")

            except Exception as e:
                print(f"[ERROR] Ejecutando cuádruplo {self.instruction_pointer}: {quad}")
                print(e)
                break

            if not jumped:
                self.instruction_pointer += 1

        # Impresión final de estado
        print("\n--- MEMORIA FINAL ---")
        print(f"Memoria Global: {self.memory_global}")
        print(f"Memoria Local: {self.current_local_memory}")
        print(f"Memoria Temporal: {self.memory_temporal}")
        print(f"Memoria Constante: {self.memory_constant}")
        print(f"Pila de Llamadas: {self.call_stack}")
        print(f"Puntero de Instrucción Final: {self.instruction_pointer}")
        print("---------------------")
class MemoryManager:

    def __init__(self):

        # Límites por tipo y segmento (ahora inician desde 1000)
        self.memory_limits = {
            'global': {
                'int': (1000, 1999),
                'float': (2000, 2999),
            },
            'local': {
                'int': (4000, 4999),
                'float': (5000, 5999),
            },
            'temporal': {
                'int': (7000, 7999),
                'float': (8000, 8999),
                'bool': (9000, 9999)
            },
            'constant': {
                'int': (10000, 10999),
                'float': (11000, 11999),
                'string': (12000, 12999)
            }
        }

        # Contadores actuales por tipo y segmento
        self.pointers = {seg: {t: lim[0] for t, lim in types.items()}
                        for seg, types in self.memory_limits.items()}

        # Tabla de constantes
        self.constants_table = {}

    def get_next_address(self, var_type, memory_segment='global'):
        """
        Asigna la siguiente dirección disponible en el segmento dado.
        """
        limit_low, limit_high = self.memory_limits[memory_segment][var_type]
        current = self.pointers[memory_segment][var_type]

        if current > limit_high:
            raise MemoryError(f"Segmento de memoria {memory_segment} {var_type} lleno")

        address = current
        self.pointers[memory_segment][var_type] += 1
        return address

    def add_constant(self, value, const_type):
        """
        Añade una constante a la tabla si no existe y devuelve su dirección.
        """
        key = (value, const_type)
        if key in self.constants_table:
            return self.constants_table[key]

        address = self.get_next_address(const_type, 'constant')
        self.constants_table[key] = address
        return address

    def get_constant_address(self, value, const_type):
        """
        Devuelve la dirección de una constante ya registrada.
        """
        key = (value, const_type)
        return self.constants_table.get(key)

    def reset_local_pointers(self):
        """
        Reinicia los contadores de memoria local para una nueva función.
        """
        for t in ['int', 'float', 'bool']:
            self.pointers['local'][t] = self.memory_limits['local'][t][0]

    def reset_temporal_pointers(self):
        """
        Reinicia los contadores de memoria temporal para una nueva ejecución.
        """
        for t in ['int', 'float', 'bool']:
            self.pointers['temporal'][t] = self.memory_limits['temporal'][t][0]

    def generate_temporal(self, var_type):
        """
        Genera una variable temporal de tipo dado.
        """
        return self.get_next_address(var_type, 'temporal')

    def assign_variable_address(self, var_type, scope):
        """
        Asigna una dirección a una variable global o local.
        """
        address = self.get_next_address(var_type, scope)
        return address
    
    def get_var_address(self, var_id, scope, dir_func):
        # Buscar en el ámbito actual
        func_info = dir_func.func_dir.get(scope, {})
        vars_dict = func_info.get("vars", {})

        var_info = vars_dict.get(var_id)
        if var_info and "address" in var_info:
            return var_info["address"]
        
        # Si no se encontró, intenta buscar en 'global'
        if scope != "global":
            global_vars = dir_func.func_dir.get("global", {}).get("vars", {})
            var_info_global = global_vars.get(var_id)
            if var_info_global and "address" in var_info_global:
                return var_info_global["address"]

        return None
    
    def print_constants_table(self):
        """
        Imprime la tabla de constantes.
        """
        for (value, const_type), address in self.constants_table.items():
            print(f"Valor: {value:<10} | Tipo: {const_type:<10} | Dirección: {address:<10}")

    def get_var_info(self, var_id, scope, dir_func):
        func_info = dir_func.func_dir.get(scope, {})
        vars_dict = func_info.get("vars", {})

        var_info = vars_dict.get(var_id)
        if var_info and "type" in var_info:
            return var_info

        # Busca en global si no está en el scope actual
        if scope != "global":
            global_info = dir_func.func_dir.get("global", {}).get("vars", {})
            var_info_global = global_info.get(var_id)
            if var_info_global and "type" in var_info_global:
                return var_info_global

        return None
    
    # Impresión de la tabla de memoria
    def print_memory(self):
        
        for segment, types in self.memory_limits.items():
            print(segment.upper())
            for var_type, (low, high) in types.items():
                print(f"{var_type.upper()} -> Rango: {low} - {high} | Dirección actual: {self.pointers[segment][var_type]}")
            print("-----------------------------------------------------------")

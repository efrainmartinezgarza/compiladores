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

    # Asignación de la siguiente dirección disponible (en el segmento actual)
    def generate_address(self, var_type, memory_segment='global'):
        limit_low, limit_high = self.memory_limits[memory_segment][var_type]
        current = self.pointers[memory_segment][var_type]

        if current > limit_high:
            raise MemoryError(f"Segmento de memoria {memory_segment} {var_type} lleno")

        address = current
        self.pointers[memory_segment][var_type] += 1
        return address

    # Agregar una constante a la tabla de constantes y crear su dirección
    def add_constant(self, value, const_type):

        # Si la constante ya está registrada, devuelve su dirección
        key = (value, const_type)
        if key in self.constants_table:
            return self.constants_table[key]
        
        # Si no está registrada, se crea una nueva dirección
        # Creación de la dirección para la constante
        address = self.generate_address(const_type, 'constant')

        # Almacenamiento de la dirección en la tabla de constantes (como clave-valor)
        self.constants_table[key] = address
        return address

    # Búsqueda de la dirección de una constante ya registrada en la "tabla de constantes"
    def get_constant_address(self, value, const_type):
        key = (value, const_type)
        return self.constants_table.get(key) # Devuelve la dirección si existe, o None si no está registrada
    
    # Obtención de la dirección de una variable dada su ID y su ámbito 
    # (se busca en el directorio de funciones y variables)
    def get_variable_address(self, var_id, scope, dir_func):
        
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
    
    # Impresión de la tabla de constantes
    def print_constants_table(self):
        """
        Imprime la tabla de constantes.
        """
        for (value, const_type), address in self.constants_table.items():
            print(f"Valor: {value:<10} | Tipo: {const_type:<10} | Dirección: {address:<10}")

     # Impresión de la tabla de memoria
    def print_memory(self):
        
        for segment, types in self.memory_limits.items():
            print(segment.upper())
            for var_type, (low, high) in types.items():
                print(f"{var_type.upper()} -> Rango: {low} - {high} | Dirección actual: {self.pointers[segment][var_type]}")
            print("-----------------------------------------------------------")

    
   
class SemanticCube:
    def __init__(self):

        # Tipos de datos soportados en el lenguaje BabyDuck
        INT = "int"
        FLOAT = "float"

        # Tabla de operaciones definidas para cada tipo de dato. 
        self.operations = {
            "+": {

                INT: {
                    INT: INT,         # int + int = int
                    FLOAT: FLOAT},    # int + float = float
                
                FLOAT: {
                    INT: FLOAT,       # float + int = float
                    FLOAT: FLOAT}     # float + float = float
            },
            "-": {
                INT: {
                    INT: INT,         # int - int = int
                    FLOAT: FLOAT},    # int - float = float
                    
                FLOAT: {
                    INT: FLOAT,       # float - int = float
                    FLOAT: FLOAT}     # float - float = float
            },
            "*": {
                INT: {
                    INT: INT,         # int * int = int
                    FLOAT: FLOAT},    # int * float = float

                FLOAT: {
                    INT: FLOAT,       # float * int = float
                    FLOAT: FLOAT}     # float * float = float
            },
            "/": {
                INT: {
                    INT: FLOAT,       # int / int = int
                    FLOAT: FLOAT},    # int / float = float
                
                FLOAT: {
                    INT: FLOAT,       # float / int = float
                    FLOAT: FLOAT}     # float / float = float
            },
            ">": {
                INT: {
                    INT: INT,         # int > int = int (booleano) 
                    FLOAT: INT},      # int > float = int (booleano)

                FLOAT: {
                    INT: INT,         # float > int = int (booleano)
                    FLOAT: INT}       # float > float = int (booleano)
            },
            "<": {
                INT: {
                    INT: INT,         # int < int = int (booleano)
                    FLOAT: INT},      # int < float = int (booleano)

                FLOAT: {
                    INT: INT,         # float < int = int (booleano)
                    FLOAT: INT}       # float < float = int (booleano)
            },
            "!=": {
                INT: {
                    INT: INT,         # int != int = int (booleano) 
                    FLOAT: INT},      # int != float = int (booleano)

                FLOAT: {
                    INT: INT,         # float != int = int (booleano)
                    FLOAT: INT}       # float != float = int (booleano)
            }
        }

    # def_result_type: Devuelve el tipo resultante de aplicar una operación entre dos operandos.
    def get_result_type(self, left_type, right_type, operator):
        try:
            return self.operations[operator][left_type][right_type]
        except KeyError:
            raise TypeError(f"Operación no permitida: {left_type} {operator} {right_type}")

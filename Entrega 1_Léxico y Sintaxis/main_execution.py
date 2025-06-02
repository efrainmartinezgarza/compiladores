# Importación de librerías
# Comando para instalar Lark: pip install lark-parser
from lark import Lark, Tree # Clase principal para crear el parser.
from pathlib import Path # Librería para manejar rutas de archivos con rutas relativas y absolutas.
from transformer import MyTransformer # Importación de la clase MyTransformer desde el archivo transformer.py.
from directory import Directory # Importación de la clase Directory desde el archivo directory.py.
from virtual_machine import VirtualMachine # Importación de la clase VirtualMachine desde el archivo vm.py.

def tree_to_dict(tree):
    if isinstance(tree, Tree):
        return {
            "type": tree.data,
            "children": [tree_to_dict(child) for child in tree.children]
        }
    elif hasattr(tree, 'value'):
        return tree.value
    else:
        return str(tree)

# Obtención del directorio donde está "main.py".
MAIN_PATH = Path(__file__).parent

# Uso de rutas relativas para acceder a archivos externos.
GRAMMAR_PATH = MAIN_PATH / "grammar.lark"
TEST_PROGRAM_PATH = MAIN_PATH / "Pruebas/test_13.txt"

# load_grammar_parser: Función para abrir y procesar el archivo de gramática del lenguaje BabyDuck.
def load_grammar_parser():
    with open(GRAMMAR_PATH, "r") as grammar_file:
        grammar = grammar_file.read()
    return Lark(grammar, start="start", parser="earley") # Lark(Contenido de la gramática, nombre del nodo inicial y el tipo de parser a utilizar).

# Proceso de lectura del archivo que contiene el código fuente a analizar.
with open(TEST_PROGRAM_PATH, "r") as test_file: # La "r" se usa para especificar que el archivo se abrirá en modo lectura ("read").
    test_code = test_file.read() # Lectura y almacenamiento del contenido del archivo en una variable.

# Creación del parser: Se hace un llamado a la función load_parser() que contiene la gramática.
# Aquí tambien se crea el lexer (al mismo tiempo que el parser).
parser = load_grammar_parser()

# Conversión de la entrada de texto a un árbol sintáctico.
tree = parser.parse(test_code)

# Uso del lexer para descomponer el código fuente en tokens.
tokens = parser.lex(test_code)

# Transformación del árbol sintáctico a formato diccionario.
transformer = MyTransformer()
result = transformer.transform(tree)


# Sección 2: Directorio de funciones y variables, cuádruplos y memoria.
# ----------------------------------------------------------------------------------------------------------------------------------

checker = Directory() # Creación de un objeto de la clase Directory para manejar el directorio de funciones y variables.
checker.set_program_ast(result) # Establecimiento del AST del programa en el objeto "checker".
checker.analyze() # Análisis del AST del programa (llenado del directorio de funciones y variables).


quadruples = checker.quad_gen.filaCuadruplos # Obtención de los cuádruplos generados.
function_directory = checker.function_dir.func_dir # Obtención del directorio de funciones y variables.
constant_table = checker.memory_manager.constants_table # Obtención de la tabla de constantes.

# Máquina virtual
vm = VirtualMachine(quadruples, function_directory, constant_table)
vm.run()


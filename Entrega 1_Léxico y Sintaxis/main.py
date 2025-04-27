from lark import Lark
from pathlib import Path 

# Obtención del directorio donde está "main.py".
CURRENT_DIR = Path(__file__).parent

# Uso de rutas relativas para acceder a archivos externos.
GRAMMAR_PATH = CURRENT_DIR / "grammar.lark"
TEST_PROGRAM_PATH = CURRENT_DIR / "test_program.txt"

# load_parser: Función para abrir y procesar el archivo de gramática del lenguaje BabyDuck.
def load_parser():
    with open(GRAMMAR_PATH, "r") as file:
        grammar = file.read()
    return Lark(grammar, start="start", parser="earley") 

# Proceso de lectura del archivo que contiene el código fuente a analizar.
with open(TEST_PROGRAM_PATH, "r") as f:
    source_code = f.read() 

# Creación del parser
parser = load_parser()

# Conversión de la entrada de texto a un árbol sintáctico.
tree = parser.parse(source_code)

# Uso del lexer para descomponer el código fuente en tokens.
tokens = parser.lex(source_code)

# Impresión de la entrada de texto original.
print("\nEntrada original:")
print("---------------------------------")
print(source_code)

# Impresión de los tokens encontrados.
print("\nTokens encontrados:")
print("------------------------------")
print("\nToken            |   Carácter")
print("------------------------------")
for token in tokens:
    if hasattr(token, 'type'): 
        print(f"{token.type:<16} | {repr(token.value):<10}") 
                                                             
# Impresión del árbol sintáctico generado.
print("\nÁrbol sintáctico:")
print("---------------------------------")
print(tree.pretty()) 
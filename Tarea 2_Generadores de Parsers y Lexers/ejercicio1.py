
"""------------------------------------------------------------------------------------------------------------------------------
Tarea 2: Ejericio con Lark (Python)
Efraín Martínez Garza (A01280601)
------------------------------------------------------------------------------------------------------------------------------
Descripción: Desarrollo de un parser para evaluar expresiones aritméticas simples (suma y resta) utilizando la librería Lark.
------------------------------------------------------------------------------------------------------------------------------"""

# Importación de librerías
# Comando de instalación: pip install lark-parser
from lark import Lark

# Definición del léxico y la gramática
grammar = """
    start: operacion
    operacion: numero ((suma | resta) numero)*
    numero: DIGITO+
    DIGITO: /[0-9]/
    suma: "+"
    resta: "-"
    %import common.WS // Importación de reglas para espacios en blanco
    %ignore WS  // Comando para ignorar espacios en blanco
"""

# Creación del parser
parser = Lark(grammar, start='start', lexer='standard')

# Expresión a evaluar
expresionIngresada = "1 + 2 - 3 + 5"

# Aplicación del parser a la expresión (conversión a árbol sintáctico)
arbol = parser.parse(expresionIngresada)

# Impresión de la expresión original
print("\nExpresión original:")
print("---------------------------------")
print(expresionIngresada)

# Impresión del árbol sintáctico generado
print("\nÁrbol sintáctico:")
print("---------------------------------")
print(arbol.pretty())

# Obtención e impresión de los tokens encontrados
tokens = parser.lex(expresionIngresada)  
print("Tokens encontrados:")
print("---------------------------------")
for token in tokens:
    print(f"{token.type}: {token.value}")

print("\n")
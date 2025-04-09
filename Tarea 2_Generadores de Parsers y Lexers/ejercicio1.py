
"""------------------------------------------------------------------------------------------------------------------------------
Tarea 2: Ejericio con Lark (Python)
Efraín Martínez Garza (A01280601)
------------------------------------------------------------------------------------------------------------------------------
Descripción: Creación de un parser para evaluar expresiones aritméticas simples (suma y resta) utilizando la librería Lark.
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
parser = Lark(grammar, start='start')

# Expresión a evaluar
expression = "5 + 8 - 1 + 1"

# Aplicación del parser a la expresión (conversión a árbol sintáctico)
arbol = parser.parse(expression)

# Impresión del árbol sintáctico generado
print(arbol.pretty())

import os
from io import StringIO
import sys
from lark import Token, Tree

# Asegúrate de importar lo necesario desde main.py
from main import parser, MyTransformer, Directory

# Rutas del proyecto
MAIN_PATH = os.path.dirname(os.path.abspath(__file__))
TEST_FOLDER = os.path.join(MAIN_PATH, "Pruebas")
RESULT_FOLDER = os.path.join(MAIN_PATH, "Resultados")

# Crear carpeta de resultados si no existe
os.makedirs(RESULT_FOLDER, exist_ok=True)

def tree_to_dict(tree):
    """Recursivamente convierte un árbol Lark a un diccionario"""
    if isinstance(tree, Tree):
        return {
            "type": tree.data,
            "children": [tree_to_dict(child) for child in tree.children]
        }
    elif hasattr(tree, 'value'):
        return {"type": tree.type, "value": tree.value} if isinstance(tree, Token) else tree.value
    else:
        return str(tree)

def analyze_file(file_path):
    file_name = os.path.basename(file_path)
    print(f"\nAnalizando: {file_name}")

    try:
        with open(file_path, 'r') as f:
            test_code = f.read()

        # Fase 1: Lexer - Obtener tokens
        tokens = list(parser.lex(test_code))  # Obtiene los tokens reconocidos

        # Fase 2: Parser - Árbol sintáctico
        tree = parser.parse(test_code)
        ast_tree = tree_to_dict(tree)

        # Fase 3: Transformer - AST transformado
        transformer = MyTransformer()
        result = transformer.transform(tree)

        # Fase 4: Semantic Analyzer - Directorio, Cuádruplos, Memoria
        checker = Directory()
        checker.set_program_ast(result)
        checker.analyze()  # Esto llama a SemanticAnalyzer.analyze()

        status = "EXITOSO"
        error_msg = ""

    except Exception as e:
        status = "ERROR DETECTADO"
        error_msg = str(e)
        tokens = None
        tree = None
        result = None
        checker = None

    # Capturar salida para guardarla en archivo
    output_capture = StringIO()
    sys.stdout = output_capture

    try:
        print("📝 Tokens encontrados:")
        print("------------------------------")
        print("Token            |   Carácter")
        print("------------------------------")
        if tokens:
            for token in tokens:
                if hasattr(token, 'type'):
                    print(f"{token.type:<16} | {repr(token.value):<10}")

        print("\n\nÁrbol sintáctico (raw):")
        print("------------------------------")
        if tree:
            print(tree.pretty())

        print("\n\nÁrbol transformado (AST):")
        print("------------------------------")
        if result:
            print(result)

        if checker and status == "EXITOSO":
            print("\n\nDirectorio de funciones y variables:")
            print("------------------------------")
            checker.function_dir.print_func_dir()

            print("\n\nCuádruplos generados:")
            print("------------------------------")
            checker.quad_gen.print_filaCuadruplos()

            print("\n\nTabla de constantes:")
            print("------------------------------")
            checker.memory_manager.print_constants_table()

            print("\n\nUso de memoria:")
            print("------------------------------")
            checker.memory_manager.print_memory()

    finally:
        sys.stdout = sys.__stdout__  # Restaura stdout

    full_output = output_capture.getvalue()

    # Guardar en archivo
    output_file = os.path.join(RESULT_FOLDER, f"resultado_{file_name}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"[RESULTADO] {status}\n")
        f.write("-" * 50 + "\n\n")
        if status == "ERROR DETECTADO":
            f.write("Mensaje de error:\n")
            f.write(f"{error_msg}\n")
        else:
            f.write(full_output)

    print(f"[{status}] {file_name}")

# Ejecutar todas las pruebas
for file_name in os.listdir(TEST_FOLDER):
    if file_name.endswith(".txt"):
        file_path = os.path.join(TEST_FOLDER, file_name)
        analyze_file(file_path)

print(f"\nPruebas completadas. Resultados guardados en: {RESULT_FOLDER}")
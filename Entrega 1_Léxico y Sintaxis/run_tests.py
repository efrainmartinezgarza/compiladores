import os
from io import StringIO
import sys
from lark import Token, Tree

# Asegúrate de importar lo necesario desde main.py
from main_debug import parser, MyTransformer, Directory
from virtual_machine import VirtualMachine # Added import

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
    output_capture = StringIO() # Creación de un buffer para capturar la salida
    sys.stdout = output_capture # Redireccionamiento al buffer

    # Primero, imprimir el código original al buffer de captura
    print("Código original:")
    print("------------------------------")
    print(test_code) # test_code ya contiene el código del archivo leído
    print("\n" + "-" * 50 + "\n") # Separador

    try:
        print("Tokens encontrados:")
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

            # Ejecutar con Máquina Virtual
            print("\n\nSalida de la Máquina Virtual:")
            print("------------------------------")
            try:
                quadruples = checker.quad_gen.filaCuadruplos
                function_directory = checker.function_dir.func_dir
                constant_table = checker.memory_manager.constants_table

                if quadruples is not None and function_directory is not None and constant_table is not None:
                    vm = VirtualMachine(quadruples, function_directory, constant_table)
                    vm.run()  # VM's print output will go to output_capture
                else:
                    print("No se pudo ejecutar la VM: faltan componentes (cuádruplos, dir. funciones o tabla de constantes).")

            except Exception as vm_e:
                print(f"ERROR durante la ejecución de la Máquina Virtual: {vm_e}")

    finally:
        sys.stdout = sys.__stdout__  # Restaura stdout

    full_output = output_capture.getvalue()

    # Guardar en archivo
    output_file = os.path.join(RESULT_FOLDER, f"resultado_{file_name}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"[RESULTADO] {status}\n")
        f.write("-" * 50 + "\n\n")
        if status == "ERROR DETECTADO":
            f.write("Código original:\n") # También incluir el código original en caso de error
            f.write("------------------------------\n")
            f.write(test_code + "\n\n")
            f.write("Mensaje de error:\n")
            f.write(f"{error_msg}\n")
        else:
            f.write(full_output)

    # print(f"[{status}] {file_name}") # Removed individual status print
    return status, file_name # Added return

# Ejecutar todas las pruebas
failed_files = []
all_successful = True

for file_name_iter in os.listdir(TEST_FOLDER): # Renamed file_name to file_name_iter to avoid conflict
    if file_name_iter.endswith(".txt"):
        file_path = os.path.join(TEST_FOLDER, file_name_iter)
        status, f_name = analyze_file(file_path) # Capture returned status and filename
        if status == "ERROR DETECTADO":
            all_successful = False
            failed_files.append(f_name)

# Impresión de resultados finales

print("\n\nRESULTADOS DE LAS PRUEBAS")
print("---------------------------------------------------------------------------------")

if all_successful:
    print("Todos los resultados fueron exitosos.")
else:
    print("\nExistieron errores en los siguientes archivos:")
    for f_name in failed_files:
        print(f"  - {f_name}")

print(f"Las pruebas fueron completadas y los resultados guardados.")

print("---------------------------------------------------------------------------------\n")

from function_directory import FunctionDirectory
from expression_evaluator import ExpressionEvaluator
from semantic_analyzer import SemanticAnalyzer
from quad_generator import QuadGenerator
from executor import Executor
from memory_manager import MemoryManager

class Directory:
    def __init__(self):
        self.function_dir = FunctionDirectory()
        self.evaluator = ExpressionEvaluator(self.function_dir)
        self.memory_manager = MemoryManager()
        self.quad_gen = QuadGenerator(self.memory_manager, self.function_dir)
        self.analyzer = SemanticAnalyzer(self.function_dir, self.evaluator, self.quad_gen, self.memory_manager)
        self.executor = Executor(self.function_dir, self.evaluator)
        self.program_ast = None

    def set_program_ast(self, ast):
        self.program_ast = ast

    def analyze(self):
        if not self.program_ast:
            raise ValueError("No hay AST cargado.")
        self.analyzer.analyze(self.program_ast)
        print("Análisis semántico completado correctamente.")

    def execute(self):
        if not self.program_ast:
            raise RuntimeError("No hay AST cargado para ejecutar.")
        self.executor.execute_program(self.program_ast)

    def print_func_dir(self):
        self.function_dir.print_func_dir()
    
    def print_quadruples(self):
        self.quad_gen.print_filaCuadruplos()



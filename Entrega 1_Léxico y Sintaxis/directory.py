from function_directory import FunctionDirectory
from semantic_analyzer import SemanticAnalyzer
from quad_generator import QuadGenerator
from memory_manager import MemoryManager

class Directory:
    def __init__(self):
        self.function_dir = FunctionDirectory()
        self.memory_manager = MemoryManager()
        self.quad_gen = QuadGenerator(self.memory_manager, self.function_dir)
        self.analyzer = SemanticAnalyzer(self.function_dir, self.quad_gen, self.memory_manager)
        self.program_ast = None

    def set_program_ast(self, ast):
        self.program_ast = ast

    def analyze(self):
        if not self.program_ast:
            raise ValueError("No hay AST cargado.")
        self.analyzer.analyze(self.program_ast)





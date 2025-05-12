class Executor:
    def __init__(self, directory, evaluator):
        self.dir = directory
        self.eval = evaluator
        self._analysis_passed = False

    def execute_program(self, program_ast):
        program_type = program_ast.get("type")
        if program_type not in ["program_simple", "program_vars", "program_funcs", "program_vars_funcs"]:
            raise ValueError(f"Tipo de programa desconocido: {program_type}")

        self.dir.set_current_scope("global")
        body = program_ast.get("body")
        print("Iniciando ejecución del cuerpo principal...")
        self.execute_body(body)

    def execute_body(self, body_node):
        if body_node is None:
            return
        if body_node.get("type") == "body_statement":
            for stmt in body_node.get("value", []):
                self.execute_statement(stmt)

    def execute_statement(self, stmt_node):
        stmt_type = stmt_node.get("type")
        if stmt_type == "statement":
            self.execute_statement(stmt_node["value"])
        elif stmt_type == "assign":
            self.execute_assign(stmt_node)
        elif stmt_type in ["print_expression", "print_string", "print_multiple_expressions"]:
            self.execute_print(stmt_node)
        elif "f_call" in stmt_type:
            self.execute_function_call(stmt_node)
        elif "condition" in stmt_type:
            self.execute_condition(stmt_node)
        elif stmt_type == "cycle":
            self.execute_cycle(stmt_node)

    def execute_assign(self, assign_node):
        var_id = assign_node["id"]["value"]
        expr_node = assign_node["value"]
        value = self.eval.evaluate(expr_node)
        self.dir.assign_variable_value(var_id, value)

    def execute_print(self, print_node):
        expr_list = []
        if print_node["type"] == "print_expression":
            expr_list.append(print_node["value"])
        elif print_node["type"] == "print_multiple_expressions":
            expr_list.extend(print_node["value"])
        elif print_node["type"] == "print_string":
            print(print_node["value"]["value"])
            return
        output = [str(self.eval.evaluate(expr)) for expr in expr_list]
        print(", ".join(output))

    def execute_function_call(self, call_node):
        if call_node.get("type") == "f_call_simple":
            func_name = call_node["value"]["value"]
            args = []
        elif call_node.get("type") == "f_call_one_expression":
            func_name = call_node["function"]["value"]
            args = [call_node["value"]]
        elif call_node.get("type") == "f_call_multiple_expressions":
            func_name = call_node["function"]["value"]
            args = call_node.get("value", [])

        if func_name in self.dir.built_in_functions:
            return

        expected_params = self.dir.func_dir[func_name]["params"]
        self.dir.set_current_scope(func_name)

        for i, param in enumerate(expected_params):
            var_id = param["id"]
            value = self.eval.evaluate(args[i])
            self.dir.assign_variable_value(var_id, value)

        self.execute_body(self.dir.func_dir[func_name]["body"])
        self.dir.set_current_scope("global")

    def execute_condition(self, cond_node):
        condition = self.eval.evaluate(cond_node.get("condition"))
        if condition:
            if "body" in cond_node:
                self.execute_body(cond_node["body"])
            elif "body1" in cond_node:
                self.execute_body(cond_node["body1"])
        else:
            if "body2" in cond_node:
                self.execute_body(cond_node["body2"])
            elif "else_block" in cond_node:
                self.execute_body(cond_node["else_block"])

    def execute_cycle(self, cycle_node):
        while self.eval.evaluate(cycle_node["condition"]):
            self.execute_body(cycle_node["body"])

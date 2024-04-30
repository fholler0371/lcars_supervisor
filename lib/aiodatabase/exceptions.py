class FunctionNotFoundException(Exception):
     def __init__(self, func_name, message="function not found: "):
        self.func_name = func_name
        self.message = message
        super().__init__(f"{message}{func_name}")

import ast
import re

class TypeAgnosticNormalizer:
    def __init__(self):
        self.var_counter = 0
        self.func_counter = 0
        self.class_counter = 0
        self.arg_counter = 0
        self.local_counter = 0
        self.var_map = {}
        self.func_map = {}
        self.class_map = {}
        self.arg_map = {}
        self.local_map = {}
        self.current_function_args = set()

    def reset(self):
        self.var_counter = 0
        self.func_counter = 0
        self.class_counter = 0
        self.arg_counter = 0
        self.local_counter = 0
        self.var_map = {}
        self.func_map = {}
        self.class_map = {}
        self.arg_map = {}
        self.local_map = {}
        self.current_function_args = set()

    def normalize(self, code: str, language: str = "Python") -> str:
        self.reset()
        try:
            tree = ast.parse(code)
            transformer = EnhancedIdentifierTransformer(self)
            transformed_tree = transformer.visit(tree)
            ast.fix_missing_locations(transformed_tree)
            return ast.unparse(transformed_tree)
        except Exception:
            return self._regex_normalize(code)

    def _regex_normalize(self, code: str) -> str:
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        code = re.sub(r'"[^"]*"', '""', code)
        code = re.sub(r"'[^']*'", "''", code)
        identifiers = set(re.findall(r'\b([a-zA-Z_]\w*)\b', code))
        python_keywords = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield', 'print', 'range', 'len', 'int',
            'str', 'float', 'list', 'dict', 'set', 'tuple', 'bool', 'type'
        }
        for i, ident in enumerate(sorted(identifiers, key=len, reverse=True)):
            if ident not in python_keywords and not ident.startswith('__'):
                placeholder = f'VAR_{i}'
                code = re.sub(r'\b' + ident + r'\b', placeholder, code)
        return code


class EnhancedIdentifierTransformer(ast.NodeTransformer):
    def __init__(self, normalizer):
        self.norm = normalizer
        self.in_function = False
        super().__init__()

    def visit_FunctionDef(self, node):
        old_in_function = self.in_function
        self.in_function = True
        old_args = self.norm.current_function_args.copy()
        
        self.norm.current_function_args = set()
        for arg in node.args.args:
            arg_name = arg.arg
            if arg_name not in self.norm.arg_map:
                self.norm.arg_map[arg_name] = f'ARG_{self.norm.arg_counter}'
                self.norm.arg_counter += 1
            self.norm.current_function_args.add(arg_name)
        
        if node.name not in self.norm.func_map:
            self.norm.func_map[node.name] = f'FUNC_{self.norm.func_counter}'
            self.norm.func_counter += 1
        node.name = self.norm.func_map[node.name]
        
        self.generic_visit(node)
        
        self.norm.current_function_args = old_args
        self.in_function = old_in_function
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            var_name = node.id
            
            if var_name in self.norm.current_function_args:
                node.id = self.norm.arg_map.get(var_name, f'ARG_{var_name}')
            elif self.in_function and isinstance(node.ctx, ast.Store):
                if var_name not in self.norm.local_map:
                    self.norm.local_map[var_name] = f'LOCAL_{self.norm.local_counter}'
                    self.norm.local_counter += 1
                node.id = self.norm.local_map[var_name]
            elif var_name not in self.norm.var_map:
                self.norm.var_map[var_name] = f'VAR_{self.norm.var_counter}'
                self.norm.var_counter += 1
                node.id = self.norm.var_map[var_name]
            else:
                node.id = self.norm.var_map.get(var_name, f'VAR_{var_name}')
        return node

    def visit_ClassDef(self, node):
        if node.name not in self.norm.class_map:
            self.norm.class_map[node.name] = f'CLASS_{self.norm.class_counter}'
            self.norm.class_counter += 1
        node.name = self.norm.class_map[node.name]
        self.generic_visit(node)
        return node


type_normalizer = TypeAgnosticNormalizer() 

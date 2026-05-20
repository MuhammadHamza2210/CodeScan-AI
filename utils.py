import re
import ast
import difflib
import hashlib
import sys
import io
import dis

def normalize_code(code: str, language: str = "Python") -> str:
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
    code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
    code = re.sub(r'"[^"]*"', '"STR"', code)
    code = re.sub(r"'[^']*'", "'STR'", code)
    code = re.sub(r'\b\d+\.?\d*\b', 'NUM', code)
    code = re.sub(r'\s+', ' ', code).strip()
    return code.lower()


def get_tokens(code: str) -> list:
    return re.findall(r'[a-zA-Z_]\w*|[+\-*/=<>!&|%^~]+|[(){}\[\];:,.]', code)


def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def ngram_similarity(tokens_a: list, tokens_b: list, n: int = 4) -> float:
    def ngrams(lst, n):
        return set(tuple(lst[i:i + n]) for i in range(len(lst) - n + 1))
    return jaccard_similarity(ngrams(tokens_a, n), ngrams(tokens_b, n))


def sequence_similarity(code_a: str, code_b: str) -> float:
    return difflib.SequenceMatcher(None, code_a, code_b).ratio()


def ast_similarity(code_a: str, code_b: str) -> float:
    def get_node_seq(code):
        try:
            tree = ast.parse(code)
            return [type(node).__name__ for node in ast.walk(tree)]
        except Exception:
            return []
    seq_a = get_node_seq(code_a)
    seq_b = get_node_seq(code_b)
    if not seq_a or not seq_b:
        return 0.0
    return jaccard_similarity(set(seq_a), set(seq_b))


def bytecode_similarity(code_a: str, code_b: str) -> float:
    def get_instructions(code):
        try:
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            compiled = compile(code, '<string>', 'exec')
            dis.dis(compiled)
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            return [p for p in output.split() if p.isupper() and len(p) > 2]
        except Exception:
            return []
    instr_a = get_instructions(code_a)
    instr_b = get_instructions(code_b)
    if not instr_a or not instr_b:
        return 0.0
    return jaccard_similarity(set(instr_a), set(instr_b)) * 100


def big_o_similarity(code_a: str, code_b: str) -> float:
    def get_complexity(code):
        try:
            tree = ast.parse(code)
            loops = 0
            max_depth = 0
            current_depth = 0
            has_recursion = False
            func_names = set()
            call_names = set()

            class ComplexityVisitor(ast.NodeVisitor):
                def visit_FunctionDef(self, node):
                    func_names.add(node.name)
                    self.generic_visit(node)

                def visit_Call(self, node):
                    if isinstance(node.func, ast.Name):
                        call_names.add(node.func.id)
                    self.generic_visit(node)

                def visit_For(self, node):
                    nonlocal loops, current_depth, max_depth
                    loops += 1
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)
                    self.generic_visit(node)
                    current_depth -= 1

                def visit_While(self, node):
                    nonlocal loops, current_depth, max_depth
                    loops += 1
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)
                    self.generic_visit(node)
                    current_depth -= 1

            visitor = ComplexityVisitor()
            visitor.visit(tree)
            has_recursion = bool(func_names & call_names)

            if has_recursion:
                return 'O(2ⁿ)' if max_depth > 2 else 'O(n)'
            elif max_depth >= 3:
                return 'O(n³)'
            elif max_depth == 2:
                return 'O(n²)'
            elif loops >= 2:
                return 'O(n²)'
            elif loops == 1:
                return 'O(n)'
            return 'O(1)'
        except Exception:
            return 'Unknown'

    return 100.0 if get_complexity(code_a) == get_complexity(code_b) else 0.0


def compute_fingerprint(code: str) -> str:
    return hashlib.md5(normalize_code(code).encode()).hexdigest()


def get_diff_lines(code_a: str, code_b: str) -> list:
    return list(difflib.unified_diff(
        code_a.splitlines(), code_b.splitlines(), lineterm='', n=2
    )) 

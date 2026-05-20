import ast
from collections import Counter
from typing import Dict

class ControlFlowGraph:
    @staticmethod
    def build_cfg(code: str) -> Dict:
        try:
            tree = ast.parse(code)
            cfg = {
                'nodes': [],
                'edges': [],
                'branch_count': 0,
                'loop_count': 0,
                'try_count': 0,
                'except_count': 0,
                'call_count': 0,
                'entry_point': None,
                'exit_points': [],
            }

            class CFGBuilder(ast.NodeVisitor):
                def __init__(self, cfg):
                    self.cfg = cfg
                    self.current_node = 0
                    self.cfg['entry_point'] = self.current_node

                def add_node(self, node_type, label=""):
                    self.cfg['nodes'].append({
                        'id': self.current_node,
                        'type': node_type,
                        'label': label or node_type,
                    })
                    node_id = self.current_node
                    self.current_node += 1
                    return node_id

                def add_edge(self, from_node, to_node, edge_type="flow"):
                    self.cfg['edges'].append({
                        'from': from_node,
                        'to': to_node,
                        'type': edge_type,
                    })

                def visit_If(self, node):
                    self.cfg['branch_count'] += 1
                    cond_node = self.add_node('IF', 'Condition')
                    body_node = self.add_node('BLOCK', 'If-Body')
                    self.add_edge(cond_node, body_node, 'true')
                    if node.orelse:
                        else_node = self.add_node('BLOCK', 'Else-Body')
                        self.add_edge(cond_node, else_node, 'false')
                    end_node = self.add_node('MERGE', 'End-If')
                    self.add_edge(body_node, end_node)
                    if node.orelse:
                        self.add_edge(else_node, end_node)
                    self.generic_visit(node)
                    return end_node

                def visit_For(self, node):
                    self.cfg['loop_count'] += 1
                    loop_node = self.add_node('FOR', 'Loop')
                    body_node = self.add_node('BLOCK', 'Loop-Body')
                    self.add_edge(loop_node, body_node, 'enter')
                    self.add_edge(body_node, loop_node, 'back-edge')
                    exit_node = self.add_node('EXIT_LOOP', 'Exit')
                    self.add_edge(loop_node, exit_node, 'exit')
                    self.generic_visit(node)
                    return exit_node

                def visit_While(self, node):
                    self.cfg['loop_count'] += 1
                    loop_node = self.add_node('WHILE', 'Loop')
                    body_node = self.add_node('BLOCK', 'Loop-Body')
                    self.add_edge(loop_node, body_node, 'enter')
                    self.add_edge(body_node, loop_node, 'back-edge')
                    exit_node = self.add_node('EXIT_LOOP', 'Exit')
                    self.add_edge(loop_node, exit_node, 'exit')
                    self.generic_visit(node)
                    return exit_node

                def visit_Try(self, node):
                    self.cfg['try_count'] += 1
                    try_node = self.add_node('TRY', 'Try-Block')
                    self.generic_visit(node)
                    for handler in node.handlers:
                        self.cfg['except_count'] += 1
                        except_node = self.add_node('EXCEPT', 'Except-Block')
                        self.add_edge(try_node, except_node, 'exception')
                        if handler.body:
                            self.generic_visit(handler)
                    if node.finalbody:
                        finally_node = self.add_node('FINALLY', 'Finally-Block')
                        self.add_edge(try_node, finally_node, 'finally')
                        self.generic_visit_finally(node.finalbody)
                    return try_node
                
                def visit_TryStar(self, node):
                    return self.visit_Try(node)

                def visit_Call(self, node):
                    self.cfg['call_count'] += 1
                    call_node = self.add_node('CALL', f'Call to {self._get_func_name(node.func)}')
                    self.generic_visit(node)
                    return call_node

                def _get_func_name(self, func_node):
                    if isinstance(func_node, ast.Name):
                        return func_node.id
                    elif isinstance(func_node, ast.Attribute):
                        return func_node.attr
                    return 'function'

                def generic_visit_finally(self, body):
                    for node in body:
                        self.visit(node)

            builder = CFGBuilder(cfg)
            builder.visit(tree)
            return cfg
        except Exception:
            return {'nodes': [], 'edges': [], 'branch_count': 0, 'loop_count': 0, 'try_count': 0, 'except_count': 0, 'call_count': 0}

    @staticmethod
    def compare_cfgs(cfg_a: Dict, cfg_b: Dict) -> float:
        if not cfg_a['nodes'] or not cfg_b['nodes']:
            return 0.0
        score = 0.0
        
        max_branches = max(cfg_a['branch_count'], cfg_b['branch_count'], 1)
        branch_sim = 1.0 - abs(cfg_a['branch_count'] - cfg_b['branch_count']) / max_branches
        score += branch_sim * 20
        
        max_loops = max(cfg_a['loop_count'], cfg_b['loop_count'], 1)
        loop_sim = 1.0 - abs(cfg_a['loop_count'] - cfg_b['loop_count']) / max_loops
        score += loop_sim * 20
        
        max_try = max(cfg_a.get('try_count', 0), cfg_b.get('try_count', 0), 1)
        try_sim = 1.0 - abs(cfg_a.get('try_count', 0) - cfg_b.get('try_count', 0)) / max_try
        score += try_sim * 15
        
        max_calls = max(cfg_a.get('call_count', 0), cfg_b.get('call_count', 0), 1)
        call_sim = 1.0 - abs(cfg_a.get('call_count', 0) - cfg_b.get('call_count', 0)) / max_calls
        score += call_sim * 15
        
        types_a = Counter(n['type'] for n in cfg_a['nodes'])
        types_b = Counter(n['type'] for n in cfg_b['nodes'])
        all_types = set(types_a.keys()) | set(types_b.keys())
        if all_types:
            intersection = sum(min(types_a.get(t, 0), types_b.get(t, 0)) for t in all_types)
            union = sum(max(types_a.get(t, 0), types_b.get(t, 0)) for t in all_types)
            type_sim = intersection / union if union > 0 else 0
            score += type_sim * 30
        
        return min(score, 100.0)


cfg_engine = ControlFlowGraph() 

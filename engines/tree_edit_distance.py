import ast
from typing import Optional
from config import HAS_ZSS

if HAS_ZSS:
    from zss import simple_distance, Node as ZSSNode

class TreeEditDistance:
    @staticmethod
    def ast_to_zss_node(ast_node):
        if not HAS_ZSS:
            return None
        zss_node = ZSSNode(type(ast_node).__name__)
        for child in ast.iter_child_nodes(ast_node):
            child_node = TreeEditDistance.ast_to_zss_node(child)
            if child_node:
                zss_node.addkid(child_node)
        return zss_node

    @staticmethod
    def count_ast_nodes(tree):
        try:
            return len(list(ast.walk(tree)))
        except Exception:
            return 1

    @staticmethod
    def compute_ted(code_a: str, code_b: str) -> Optional[float]:
        if not HAS_ZSS:
            return None
        try:
            tree_a = ast.parse(code_a)
            tree_b = ast.parse(code_b)
            zss_a = TreeEditDistance.ast_to_zss_node(tree_a)
            zss_b = TreeEditDistance.ast_to_zss_node(tree_b)
            if zss_a and zss_b:
                edit_distance = simple_distance(zss_a, zss_b)
                nodes_a = len(list(ast.walk(tree_a)))
                nodes_b = len(list(ast.walk(tree_b)))
                max_nodes = max(nodes_a, nodes_b, 1)
                similarity = max(0.0, 100.0 - ((edit_distance / max_nodes) * 100))
                return similarity
        except Exception as e:
            import streamlit as st
            st.sidebar.error(f"TED Error: {str(e)[:50]}")
        return None


ted_engine = TreeEditDistance() 

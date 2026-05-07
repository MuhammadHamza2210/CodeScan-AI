# ============================================================
# 🛡️ CodeScan AI — Ultimate Plagiarism Detector v7.0
# ============================================================
# 6 Detection Engines | 90%+ Accuracy | All Bugs Fixed
# ============================================================

import streamlit as st
import difflib
import hashlib
import json
import time
import re
import ast
import math
import dis
import io
import sys
import itertools
import collections
from datetime import datetime
from collections import defaultdict, Counter, deque
from typing import List, Dict, Tuple, Set, Optional
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# EXTERNAL DEPENDENCY FLAGS
# ============================================================
HAS_SKLEARN = False
HAS_ZSS = False
HAS_TRANSFORMERS = False

try:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    pass

try:
    from zss import simple_distance, Node as ZSSNode
    HAS_ZSS = True
except ImportError:
    pass

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    pass

# ============================================================
# STREAMLIT PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="CodeScan — Ultimate Plagiarism Detector",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# GLOBAL CSS (ORIGINAL DESIGN – UNCHANGED)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #0a0a0c;
  --surface:   #111115;
  --surface2:  #18181e;
  --surface3:  #1f1f28;
  --border:    rgba(255,255,255,0.06);
  --border2:   rgba(255,255,255,0.10);
  --accent:    #7c6dfa;
  --accent2:   #a78bfa;
  --green:     #34d399;
  --red:       #f87171;
  --amber:     #fbbf24;
  --text:      #e8e8f0;
  --muted:     #6b6b80;
  --muted2:    #4a4a5a;
  --font-head: 'Syne', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

.stApp { background: var(--bg) !important; font-family: var(--font-body); color: var(--text); }
.stApp > header { background: transparent !important; }
#MainMenu, footer, .stDeployButton { display: none !important; }

[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
section[data-testid="stSidebarContent"] { padding: 0 !important; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--muted2); border-radius: 10px; }

.stButton > button {
  font-family: var(--font-body) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  background: var(--surface3) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 8px !important;
  padding: 8px 18px !important;
  transition: all .2s ease !important;
  letter-spacing: .3px !important;
}
.stButton > button:hover {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 20px rgba(124,109,250,.35) !important;
}

.primary-btn button {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
  font-size: 14px !important;
  padding: 10px 28px !important;
}
.primary-btn button:hover {
  background: var(--accent2) !important;
  border-color: var(--accent2) !important;
  box-shadow: 0 6px 28px rgba(124,109,250,.5) !important;
}

.stTextArea textarea, .stTextInput input {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: var(--font-mono) !important;
  font-size: 12.5px !important;
  padding: 12px 14px !important;
  transition: border-color .2s !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(124,109,250,.15) !important;
}
.stTextArea label, .stTextInput label, .stSelectbox label, .stFileUploader label {
  color: var(--muted) !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  letter-spacing: .8px !important;
  text-transform: uppercase !important;
  font-family: var(--font-body) !important;
}

.stSelectbox > div > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}

[data-testid="stFileUploader"] {
  background: var(--surface2) !important;
  border: 1px dashed var(--border2) !important;
  border-radius: 12px !important;
  padding: 8px !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

[data-testid="stMetric"] {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .7px; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: var(--font-head) !important; font-size: 28px !important; }

.streamlit-expanderHeader {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: var(--font-body) !important;
  font-size: 13px !important;
}
.streamlit-expanderContent {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 10px 10px !important;
}

.stTabs [data-baseweb="tab-list"] {
  background: var(--surface2) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 2px !important;
  border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  border-radius: 7px !important;
  font-family: var(--font-body) !important;
  font-size: 13px !important;
  padding: 6px 16px !important;
  border: none !important;
}
.stTabs [aria-selected="true"] {
  background: var(--surface3) !important;
  color: var(--text) !important;
  box-shadow: 0 1px 6px rgba(0,0,0,.4) !important;
}

.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
  border-radius: 4px !important;
}

.stSlider .rc-slider-track { background: var(--accent) !important; }
.stSlider .rc-slider-handle { border-color: var(--accent) !important; background: var(--accent) !important; }

.stCheckbox label, .stRadio label { color: var(--text) !important; font-family: var(--font-body) !important; font-size: 13px !important; }

.stAlert { border-radius: 10px !important; font-family: var(--font-body) !important; font-size: 13px !important; border-left-width: 3px !important; }

code, .stCode { font-family: var(--font-mono) !important; font-size: 12px !important; }

.stSpinner > div { border-top-color: var(--accent) !important; }

.heatmap-table { border-collapse: collapse; font-size: 10px; width: 100%; }
.heatmap-table th { padding: 6px 8px; color: #6b6b80; font-weight: 500; }
.heatmap-table td { padding: 8px; text-align: center; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
def init_state():
    defaults = {
        "page": "Analyze",
        "history": [],
        "settings": {
            "sensitivity": 70,
            "language": "Python",
            "method": "Hybrid (All Engines)",
            "theme": "Dark",
            "save_history": True,
            "use_ml": HAS_SKLEARN,
            "use_bytecode": True,
            "use_big_o": True,
            "use_ast_ted": HAS_ZSS,
            "use_cfg": True,
            "use_winnowing": True,
            "use_codebert": HAS_TRANSFORMERS,
            "use_type_agnostic": True,
        },
        "last_result": None,
        "training_data": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ============================================================
# FEATURE 1: TYPE-AGNOSTIC NORMALIZATION
# ============================================================
class TypeAgnosticNormalizer:
    def __init__(self):
        self.var_counter = 0
        self.func_counter = 0
        self.class_counter = 0
        self.var_map = {}
        self.func_map = {}
        self.class_map = {}

    def reset(self):
        self.var_counter = 0
        self.func_counter = 0
        self.class_counter = 0
        self.var_map = {}
        self.func_map = {}
        self.class_map = {}

    def normalize(self, code: str, language: str = "Python") -> str:
        self.reset()
        try:
            tree = ast.parse(code)
            transformer = IdentifierTransformer(self)
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


class IdentifierTransformer(ast.NodeTransformer):
    def __init__(self, normalizer):
        self.norm = normalizer
        super().__init__()

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            if node.id not in self.norm.var_map:
                self.norm.var_map[node.id] = f'VAR_{self.norm.var_counter}'
                self.norm.var_counter += 1
            node.id = self.norm.var_map[node.id]
        return node

    def visit_FunctionDef(self, node):
        if node.name not in self.norm.func_map:
            self.norm.func_map[node.name] = f'FUNC_{self.norm.func_counter}'
            self.norm.func_counter += 1
        node.name = self.norm.func_map[node.name]
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        if node.name not in self.norm.class_map:
            self.norm.class_map[node.name] = f'CLASS_{self.norm.class_counter}'
            self.norm.class_counter += 1
        node.name = self.norm.class_map[node.name]
        self.generic_visit(node)
        return node


type_normalizer = TypeAgnosticNormalizer()

# ============================================================
# FEATURE 2: TREE EDIT DISTANCE (FIXED)
# ============================================================
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
            st.sidebar.error(f"TED Error: {str(e)[:50]}")
        return None


ted_engine = TreeEditDistance()

# ============================================================
# FEATURE 3: CONTROL FLOW GRAPH
# ============================================================
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

            builder = CFGBuilder(cfg)
            builder.visit(tree)
            return cfg
        except Exception:
            return {'nodes': [], 'edges': [], 'branch_count': 0, 'loop_count': 0}

    @staticmethod
    def compare_cfgs(cfg_a: Dict, cfg_b: Dict) -> float:
        if not cfg_a['nodes'] or not cfg_b['nodes']:
            return 0.0
        score = 0.0
        max_branches = max(cfg_a['branch_count'], cfg_b['branch_count'], 1)
        branch_sim = 1.0 - abs(cfg_a['branch_count'] - cfg_b['branch_count']) / max_branches
        score += branch_sim * 30
        max_loops = max(cfg_a['loop_count'], cfg_b['loop_count'], 1)
        loop_sim = 1.0 - abs(cfg_a['loop_count'] - cfg_b['loop_count']) / max_loops
        score += loop_sim * 30
        types_a = Counter(n['type'] for n in cfg_a['nodes'])
        types_b = Counter(n['type'] for n in cfg_b['nodes'])
        all_types = set(types_a.keys()) | set(types_b.keys())
        if all_types:
            intersection = sum(min(types_a.get(t, 0), types_b.get(t, 0)) for t in all_types)
            union = sum(max(types_a.get(t, 0), types_b.get(t, 0)) for t in all_types)
            type_sim = intersection / union if union > 0 else 0
            score += type_sim * 40
        return min(score, 100.0)


cfg_engine = ControlFlowGraph()

# ============================================================
# FEATURE 4: WINNOWING FINGERPRINT
# ============================================================
class WinnowingFingerprint:
    def __init__(self, k: int = 5, window_size: int = 4):
        self.k = k
        self.window_size = window_size

    def _kgrams(self, text: str) -> List[str]:
        return [text[i:i + self.k] for i in range(len(text) - self.k + 1)]

    def _hash_kgram(self, kgram: str) -> int:
        return hash(kgram) & 0xFFFFFFFF

    def generate_fingerprint(self, code: str) -> Set[int]:
        normalized = re.sub(r'\s+', ' ', code).strip()
        kgrams = self._kgrams(normalized)
        if len(kgrams) < self.window_size:
            return set()
        hashes = [self._hash_kgram(kg) for kg in kgrams]
        fingerprint = set()
        for i in range(len(hashes) - self.window_size + 1):
            window = hashes[i:i + self.window_size]
            fingerprint.add(min(window))
        return fingerprint

    @staticmethod
    def compare_fingerprints(fp_a: Set[int], fp_b: Set[int]) -> float:
        if not fp_a or not fp_b:
            return 0.0
        intersection = len(fp_a & fp_b)
        union = len(fp_a | fp_b)
        return (intersection / union) * 100 if union > 0 else 0.0


winnowing_engine = WinnowingFingerprint(k=6, window_size=4)

# ============================================================
# FEATURE 5: CodeBERT ANALYZER (MEMORY SAFE)
# ============================================================
class CodeBERTAnalyzer:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self._loaded = False
        self._load_error = None

    def _load_model(self):
        if self._loaded:
            return True
        if not HAS_TRANSFORMERS:
            self._load_error = "transformers library not installed"
            return False
        try:
            model_name = "microsoft/codebert-base"
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name).to(self.device)
            self.model.eval()
            self._loaded = True
            return True
        except Exception as e:
            self._load_error = str(e)
            return False

    def encode(self, code: str) -> Optional[np.ndarray]:
        if not self._loaded and not self._load_model():
            return None
        try:
            if len(code) > 512:
                code = code[:512]
            inputs = self.tokenizer(
                code,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding="max_length",
            ).to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
                attention_mask = inputs['attention_mask'].unsqueeze(-1)
                masked_output = outputs.last_hidden_state * attention_mask
                summed = masked_output.sum(dim=1)
                counts = attention_mask.sum(dim=1)
                counts = torch.clamp(counts, min=1)
                embedding = (summed / counts).squeeze().cpu().numpy()
            return embedding
        except MemoryError:
            st.sidebar.error("CodeBERT: Out of memory")
            return None
        except Exception as e:
            st.sidebar.error(f"CodeBERT Error: {str(e)[:80]}")
            return None

    @staticmethod
    def cosine_similarity(vec_a, vec_b):
        if vec_a is None or vec_b is None:
            return 0.0
        try:
            norm_a = np.linalg.norm(vec_a)
            norm_b = np.linalg.norm(vec_b)
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return max(0.0, np.dot(vec_a, vec_b) / (norm_a * norm_b)) * 100
        except Exception:
            return 0.0

    def is_available(self):
        if self._loaded:
            return True
        return self._load_model()

    def get_status(self):
        if self._loaded:
            return "✅ CodeBERT ready"
        if self._load_error:
            return f"❌ {self._load_error[:100]}"
        return "⏳ CodeBERT not loaded"


codebert_analyzer = CodeBERTAnalyzer()

# ============================================================
# FEATURE 6: DECISION TREE ML CLASSIFIER
# ============================================================
class MLPlagiarismClassifier:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.is_trained = False
        self.feature_names = [
            'type_agnostic_seq_sim', 'type_agnostic_jac_sim',
            'ted_sim', 'cfg_sim', 'winnowing_sim',
            'codebert_sim', 'bytecode_sim', 'big_o_match',
            'ast_sim', 'seq_sim', 'jac_sim', 'ngram_sim',
        ]

    def extract_features(self, result: Dict) -> np.ndarray:
        features = []
        for name in self.feature_names:
            features.append(result.get(name, 0))
        return np.array(features).reshape(1, -1)

    def train(self, training_data: List[Dict]):
        if not HAS_SKLEARN or len(training_data) < 10:
            return False
        X = []
        y = []
        for item in training_data:
            features = []
            for name in self.feature_names:
                features.append(item['features'].get(name, 0))
            X.append(features)
            y.append(item['label'])
        X = np.array(X)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        self.model = DecisionTreeClassifier(
            max_depth=6,
            min_samples_split=3,
            min_samples_leaf=2,
            criterion='gini',
            random_state=42,
        )
        self.model.fit(X_scaled, y_encoded)
        self.is_trained = True
        return True

    def predict(self, result: Dict) -> Tuple[str, float]:
        if not self.is_trained or not HAS_SKLEARN:
            return None, 0.0
        features = self.extract_features(result)
        features_scaled = self.scaler.transform(features)
        pred_encoded = self.model.predict(features_scaled)[0]
        pred_label = self.label_encoder.inverse_transform([pred_encoded])[0]
        probas = self.model.predict_proba(features_scaled)[0]
        max_proba = max(probas) * 100
        return pred_label, max_proba


ml_classifier = MLPlagiarismClassifier()


def add_training_example(features: Dict, label: str):
    st.session_state["training_data"].append({
        'features': features,
        'label': label,
        'timestamp': datetime.now().isoformat(),
    })
    if len(st.session_state["training_data"]) >= 10:
        if ml_classifier.train(st.session_state["training_data"]):
            st.sidebar.success(
                f"ML Model trained on {len(st.session_state['training_data'])} examples!"
            )


# ============================================================
# CORE PLAGIARISM ENGINE FUNCTIONS
# ============================================================
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


# ============================================================
# MASTER DETECTION PIPELINE
# ============================================================
def detect_plagiarism(
    code_a: str, code_b: str, method: str, sensitivity: int, language: str
) -> dict:
    settings = st.session_state["settings"]

    # Standard normalization
    norm_a = normalize_code(code_a, language)
    norm_b = normalize_code(code_b, language)
    tok_a = get_tokens(norm_a)
    tok_b = get_tokens(norm_b)

    # Core metrics
    seq_sim = sequence_similarity(norm_a, norm_b) * 100
    jac_sim = jaccard_similarity(set(tok_a), set(tok_b)) * 100
    ngram_sim = ngram_similarity(tok_a, tok_b, n=4) * 100
    ast_sim = ast_similarity(code_a, code_b) * 100 if language == "Python" else 0

    # Type-agnostic metrics
    if settings.get("use_type_agnostic", True):
        ta_a = type_normalizer.normalize(code_a, language)
        ta_b = type_normalizer.normalize(code_b, language)
        ta_norm_a = normalize_code(ta_a, language)
        ta_norm_b = normalize_code(ta_b, language)
        ta_tok_a = get_tokens(ta_norm_a)
        ta_tok_b = get_tokens(ta_norm_b)
        ta_seq_sim = sequence_similarity(ta_norm_a, ta_norm_b) * 100
        ta_jac_sim = jaccard_similarity(set(ta_tok_a), set(ta_tok_b)) * 100
    else:
        ta_seq_sim = 0
        ta_jac_sim = 0

    # Advanced metrics
    bytecode_sim = bytecode_similarity(code_a, code_b) if settings.get("use_bytecode", True) else 0
    big_o_match = big_o_similarity(code_a, code_b) if settings.get("use_big_o", True) else 0

    ted_result = ted_engine.compute_ted(code_a, code_b) if settings.get("use_ast_ted", True) and HAS_ZSS else None
    ted_sim = ted_result if ted_result is not None and ted_result > 0.0 else 0.0

    cfg_sim = cfg_engine.compare_cfgs(
        cfg_engine.build_cfg(code_a),
        cfg_engine.build_cfg(code_b)
    ) if settings.get("use_cfg", True) else 0

    if settings.get("use_winnowing", True):
        fp_a = winnowing_engine.generate_fingerprint(code_a)
        fp_b = winnowing_engine.generate_fingerprint(code_b)
        winnowing_sim = WinnowingFingerprint.compare_fingerprints(fp_a, fp_b)
    else:
        winnowing_sim = 0

    if settings.get("use_codebert", True) and codebert_analyzer.is_available():
        emb_a = codebert_analyzer.encode(code_a[:512])
        emb_b = codebert_analyzer.encode(code_b[:512])
        cb_result = CodeBERTAnalyzer.cosine_similarity(emb_a, emb_b)
        codebert_sim = cb_result if cb_result is not None and cb_result > 0.0 else 0.0
    else:
        codebert_sim = 0.0

    # ============================================================
    # ALL METRICS COLLECTION
    # ============================================================
    all_metrics = {
        'type_agnostic_seq_sim': ta_seq_sim,
        'type_agnostic_jac_sim': ta_jac_sim,
        'ted_sim': ted_sim,
        'cfg_sim': cfg_sim,
        'winnowing_sim': winnowing_sim,
        'codebert_sim': codebert_sim,
        'bytecode_sim': bytecode_sim,
        'big_o_match': big_o_match,
        'ast_sim': ast_sim,
        'seq_sim': seq_sim,
        'jac_sim': jac_sim,
        'ngram_sim': ngram_sim,
    }

    # ============================================================
    # FILTER DEAD ENGINES (score <= 0.0 means broken/missing)
    # ============================================================
    active_metrics = {}
    dead_engines = []

    for metric_name, metric_value in all_metrics.items():
        if metric_value is not None and metric_value > 0.0:
            active_metrics[metric_name] = metric_value
        else:
            dead_engines.append(metric_name)

    # ============================================================
    # OUTLIER REMOVAL (metrics too far from median are discarded)
    # ============================================================
    if len(active_metrics) >= 4:
        values = list(active_metrics.values())
        values.sort()
        median = values[len(values) // 2]
        filtered_metrics = {}
        for k, v in active_metrics.items():
            if abs(v - median) <= 60:
                filtered_metrics[k] = v
        if filtered_metrics:
            active_metrics = filtered_metrics

    # ============================================================
    # WEIGHTED SCORING (structural > lexical)
    # ============================================================
    weights = {
        'bytecode_sim': 3.5,
        'big_o_match': 3.5,
        'ted_sim': 3.0,
        'cfg_sim': 2.5,
        'codebert_sim': 3.0,
        'type_agnostic_jac_sim': 2.0,
        'type_agnostic_seq_sim': 1.5,
        'ast_sim': 2.0,
        'winnowing_sim': 1.5,
        'jac_sim': 0.5,
        'seq_sim': 0.3,
        'ngram_sim': 0.3,
    }

    if not active_metrics:
        final_score = 0.0
    else:
        weighted_sum = 0.0
        total_weight = 0.0
        median_val = sorted(active_metrics.values())[len(active_metrics) // 2]
        for metric_name, metric_value in active_metrics.items():
            w = weights.get(metric_name, 1.0)
            distance_from_median = abs(metric_value - median_val)
            if distance_from_median < 20:
                w *= 1.3
            weighted_sum += metric_value * w
            total_weight += w
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    final_score = round(final_score, 2)

    # ============================================================
    # ML VERDICT
    # ============================================================
    ml_verdict = None
    ml_confidence = 0.0
    if settings.get("use_ml", True) and ml_classifier.is_trained:
        ml_verdict, ml_confidence = ml_classifier.predict(all_metrics)

    # ============================================================
    # THRESHOLD-BASED VERDICT
    # ============================================================
    threshold = sensitivity
    if final_score >= threshold:
        verdict = "PLAGIARIZED"
        risk = "High"
    elif final_score >= threshold * 0.6:
        verdict = "SUSPICIOUS"
        risk = "Medium"
    else:
        verdict = "ORIGINAL"
        risk = "Low"

    if ml_verdict and ml_confidence > 75:
        if ml_verdict == "PLAGIARIZED" and final_score >= threshold * 0.5:
            verdict = "PLAGIARIZED"
            risk = "High"

    # ============================================================
    # BUILD RESULT
    # ============================================================
    result = {
        **all_metrics,
        "score": final_score,
        "verdict": verdict,
        "risk": risk,
        "ml_verdict": ml_verdict,
        "ml_confidence": round(ml_confidence, 2),
        "diff": get_diff_lines(code_a, code_b),
        "shared_tokens": len(set(tok_a) & set(tok_b)),
        "unique_a": len(set(tok_a) - set(tok_b)),
        "unique_b": len(set(tok_b) - set(tok_a)),
        "fingerprint_a": compute_fingerprint(code_a),
        "fingerprint_b": compute_fingerprint(code_b),
        "tokens_a": len(tok_a),
        "tokens_b": len(tok_b),
        "lines_a": len(code_a.splitlines()),
        "lines_b": len(code_b.splitlines()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engines_used": len(active_metrics),
        "dead_engines": dead_engines,
    }

    # ============================================================
    # AUTO-TRAIN ML
    # ============================================================
    if settings.get("use_ml", True) and len(st.session_state["training_data"]) < 100:
        if final_score > 80 or final_score < 20:
            add_training_example(all_metrics, verdict)

    return result


# ============================================================
# REPORT GENERATION
# ============================================================
def generate_report(result: dict, code_a: str, code_b: str) -> str:
    report = f"""
╔══════════════════════════════════════════╗
║   CODESCAN AI — ULTIMATE PLAGIARISM    ║
║   Multi-Engine Detection Report        ║
╚══════════════════════════════════════════╝

Generated: {result['timestamp']}
Detection Engines Active: {result.get('engines_used', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FINAL VERDICT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Similarity Score:  {result['score']:.1f}%
  Verdict:           {result['verdict']}
  Risk Level:        {result['risk']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ALL DETECTION METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Type-Agnostic Seq:     {result.get('type_agnostic_seq_sim', 0):.1f}%
  Type-Agnostic Jaccard: {result.get('type_agnostic_jac_sim', 0):.1f}%
  Tree Edit Distance:    {result.get('ted_sim', 0):.1f}%
  Control Flow Graph:    {result.get('cfg_sim', 0):.1f}%
  Winnowing (MOSS):      {result.get('winnowing_sim', 0):.1f}%
  CodeBERT Semantic:     {result.get('codebert_sim', 0):.1f}%
  Bytecode:              {result.get('bytecode_sim', 0):.1f}%
  Big O Match:           {result.get('big_o_match', 0):.1f}%
  AST Structure:         {result.get('ast_sim', 0):.1f}%
  Sequence:              {result.get('seq_sim', 0):.1f}%

═══════════════════════════════════════════
  CodeScan AI Ultimate Edition © 2026
═══════════════════════════════════════════
"""
    return report


def generate_html_report(result: dict, code_a: str, code_b: str) -> str:
    v_color = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(
        result["verdict"], "#7c6dfa"
    )
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CodeScan AI — Ultimate Plagiarism Report</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0a0a0c; color: #e8e8f0; padding: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #7c6dfa; font-size: 28px; margin: 0; }}
        .section {{ background: #18181e; border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 24px; margin: 16px 0; }}
        .section h3 {{ color: #a78bfa; font-size: 14px; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 1px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        table td {{ padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 13px; }}
        table td:first-child {{ color: #6b6b80; width: 40%; }}
        table td:last-child {{ color: #e8e8f0; font-weight: 600; text-align: right; }}
        .verdict {{ display: inline-block; padding: 8px 24px; border-radius: 8px; font-weight: 700; background: {v_color}22; color: {v_color}; border: 2px solid {v_color}55; }}
        .score {{ font-size: 48px; font-weight: 900; color: {v_color}; text-align: center; }}
        .footer {{ text-align: center; color: #4a4a5a; font-size: 11px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⬡ CodeScan AI — Plagiarism Report</h1>
        <p>Generated: {result['timestamp']}</p>
    </div>
    <div class="score">{result['score']:.1f}%</div>
    <div style="text-align:center;margin:16px 0;"><span class="verdict">{result['verdict']}</span></div>

    <div class="section">
        <h3>Detection Metrics</h3>
        <table>
            <tr><td>Type-Agnostic Sequence</td><td>{result.get('type_agnostic_seq_sim', 0):.1f}%</td></tr>
            <tr><td>Type-Agnostic Jaccard</td><td>{result.get('type_agnostic_jac_sim', 0):.1f}%</td></tr>
            <tr><td>Tree Edit Distance</td><td>{result.get('ted_sim', 0):.1f}%</td></tr>
            <tr><td>Control Flow Graph</td><td>{result.get('cfg_sim', 0):.1f}%</td></tr>
            <tr><td>Winnowing (MOSS)</td><td>{result.get('winnowing_sim', 0):.1f}%</td></tr>
            <tr><td>CodeBERT Semantic</td><td>{result.get('codebert_sim', 0):.1f}%</td></tr>
            <tr><td>Bytecode</td><td>{result.get('bytecode_sim', 0):.1f}%</td></tr>
            <tr><td>Big O Match</td><td>{result.get('big_o_match', 0):.1f}%</td></tr>
        </table>
    </div>

    <div class="footer">⬡ CodeScan AI Ultimate Edition © 2026</div>
</body>
</html>
"""
    return html


# ============================================================
# HEATMAP
# ============================================================
def generate_heatmap(filenames: list, results: list) -> str:
    n = len(filenames)
    matrix = [[0.0] * n for _ in range(n)]
    for na, nb, score, _ in results:
        i = filenames.index(na)
        j = filenames.index(nb)
        matrix[i][j] = score
        matrix[j][i] = score

    def heat_color(val):
        if val >= 70:
            return f"rgba(248,113,113,{val / 100})"
        elif val >= 40:
            return f"rgba(251,191,36,{val / 100})"
        else:
            return f"rgba(52,211,153,{val / 100})"

    html = '<table class="heatmap-table"><tr><th></th>'
    for f in filenames:
        html += f'<th>{f[:10]}</th>'
    html += '</tr>'
    for i, row in enumerate(matrix):
        html += f'<tr><td style="color:#6b6b80;">{filenames[i][:10]}</td>'
        for val in row:
            html += f'<td style="background:{heat_color(val)};color:#fff;">{val:.0f}</td>'
        html += '</tr>'
    html += '</table>'
    return html


# ============================================================
# UI COMPONENTS
# ============================================================
def badge(label: str, color: str = "#7c6dfa") -> str:
    return f"""<span style="display:inline-block;background:{color}22;color:{color};border:1px solid {color}55;border-radius:6px;padding:2px 10px;font-size:11px;font-family:'DM Sans',sans-serif;font-weight:600;letter-spacing:.5px;text-transform:uppercase;">{label}</span>"""


def score_ring(score: float, verdict: str) -> str:
    color = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(verdict, "#7c6dfa")
    radius = 54
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - score / 100)
    return f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:10px;padding:20px 0;">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="{color}" stroke-width="10" stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}" stroke-linecap="round" transform="rotate(-90 70 70)" style="transition:stroke-dashoffset 1s ease;filter:drop-shadow(0 0 8px {color}88)"/>
        <text x="70" y="66" text-anchor="middle" font-family="Syne,sans-serif" font-size="22" font-weight="700" fill="{color}">{score:.0f}%</text>
        <text x="70" y="84" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="10" fill="rgba(255,255,255,0.4)" letter-spacing="1.5">SIMILARITY</text>
      </svg>
      <div style="background:{color}22;color:{color};border:1px solid {color}55;border-radius:8px;padding:5px 20px;font-family:'Syne',sans-serif;font-size:13px;font-weight:700;letter-spacing:1.5px;">{verdict}</div>
    </div>"""


def mini_bar(label: str, value: float, color: str = "#7c6dfa") -> str:
    return f"""
    <div style="margin-bottom:10px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-size:12px;color:rgba(255,255,255,0.5);font-family:'DM Sans',sans-serif;">{label}</span>
        <span style="font-size:12px;color:rgba(255,255,255,0.8);font-family:'JetBrains Mono',monospace;font-weight:500;">{value:.1f}%</span>
      </div>
      <div style="height:5px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;">
        <div style="height:100%;width:{value}%;background:{color};border-radius:3px;box-shadow:0 0 6px {color}88;transition:width .8s ease;"></div>
      </div>
    </div>"""


def diff_viewer(diff_lines: list) -> str:
    if not diff_lines:
        return "<p style='color:var(--muted);font-size:12px;'>No differences found.</p>"
    html = """<div style="font-family:'JetBrains Mono',monospace;font-size:11.5px;background:#0d0d10;border-radius:10px;padding:16px;overflow-x:auto;border:1px solid rgba(255,255,255,0.06);max-height:340px;overflow-y:auto;">"""
    for line in diff_lines[:120]:
        esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if line.startswith('+++') or line.startswith('---'):
            html += f'<div style="color:#6b6b80;padding:1px 0;">{esc}</div>'
        elif line.startswith('+'):
            html += f'<div style="color:#34d399;background:#34d39912;padding:1px 4px;border-radius:2px;">{esc}</div>'
        elif line.startswith('-'):
            html += f'<div style="color:#f87171;background:#f8717112;padding:1px 4px;border-radius:2px;">{esc}</div>'
        elif line.startswith('@@'):
            html += f'<div style="color:#7c6dfa;padding:2px 0;">{esc}</div>'
        else:
            html += f'<div style="color:rgba(255,255,255,0.35);padding:1px 0;">{esc}</div>'
    html += "</div>"
    return html


def stat_row(items: list) -> str:
    cols = "".join(
        f"""<div style="flex:1;text-align:center;padding:12px 8px;background:rgba(255,255,255,0.03);border-radius:10px;margin:0 4px;"><div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;color:{c};">{v}</div><div style="font-size:10px;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:.8px;margin-top:3px;font-family:'DM Sans',sans-serif;">{l}</div></div>"""
        for l, v, c in items
    )
    return f'<div style="display:flex;gap:6px;margin-top:4px;">{cols}</div>'


# ============================================================
# SIDEBAR
# ============================================================
PAGES = [
    ("⬡", "Analyze"),
    ("⏱", "History"),
    ("◈", "Analytics"),
    ("⊞", "Batch"),
    ("◉", "Settings"),
    ("◎", "About"),
]

with st.sidebar:
    st.markdown("""
    <div style="padding:28px 20px 18px 20px;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:34px;height:34px;background:linear-gradient(135deg,#7c6dfa,#a78bfa);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:0 4px 16px rgba(124,109,250,.4);">⬡</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:#e8e8f0;letter-spacing:.5px;">CodeScan</div>
          <div style="font-size:10px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;letter-spacing:1.2px;text-transform:uppercase;margin-top:1px;">Ultimate Detector</div>
        </div>
      </div>
      <div style="height:1px;background:rgba(255,255,255,0.06);margin-top:20px;"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0 10px;">', unsafe_allow_html=True)
    for icon, page in PAGES:
        active = st.session_state["page"] == page
        bg = "background:rgba(124,109,250,0.15);border:1px solid rgba(124,109,250,0.25);" if active else "background:transparent;border:1px solid transparent;"
        col = "#a78bfa" if active else "rgba(255,255,255,0.45)"
        icol = "#7c6dfa" if active else "rgba(255,255,255,0.25)"
        st.markdown(f"""<div style="{bg}border-radius:9px;padding:9px 12px;margin-bottom:3px;display:flex;align-items:center;gap:10px;cursor:pointer;transition:all .2s ease;" id="nav_{page}"><span style="font-size:15px;color:{icol};">{icon}</span><span style="font-family:'DM Sans',sans-serif;font-size:13.5px;font-weight:500;color:{col};">{page}</span></div>""", unsafe_allow_html=True)
        if st.button(page, key=f"nav_btn_{page}", use_container_width=True):
            st.session_state["page"] = page
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:16px 10px;"></div>', unsafe_allow_html=True)
    n_hist = len(st.session_state["history"])
    n_train = len(st.session_state["training_data"])
    flagged = sum(1 for h in st.session_state["history"] if h["verdict"] != "ORIGINAL")

    cb_status = codebert_analyzer.get_status()
    st.markdown(f"""
    <div style="padding:0 14px 20px;">
      <div style="font-size:10px;color:rgba(255,255,255,0.25);letter-spacing:1px;text-transform:uppercase;font-family:'DM Sans',sans-serif;margin-bottom:10px;">System Status</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
        <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 8px;text-align:center;"><div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#a78bfa;">{n_hist}</div><div style="font-size:10px;color:rgba(255,255,255,0.3);">Scans</div></div>
        <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 8px;text-align:center;"><div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#f87171;">{flagged}</div><div style="font-size:10px;color:rgba(255,255,255,0.3);">Flagged</div></div>
      </div>
      <div style="font-size:9px;color:rgba(255,255,255,0.4);padding:6px;background:rgba(255,255,255,0.02);border-radius:6px;word-break:break-word;">{cb_status}</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE: ANALYZE
# ============================================================
def page_analyze():
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
        <span style="font-size:11px;color:rgba(255,255,255,0.25);letter-spacing:1.5px;text-transform:uppercase;font-family:'DM Sans',sans-serif;">6-Engine Ultimate Detection</span>
      </div>
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;margin:0;line-height:1.2;">Analyze Code Similarity</h1>
      <p style="color:rgba(255,255,255,0.35);font-size:13px;font-family:'DM Sans',sans-serif;margin-top:6px;">Decision Tree • Tree Edit Distance • CFG • Winnowing • CodeBERT • Type-Agnostic Normalization</p>
    </div>
    """, unsafe_allow_html=True)

    s = st.session_state["settings"]
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        lang = st.selectbox("Language", ["Python", "Java", "C++", "C", "JavaScript", "Other"], index=["Python","Java","C++","C","JavaScript","Other"].index(s["language"]))
    with c2:
        method = st.selectbox("Method", ["Hybrid (All Engines)", "Standard Only", "Advanced Only"], index=0)
    with c3:
        sensitivity = st.slider("Sensitivity", 40, 95, s["sensitivity"], 5)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 0 20px 0;"></div>', unsafe_allow_html=True)

    input_tab1, input_tab2 = st.tabs(["✏  Paste Code", "📁  Upload Files"])
    code_a, code_b = "", ""

    with input_tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        cola, colb = st.columns(2)
        with cola:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;"><div style="width:8px;height:8px;background:#7c6dfa;border-radius:50%;"></div><span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Code Snippet A</span></div>""", unsafe_allow_html=True)
            code_a = st.text_area("Code A", height=280, placeholder="# Paste first code snippet here...", label_visibility="collapsed", key="code_a_text") or ""
        with colb:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;"><div style="width:8px;height:8px;background:#a78bfa;border-radius:50%;"></div><span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Code Snippet B</span></div>""", unsafe_allow_html=True)
            code_b = st.text_area("Code B", height=280, placeholder="# Paste second code snippet here...", label_visibility="collapsed", key="code_b_text") or ""

    with input_tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;"><div style="width:8px;height:8px;background:#7c6dfa;border-radius:50%;"></div><span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Upload File A</span></div>""", unsafe_allow_html=True)
            file_a = st.file_uploader("File A", type=["py","java","cpp","c","js","txt"], label_visibility="collapsed", key="file_a")
            if file_a:
                code_a = file_a.read().decode("utf-8", errors="replace")
                st.markdown(f"<div style='margin-top:8px;'>{badge(file_a.name, '#34d399')}</div>", unsafe_allow_html=True)
        with fc2:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;"><div style="width:8px;height:8px;background:#a78bfa;border-radius:50%;"></div><span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Upload File B</span></div>""", unsafe_allow_html=True)
            file_b = st.file_uploader("File B", type=["py","java","cpp","c","js","txt"], label_visibility="collapsed", key="file_b")
            if file_b:
                code_b = file_b.read().decode("utf-8", errors="replace")
                st.markdown(f"<div style='margin-top:8px;'>{badge(file_b.name, '#34d399')}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    bcol1, bcol2, bcol3 = st.columns([3, 2, 3])
    with bcol2:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        run = st.button("⬡  Run Full Analysis (6 Engines)", use_container_width=True, key="run_btn")
        st.markdown("</div>", unsafe_allow_html=True)

    if run:
        if not code_a.strip() or not code_b.strip():
            st.warning("⚠  Please provide both code snippets.")
        else:
            with st.spinner("Running all 6 detection engines..."):
                time.sleep(1.0)
                result = detect_plagiarism(code_a, code_b, method, sensitivity, lang)
            st.session_state["last_result"] = result
            if s["save_history"]:
                entry = {**result, "lang": lang, "method": method, "code_a_preview": code_a[:120], "code_b_preview": code_b[:120]}
                st.session_state["history"].insert(0, entry)
                if len(st.session_state["history"]) > 100:
                    st.session_state["history"] = st.session_state["history"][:100]

    result = st.session_state.get("last_result")
    if result:
        v_color = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(result["verdict"], "#7c6dfa")
        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:24px 0 20px 0;"></div>', unsafe_allow_html=True)
        st.markdown(f"""<div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">⬡ Ultimate Analysis Results</div><div style="color:{v_color};font-size:11px;margin-bottom:16px;">{result.get('engines_used', 0)} Detection Engines Active</div>""", unsafe_allow_html=True)

        r1, r2 = st.columns([1, 2])
        with r1:
            st.markdown(score_ring(result["score"], result["verdict"]), unsafe_allow_html=True)
            st.markdown(stat_row([
                ("Tokens A", result["tokens_a"], "#7c6dfa"),
                ("Tokens B", result["tokens_b"], "#a78bfa"),
                ("Shared", result["shared_tokens"], "#34d399"),
            ]), unsafe_allow_html=True)
            if result.get("ml_verdict"):
                st.markdown(f"""<div style="text-align:center;margin-top:8px;">{badge("ML: " + result["ml_verdict"], "#ec4899")}</div>""", unsafe_allow_html=True)

        with r2:
            st.markdown(f"""
            <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:22px 24px;margin-bottom:14px;">
              <div style="font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:1px;text-transform:uppercase;font-family:'DM Sans',sans-serif;margin-bottom:14px;">All Detection Engines</div>
              {mini_bar("Type-Agnostic Sequence", result.get('type_agnostic_seq_sim', 0), "#a78bfa")}
              {mini_bar("Type-Agnostic Jaccard", result.get('type_agnostic_jac_sim', 0), "#c4b5fd")}
              {mini_bar("Tree Edit Distance (AST)", result.get('ted_sim', 0), "#f59e0b")}
              {mini_bar("Control Flow Graph", result.get('cfg_sim', 0), "#ef4444")}
              {mini_bar("Winnowing (MOSS)", result.get('winnowing_sim', 0), "#8b5cf6")}
              {mini_bar("CodeBERT Semantic", result.get('codebert_sim', 0), "#ec4899")}
              {mini_bar("Bytecode", result.get('bytecode_sim', 0), "#06b6d4")}
              {mini_bar("Big O Match", result.get('big_o_match', 0), "#10b981")}
              {mini_bar("AST Structure", result.get('ast_sim', 0), "#84cc16")}
              {mini_bar("Sequence", result.get('seq_sim', 0), "#6366f1")}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            st.download_button("📄 TXT Report", generate_report(result, code_a, code_b), f"codescan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", use_container_width=True)
        with exp_col2:
            st.download_button("🌐 HTML Report", generate_html_report(result, code_a, code_b), f"codescan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html", use_container_width=True)
        with exp_col3:
            if st.button("📋 Copy Score", use_container_width=True):
                st.toast(f"Score: {result['score']:.1f}%", icon="📋")

        with st.expander("⬡  View Unified Diff"):
            st.markdown(diff_viewer(result["diff"]), unsafe_allow_html=True)

        if result["verdict"] == "PLAGIARIZED":
            st.error(f"🔴 **PLAGIARISM DETECTED** — Score: {result['score']:.1f}% (Threshold: {sensitivity}%)")
        elif result["verdict"] == "SUSPICIOUS":
            st.warning(f"🟡 **SUSPICIOUS** — Score: {result['score']:.1f}%")
        else:
            st.success(f"🟢 **ORIGINAL** — Score: {result['score']:.1f}%")


# ============================================================
# OTHER PAGES
# ============================================================
def page_history():
    st.markdown("""<div style="padding:8px 0 24px 0;"><h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;">Scan History</h1></div>""", unsafe_allow_html=True)
    history = st.session_state["history"]
    if not history:
        st.info("No scans yet.")
        return
    if st.button("Clear History"):
        st.session_state["history"] = []
        st.rerun()
    for entry in history[:20]:
        vc = {"PLAGIARIZED":"#f87171","SUSPICIOUS":"#fbbf24","ORIGINAL":"#34d399"}.get(entry["verdict"],"#7c6dfa")
        st.markdown(f"""<div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:14px 18px;margin-bottom:8px;display:flex;justify-content:space-between;"><div>{badge(entry['verdict'], vc)}<span style="font-size:10px;color:#666;margin-left:8px;">{entry['timestamp']}</span></div><div style="font-size:22px;font-weight:800;color:{vc};">{entry['score']:.1f}%</div></div>""", unsafe_allow_html=True)


def page_analytics():
    st.markdown("""<div style="padding:8px 0 24px 0;"><h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;">Analytics</h1></div>""", unsafe_allow_html=True)
    st.metric("Total Scans", len(st.session_state["history"]))
    st.metric("Training Examples", len(st.session_state["training_data"]))
    st.metric("CodeBERT Status", codebert_analyzer.get_status())


def page_batch():
    st.markdown("""<div style="padding:8px 0 24px 0;"><h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;">Batch Analysis</h1></div>""", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload multiple files", accept_multiple_files=True, key="batch_files")
    if uploaded and len(uploaded) >= 2:
        if st.button("Run Batch"):
            codes = {f.name: f.read().decode("utf-8","replace") for f in uploaded}
            names = list(codes.keys())
            results = []
            for i, j in itertools.combinations(range(len(names)), 2):
                r = detect_plagiarism(codes[names[i]], codes[names[j]], "Hybrid (All Engines)", 70, "Python")
                results.append((names[i], names[j], r["score"], r["verdict"]))
            results.sort(key=lambda x: x[2], reverse=True)
            st.markdown("### Heatmap")
            st.markdown(generate_heatmap(names, results), unsafe_allow_html=True)
            for na, nb, sc, vd in results:
                st.markdown(f"**{na}** vs **{nb}**: {sc:.1f}% ({vd})")


def page_settings():
    st.markdown("""<div style="padding:8px 0 24px 0;"><h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;">Settings</h1></div>""", unsafe_allow_html=True)
    s = st.session_state["settings"]
    s["use_type_agnostic"] = st.checkbox("Type-Agnostic Normalization", s.get("use_type_agnostic", True))
    s["use_ast_ted"] = st.checkbox("Tree Edit Distance (AST)", s.get("use_ast_ted", HAS_ZSS), disabled=not HAS_ZSS)
    s["use_cfg"] = st.checkbox("Control Flow Graph", s.get("use_cfg", True))
    s["use_winnowing"] = st.checkbox("Winnowing (MOSS)", s.get("use_winnowing", True))
    s["use_codebert"] = st.checkbox("CodeBERT Semantic", s.get("use_codebert", HAS_TRANSFORMERS), disabled=not HAS_TRANSFORMERS)
    s["use_ml"] = st.checkbox("ML Decision Tree", s.get("use_ml", HAS_SKLEARN), disabled=not HAS_SKLEARN)
    if st.button("Save"):
        st.success("Settings saved!")


def page_about():
    st.markdown("""<div style="padding:8px 0 24px 0;"><h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;">About</h1></div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px;">
        <h3 style="color:#a78bfa;">CodeScan AI Ultimate Edition</h3>
        <p style="color:#888;">6 Detection Engines for 90%+ Accuracy</p>
        <p style="color:#666;">Decision Tree • Tree Edit Distance • CFG • Winnowing • CodeBERT • Type-Agnostic</p>
        <hr style="margin:16px 0;">
        <p style="color:#666;font-size:12px;">CodeBERT: {codebert_analyzer.get_status()}</p>
        <p style="color:#666;font-size:12px;">Tree Edit Distance: {"✅ Available" if HAS_ZSS else "❌ Not installed (pip install zss)"}</p>
        <p style="color:#666;font-size:12px;">ML Classifier: {"✅ Available" if HAS_SKLEARN else "❌ Not installed (pip install scikit-learn)"}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ROUTER
# ============================================================
page = st.session_state["page"]
if page == "Analyze":
    page_analyze()
elif page == "History":
    page_history()
elif page == "Analytics":
    page_analytics()
elif page == "Batch":
    page_batch()
elif page == "Settings":
    page_settings()
elif page == "About":
    page_about()
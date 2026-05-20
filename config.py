import streamlit as st
from typing import List, Dict, Tuple, Set, Optional
from datetime import datetime
from collections import defaultdict, Counter, deque
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# EXTERNAL DEPENDENCY FLAGS
# ============================================================
HAS_SKLEARN = False
HAS_ZSS = False
HAS_TRANSFORMERS = False
HAS_PLOTLY = False
HAS_PANDAS = False

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

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    pass

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pass


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

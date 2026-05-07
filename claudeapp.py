import streamlit as st
import difflib
import hashlib
import json
import time
import re
import ast
import math
from datetime import datetime
from collections import defaultdict
import random

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CodeScan — Plagiarism Detector",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Root ── */
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

/* ── Streamlit Shell ── */
.stApp { background: var(--bg) !important; font-family: var(--font-body); color: var(--text); }
.stApp > header { background: transparent !important; }
#MainMenu, footer, .stDeployButton { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
section[data-testid="stSidebarContent"] { padding: 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--muted2); border-radius: 10px; }

/* ── Buttons ── */
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

/* ── Primary button variant ── */
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

/* ── Text inputs ── */
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

/* ── Selectbox ── */
.stSelectbox > div > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: var(--surface2) !important;
  border: 1px dashed var(--border2) !important;
  border-radius: 12px !important;
  padding: 8px !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--accent) !important;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

/* ── Metrics ── */
[data-testid="stMetric"] {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .7px; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: var(--font-head) !important; font-size: 28px !important; }

/* ── Expander ── */
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

/* ── Tabs ── */
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

/* ── Progress bar ── */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
  border-radius: 4px !important;
}
.stProgress > div > div {
  background: var(--surface3) !important;
  border-radius: 4px !important;
}

/* ── Slider ── */
.stSlider [data-baseweb="slider"] { }
.stSlider .rc-slider-track { background: var(--accent) !important; }
.stSlider .rc-slider-handle { border-color: var(--accent) !important; background: var(--accent) !important; }

/* ── Checkbox / Radio ── */
.stCheckbox label, .stRadio label { color: var(--text) !important; font-family: var(--font-body) !important; font-size: 13px !important; }

/* ── Info / Warning / Error ── */
.stAlert {
  border-radius: 10px !important;
  font-family: var(--font-body) !important;
  font-size: 13px !important;
  border-left-width: 3px !important;
}

/* ── Code blocks ── */
code, .stCode { font-family: var(--font-mono) !important; font-size: 12px !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "Analyze",
        "history": [],
        "settings": {
            "sensitivity": 70,
            "language": "Python",
            "method": "Hybrid (AST + Token)",
            "theme": "Dark",
            "save_history": True,
        },
        "last_result": None,
        "uploads_a": None,
        "uploads_b": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
#  PLAGIARISM ENGINE
# ─────────────────────────────────────────────

def normalize_code(code: str, language: str = "Python") -> str:
    """Strip comments, normalize whitespace, lowercase identifiers."""
    # Remove single-line comments
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    # Remove multi-line comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
    code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
    # Remove string literals (replace with placeholder)
    code = re.sub(r'"[^"]*"', '"STR"', code)
    code = re.sub(r"'[^']*'", "'STR'", code)
    # Remove numbers
    code = re.sub(r'\b\d+\.?\d*\b', 'NUM', code)
    # Normalize whitespace
    code = re.sub(r'\s+', ' ', code).strip()
    return code.lower()


def get_tokens(code: str) -> list:
    tokens = re.findall(r'[a-zA-Z_]\w*|[+\-*/=<>!&|%^~]+|[(){}\[\];:,.]', code)
    return tokens


def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def ngram_similarity(tokens_a: list, tokens_b: list, n: int = 4) -> float:
    def ngrams(lst, n):
        return set(tuple(lst[i:i+n]) for i in range(len(lst)-n+1))
    ng_a = ngrams(tokens_a, n)
    ng_b = ngrams(tokens_b, n)
    return jaccard_similarity(ng_a, ng_b)


def sequence_similarity(code_a: str, code_b: str) -> float:
    return difflib.SequenceMatcher(None, code_a, code_b).ratio()


def ast_similarity(code_a: str, code_b: str) -> float:
    """Compare AST node type sequences."""
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
    set_a = set(seq_a)
    set_b = set(seq_b)
    return jaccard_similarity(set_a, set_b)


def compute_fingerprint(code: str) -> str:
    norm = normalize_code(code)
    return hashlib.md5(norm.encode()).hexdigest()


def get_diff_lines(code_a: str, code_b: str) -> list:
    lines_a = code_a.splitlines()
    lines_b = code_b.splitlines()
    diff = list(difflib.unified_diff(lines_a, lines_b, lineterm='', n=2))
    return diff


def detect_plagiarism(code_a: str, code_b: str, method: str, sensitivity: int, language: str) -> dict:
    """Main detection pipeline."""
    norm_a = normalize_code(code_a, language)
    norm_b = normalize_code(code_b, language)
    tok_a  = get_tokens(norm_a)
    tok_b  = get_tokens(norm_b)

    seq_sim   = sequence_similarity(norm_a, norm_b)
    jac_sim   = jaccard_similarity(set(tok_a), set(tok_b))
    ngram_sim = ngram_similarity(tok_a, tok_b, n=4)
    ast_sim   = ast_similarity(code_a, code_b) if language == "Python" else 0.5

    if "AST" in method and language == "Python":
        score = (seq_sim * 0.30 + jac_sim * 0.25 + ngram_sim * 0.25 + ast_sim * 0.20)
    elif "Token" in method:
        score = (seq_sim * 0.35 + jac_sim * 0.30 + ngram_sim * 0.35)
    else:
        score = (seq_sim * 0.50 + jac_sim * 0.25 + ngram_sim * 0.25)

    score = round(score * 100, 2)
    threshold = sensitivity

    if score >= threshold:
        verdict = "PLAGIARIZED"
        risk = "High"
    elif score >= threshold * 0.6:
        verdict = "SUSPICIOUS"
        risk = "Medium"
    else:
        verdict = "ORIGINAL"
        risk = "Low"

    diff_lines = get_diff_lines(code_a, code_b)

    shared_tokens = set(tok_a) & set(tok_b)
    unique_a = set(tok_a) - set(tok_b)
    unique_b = set(tok_b) - set(tok_a)

    return {
        "score": score,
        "verdict": verdict,
        "risk": risk,
        "seq_sim": round(seq_sim * 100, 2),
        "jac_sim": round(jac_sim * 100, 2),
        "ngram_sim": round(ngram_sim * 100, 2),
        "ast_sim": round(ast_sim * 100, 2),
        "diff": diff_lines,
        "shared_tokens": len(shared_tokens),
        "unique_a": len(unique_a),
        "unique_b": len(unique_b),
        "fingerprint_a": compute_fingerprint(code_a),
        "fingerprint_b": compute_fingerprint(code_b),
        "tokens_a": len(tok_a),
        "tokens_b": len(tok_b),
        "lines_a": len(code_a.splitlines()),
        "lines_b": len(code_b.splitlines()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ─────────────────────────────────────────────
#  UI COMPONENTS
# ─────────────────────────────────────────────

def badge(label: str, color: str = "#7c6dfa") -> str:
    return f"""<span style="
        display:inline-block;
        background:{color}22;
        color:{color};
        border:1px solid {color}55;
        border-radius:6px;
        padding:2px 10px;
        font-size:11px;
        font-family:'DM Sans',sans-serif;
        font-weight:600;
        letter-spacing:.5px;
        text-transform:uppercase;
    ">{label}</span>"""


def card(content_html: str, padding: str = "20px 24px") -> str:
    return f"""<div style="
        background:var(--surface2,#18181e);
        border:1px solid rgba(255,255,255,0.07);
        border-radius:14px;
        padding:{padding};
        margin-bottom:16px;
    ">{content_html}</div>"""


def score_ring(score: float, verdict: str) -> str:
    color = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(verdict, "#7c6dfa")
    radius = 54
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - score / 100)
    return f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:10px;padding:20px 0;">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="{color}" stroke-width="10"
          stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}"
          stroke-linecap="round" transform="rotate(-90 70 70)"
          style="transition:stroke-dashoffset 1s ease;filter:drop-shadow(0 0 8px {color}88)"/>
        <text x="70" y="66" text-anchor="middle" font-family="Syne,sans-serif"
          font-size="22" font-weight="700" fill="{color}">{score}%</text>
        <text x="70" y="84" text-anchor="middle" font-family="DM Sans,sans-serif"
          font-size="10" fill="rgba(255,255,255,0.4)" letter-spacing="1.5">SIMILARITY</text>
      </svg>
      <div style="
        background:{color}22;color:{color};
        border:1px solid {color}55;border-radius:8px;
        padding:5px 20px;font-family:'Syne',sans-serif;
        font-size:13px;font-weight:700;letter-spacing:1.5px;
      ">{verdict}</div>
    </div>"""


def mini_bar(label: str, value: float, color: str = "#7c6dfa") -> str:
    return f"""
    <div style="margin-bottom:10px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-size:12px;color:rgba(255,255,255,0.5);font-family:'DM Sans',sans-serif;">{label}</span>
        <span style="font-size:12px;color:rgba(255,255,255,0.8);font-family:'JetBrains Mono',monospace;font-weight:500;">{value}%</span>
      </div>
      <div style="height:5px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;">
        <div style="height:100%;width:{value}%;background:{color};border-radius:3px;
          box-shadow:0 0 6px {color}88;transition:width .8s ease;"></div>
      </div>
    </div>"""


def diff_viewer(diff_lines: list) -> str:
    if not diff_lines:
        return "<p style='color:var(--muted);font-size:12px;font-family:JetBrains Mono,monospace;'>No differences found.</p>"
    html = """<div style="font-family:'JetBrains Mono',monospace;font-size:11.5px;
        background:#0d0d10;border-radius:10px;padding:16px;overflow-x:auto;
        border:1px solid rgba(255,255,255,0.06);max-height:340px;overflow-y:auto;">"""
    for line in diff_lines[:120]:
        esc = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
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
    """items = list of (label, value, color)"""
    cols = "".join(f"""
      <div style="flex:1;text-align:center;padding:12px 8px;
        background:rgba(255,255,255,0.03);border-radius:10px;margin:0 4px;">
        <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;color:{c};">{v}</div>
        <div style="font-size:10px;color:rgba(255,255,255,0.35);text-transform:uppercase;
          letter-spacing:.8px;margin-top:3px;font-family:'DM Sans',sans-serif;">{l}</div>
      </div>""" for l,v,c in items)
    return f'<div style="display:flex;gap:6px;margin-top:4px;">{cols}</div>'


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
PAGES = [
    ("⬡", "Analyze"),
    ("⏱", "History"),
    ("◈", "Analytics"),
    ("⊞", "Batch"),
    ("◉", "Settings"),
    ("◎", "About"),
]

with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:28px 20px 18px 20px;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:34px;height:34px;background:linear-gradient(135deg,#7c6dfa,#a78bfa);
          border-radius:9px;display:flex;align-items:center;justify-content:center;
          font-size:16px;box-shadow:0 4px 16px rgba(124,109,250,.4);">⬡</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;
            color:#e8e8f0;letter-spacing:.5px;">CodeScan</div>
          <div style="font-size:10px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;
            letter-spacing:1.2px;text-transform:uppercase;margin-top:1px;">AI Plagiarism Detector</div>
        </div>
      </div>
      <div style="height:1px;background:rgba(255,255,255,0.06);margin-top:20px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # Nav
    st.markdown('<div style="padding:0 10px;">', unsafe_allow_html=True)
    for icon, page in PAGES:
        active = st.session_state["page"] == page
        bg   = "background:rgba(124,109,250,0.15);border:1px solid rgba(124,109,250,0.25);" if active else "background:transparent;border:1px solid transparent;"
        col  = "#a78bfa" if active else "rgba(255,255,255,0.45)"
        icol = "#7c6dfa" if active else "rgba(255,255,255,0.25)"
        st.markdown(f"""
        <div style="
            {bg}
            border-radius:9px;padding:9px 12px;margin-bottom:3px;
            display:flex;align-items:center;gap:10px;cursor:pointer;
            transition:all .2s ease;
        " id="nav_{page}">
          <span style="font-size:15px;color:{icol};">{icon}</span>
          <span style="font-family:'DM Sans',sans-serif;font-size:13.5px;font-weight:500;color:{col};">{page}</span>
        </div>""", unsafe_allow_html=True)
        if st.button(page, key=f"nav_btn_{page}", use_container_width=True):
            st.session_state["page"] = page
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Quick stats in sidebar
    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:16px 10px;"></div>', unsafe_allow_html=True)
    n_hist = len(st.session_state["history"])
    flagged = sum(1 for h in st.session_state["history"] if h["verdict"] != "ORIGINAL")
    st.markdown(f"""
    <div style="padding:0 14px 20px;">
      <div style="font-size:10px;color:rgba(255,255,255,0.25);letter-spacing:1px;
        text-transform:uppercase;font-family:'DM Sans',sans-serif;margin-bottom:10px;">Quick Stats</div>
      <div style="display:flex;gap:8px;">
        <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 8px;text-align:center;">
          <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#a78bfa;">{n_hist}</div>
          <div style="font-size:10px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;">Scans</div>
        </div>
        <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 8px;text-align:center;">
          <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#f87171;">{flagged}</div>
          <div style="font-size:10px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;">Flagged</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE — ANALYZE
# ─────────────────────────────────────────────
def page_analyze():
    # Header
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
        <span style="font-size:11px;color:rgba(255,255,255,0.25);letter-spacing:1.5px;
          text-transform:uppercase;font-family:'DM Sans',sans-serif;">Plagiarism Detection</span>
      </div>
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;margin:0;line-height:1.2;">
        Analyze Code Similarity
      </h1>
      <p style="color:rgba(255,255,255,0.35);font-size:13px;font-family:'DM Sans',sans-serif;margin-top:6px;">
        Paste or upload two code snippets to detect plagiarism using AI-powered analysis.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Settings strip
    s = st.session_state["settings"]
    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
    with c1:
        lang = st.selectbox("Language", ["Python", "Java", "C++", "C", "JavaScript", "Other"], index=["Python","Java","C++","C","JavaScript","Other"].index(s["language"]))
    with c2:
        method = st.selectbox("Detection Method", ["Hybrid (AST + Token)", "Token Only", "Sequence"], index=["Hybrid (AST + Token)","Token Only","Sequence"].index(s["method"]))
    with c3:
        sensitivity = st.slider("Sensitivity Threshold", 40, 95, s["sensitivity"], 5, help="Minimum similarity % to flag as plagiarized")
    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 0 20px 0;"></div>', unsafe_allow_html=True)

    # Input tabs
    input_tab1, input_tab2 = st.tabs(["✏  Paste Code", "📁  Upload Files"])

    code_a, code_b = "", ""

    with input_tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        cola, colb = st.columns(2)
        with cola:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
              <div style="width:8px;height:8px;background:#7c6dfa;border-radius:50%;"></div>
              <span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Code Snippet A</span>
            </div>""", unsafe_allow_html=True)
            code_a_input = st.text_area("Code A", height=320, placeholder="# Paste your first code snippet here...\ndef example():\n    pass", label_visibility="collapsed", key="code_a_text")
        with colb:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
              <div style="width:8px;height:8px;background:#a78bfa;border-radius:50%;"></div>
              <span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Code Snippet B</span>
            </div>""", unsafe_allow_html=True)
            code_b_input = st.text_area("Code B", height=320, placeholder="# Paste your second code snippet here...\ndef example():\n    pass", label_visibility="collapsed", key="code_b_text")
        code_a = code_a_input or ""
        code_b = code_b_input or ""

    with input_tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
              <div style="width:8px;height:8px;background:#7c6dfa;border-radius:50%;"></div>
              <span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Upload File A</span>
            </div>""", unsafe_allow_html=True)
            file_a = st.file_uploader("File A", type=["py","java","cpp","c","js","txt"], label_visibility="collapsed", key="file_a")
            if file_a:
                code_a = file_a.read().decode("utf-8", errors="replace")
                st.markdown(f"<div style='margin-top:8px;'>{badge(file_a.name, '#34d399')}</div>", unsafe_allow_html=True)
        with fc2:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
              <div style="width:8px;height:8px;background:#a78bfa;border-radius:50%;"></div>
              <span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Upload File B</span>
            </div>""", unsafe_allow_html=True)
            file_b = st.file_uploader("File B", type=["py","java","cpp","c","js","txt"], label_visibility="collapsed", key="file_b")
            if file_b:
                code_b = file_b.read().decode("utf-8", errors="replace")
                st.markdown(f"<div style='margin-top:8px;'>{badge(file_b.name, '#34d399')}</div>", unsafe_allow_html=True)

    # Analyze button
    st.markdown("<br>", unsafe_allow_html=True)
    bcol1, bcol2, bcol3 = st.columns([3, 2, 3])
    with bcol2:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        run = st.button("⬡  Run Analysis", use_container_width=True, key="run_btn")
        st.markdown("</div>", unsafe_allow_html=True)

    if run:
        if not code_a.strip() or not code_b.strip():
            st.warning("⚠  Please provide both code snippets before running analysis.")
        else:
            with st.spinner("Analyzing code similarity…"):
                time.sleep(0.6)
                result = detect_plagiarism(code_a, code_b, method, sensitivity, lang)

            st.session_state["last_result"] = result
            if st.session_state["settings"]["save_history"]:
                entry = {**result, "lang": lang, "method": method,
                         "code_a_preview": code_a[:120], "code_b_preview": code_b[:120]}
                st.session_state["history"].insert(0, entry)
                if len(st.session_state["history"]) > 50:
                    st.session_state["history"] = st.session_state["history"][:50]

    # ── Results ──
    result = st.session_state.get("last_result")
    if result:
        v_color = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(result["verdict"], "#7c6dfa")

        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:24px 0 20px 0;"></div>', unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;
            color:#e8e8f0;margin-bottom:16px;">⬡ Analysis Results</div>""", unsafe_allow_html=True)

        r1, r2 = st.columns([1, 2])

        with r1:
            st.markdown(score_ring(result["score"], result["verdict"]), unsafe_allow_html=True)
            st.markdown(stat_row([
                ("Tokens A", result["tokens_a"], "#7c6dfa"),
                ("Tokens B", result["tokens_b"], "#a78bfa"),
                ("Shared",   result["shared_tokens"], "#34d399"),
            ]), unsafe_allow_html=True)

        with r2:
            st.markdown(f"""
            <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);
              border-radius:14px;padding:22px 24px;margin-bottom:14px;">
              <div style="font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:1px;
                text-transform:uppercase;font-family:'DM Sans',sans-serif;margin-bottom:14px;">Metric Breakdown</div>
              {mini_bar("Sequence Similarity", result["seq_sim"], "#7c6dfa")}
              {mini_bar("Token Jaccard",       result["jac_sim"], "#a78bfa")}
              {mini_bar("N-gram (4-gram)",     result["ngram_sim"], "#60a5fa")}
              {mini_bar("AST Structure",       result["ast_sim"], "#34d399")}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);
              border-radius:14px;padding:16px 24px;">
              <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                {badge("Risk: " + result["risk"],  {"High":"#f87171","Medium":"#fbbf24","Low":"#34d399"}.get(result["risk"],"#7c6dfa"))}
                {badge("Lang: " + lang, "#60a5fa")}
                {badge("Method: " + method.split()[0], "#7c6dfa")}
                {badge("Threshold: " + str(sensitivity) + "%", "#a78bfa")}
              </div>
              <div style="margin-top:14px;display:flex;flex-wrap:wrap;gap:16px;">
                <div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:.8px;
                    text-transform:uppercase;font-family:'DM Sans',sans-serif;">Fingerprint A</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                    color:rgba(255,255,255,0.5);margin-top:3px;">{result["fingerprint_a"][:16]}…</div>
                </div>
                <div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:.8px;
                    text-transform:uppercase;font-family:'DM Sans',sans-serif;">Fingerprint B</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                    color:rgba(255,255,255,0.5);margin-top:3px;">{result["fingerprint_b"][:16]}…</div>
                </div>
                <div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:.8px;
                    text-transform:uppercase;font-family:'DM Sans',sans-serif;">Scanned At</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                    color:rgba(255,255,255,0.5);margin-top:3px;">{result["timestamp"]}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Diff viewer
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⬡  View Unified Diff", expanded=False):
            st.markdown(diff_viewer(result["diff"]), unsafe_allow_html=True)

        # Verdict box
        if result["verdict"] == "PLAGIARIZED":
            st.error(f"🔴  **PLAGIARISM DETECTED** — Similarity score of {result['score']}% exceeds the {sensitivity}% threshold. This submission is flagged for review.")
        elif result["verdict"] == "SUSPICIOUS":
            st.warning(f"🟡  **SUSPICIOUS SIMILARITY** — Score of {result['score']}% is noteworthy but below the flag threshold. Manual review recommended.")
        else:
            st.success(f"🟢  **LIKELY ORIGINAL** — Similarity score of {result['score']}% is within acceptable limits.")


# ─────────────────────────────────────────────
#  PAGE — HISTORY
# ─────────────────────────────────────────────
def page_history():
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;margin:0;">
        Scan History
      </h1>
      <p style="color:rgba(255,255,255,0.35);font-size:13px;font-family:'DM Sans',sans-serif;margin-top:6px;">
        All previous plagiarism detection scans.
      </p>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state["history"]
    if not history:
        st.markdown("""<div style="text-align:center;padding:60px 0;">
          <div style="font-size:40px;margin-bottom:12px;">◎</div>
          <div style="font-family:'Syne',sans-serif;font-size:16px;color:rgba(255,255,255,0.3);">
            No scans yet. Run an analysis to get started.
          </div>
        </div>""", unsafe_allow_html=True)
        return

    hc1, hc2 = st.columns([4, 1])
    with hc2:
        if st.button("🗑  Clear History"):
            st.session_state["history"] = []
            st.rerun()

    for i, entry in enumerate(history):
        v_color = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(entry["verdict"], "#7c6dfa")
        bar_w = entry["score"]
        st.markdown(f"""
        <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);border-radius:14px;
          padding:18px 22px;margin-bottom:10px;position:relative;overflow:hidden;">
          <div style="position:absolute;bottom:0;left:0;height:2px;width:{bar_w}%;background:{v_color};
            opacity:0.6;border-radius:0 0 2px 2px;"></div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div style="flex:1;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                {badge(entry['verdict'], v_color)}
                {badge(entry.get('lang','Python'), '#60a5fa')}
                <span style="font-size:10px;color:rgba(255,255,255,0.25);font-family:'JetBrains Mono',monospace;">
                  {entry['timestamp']}
                </span>
              </div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:11.5px;
                color:rgba(255,255,255,0.4);margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:85%;">
                A: {entry.get('code_a_preview','')[:80]}…
              </div>
            </div>
            <div style="text-align:right;min-width:70px;">
              <div style="font-family:'Syne',sans-serif;font-size:26px;font-weight:800;color:{v_color};">
                {entry['score']}%
              </div>
              <div style="font-size:10px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;">
                similarity
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE — ANALYTICS
# ─────────────────────────────────────────────
def page_analytics():
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;margin:0;">
        Analytics
      </h1>
      <p style="color:rgba(255,255,255,0.35);font-size:13px;font-family:'DM Sans',sans-serif;margin-top:6px;">
        Visual insights across all your scans.
      </p>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state["history"]
    if len(history) < 2:
        st.info("Run at least 2 scans to see analytics.")
        return

    scores   = [h["score"] for h in history]
    verdicts = [h["verdict"] for h in history]
    total    = len(history)
    plag     = verdicts.count("PLAGIARIZED")
    susp     = verdicts.count("SUSPICIOUS")
    orig     = verdicts.count("ORIGINAL")
    avg_sc   = round(sum(scores) / total, 1)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Scans",    total)
    m2.metric("Plagiarized",    plag, f"{round(plag/total*100)}%")
    m3.metric("Suspicious",     susp, f"{round(susp/total*100)}%")
    m4.metric("Avg Similarity", f"{avg_sc}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Distribution
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:700;
        color:#e8e8f0;margin-bottom:14px;">Score Distribution</div>""", unsafe_allow_html=True)

    buckets = defaultdict(int)
    for s in scores:
        b = int(s // 10) * 10
        buckets[b] += 1
    max_count = max(buckets.values()) if buckets else 1

    bar_html = '<div style="display:flex;gap:6px;align-items:flex-end;height:120px;background:#18181e;border-radius:12px;padding:16px;">'
    for b in range(0, 101, 10):
        cnt   = buckets.get(b, 0)
        h_pct = int(cnt / max_count * 100) if max_count else 0
        color = "#f87171" if b >= 70 else ("#fbbf24" if b >= 40 else "#34d399")
        bar_html += f"""
        <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;justify-content:flex-end;height:100%;">
          <div style="font-size:9px;color:rgba(255,255,255,0.3);font-family:'JetBrains Mono',monospace;">{cnt}</div>
          <div style="width:100%;height:{max(h_pct,2)}%;background:{color};border-radius:3px 3px 0 0;
            box-shadow:0 0 8px {color}44;min-height:2px;transition:height .5s ease;"></div>
          <div style="font-size:9px;color:rgba(255,255,255,0.25);font-family:'DM Sans',sans-serif;">{b}</div>
        </div>"""
    bar_html += "</div>"
    st.markdown(bar_html, unsafe_allow_html=True)

    # Verdict breakdown
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:700;
        color:#e8e8f0;margin-bottom:14px;">Verdict Breakdown</div>""", unsafe_allow_html=True)

    total_v = total or 1
    vd_html = '<div style="display:flex;gap:10px;">'
    for label, count, color in [("Plagiarized", plag, "#f87171"), ("Suspicious", susp, "#fbbf24"), ("Original", orig, "#34d399")]:
        pct = round(count / total_v * 100)
        vd_html += f"""
        <div style="flex:1;background:#18181e;border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:16px 18px;">
          <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:{color};">{count}</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.4);font-family:'DM Sans',sans-serif;margin-top:2px;">{label}</div>
          <div style="height:4px;background:rgba(255,255,255,0.06);border-radius:2px;margin-top:10px;">
            <div style="height:100%;width:{pct}%;background:{color};border-radius:2px;box-shadow:0 0 6px {color}66;"></div>
          </div>
          <div style="font-size:10px;color:{color};margin-top:4px;font-family:'JetBrains Mono',monospace;">{pct}%</div>
        </div>"""
    vd_html += "</div>"
    st.markdown(vd_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE — BATCH
# ─────────────────────────────────────────────
def page_batch():
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;margin:0;">
        Batch Analysis
      </h1>
      <p style="color:rgba(255,255,255,0.35);font-size:13px;font-family:'DM Sans',sans-serif;margin-top:6px;">
        Upload multiple files and detect cross-submission plagiarism.
      </p>
    </div>
    """, unsafe_allow_html=True)

    s = st.session_state["settings"]
    b1, b2, b3 = st.columns(3)
    with b1:
        lang_b = st.selectbox("Language", ["Python","Java","C++","C","JavaScript","Other"], key="batch_lang")
    with b2:
        sens_b = st.slider("Threshold", 40, 95, s["sensitivity"], 5, key="batch_sens")
    with b3:
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload code files (select multiple)",
        type=["py","java","cpp","c","js","txt"],
        accept_multiple_files=True,
        key="batch_files"
    )

    if uploaded and len(uploaded) >= 2:
        st.markdown(f"""<div style="margin:8px 0 16px;">
          {badge(f"{len(uploaded)} files loaded", '#34d399')}
        </div>""", unsafe_allow_html=True)

        if st.button("⬡  Run Batch Analysis", key="batch_run"):
            codes = {}
            for f in uploaded:
                codes[f.name] = f.read().decode("utf-8", errors="replace")

            names = list(codes.keys())
            pairs = [(names[i], names[j]) for i in range(len(names)) for j in range(i+1, len(names))]

            results = []
            prog = st.progress(0)
            for idx, (na, nb) in enumerate(pairs):
                r = detect_plagiarism(codes[na], codes[nb], s["method"], sens_b, lang_b)
                results.append((na, nb, r))
                prog.progress((idx+1)/len(pairs))
                time.sleep(0.05)

            results.sort(key=lambda x: x[2]["score"], reverse=True)
            st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:16px 0;"></div>', unsafe_allow_html=True)
            st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;
                color:#e8e8f0;margin-bottom:14px;">Results</div>""", unsafe_allow_html=True)

            for na, nb, r in results:
                v_color = {"PLAGIARIZED":"#f87171","SUSPICIOUS":"#fbbf24","ORIGINAL":"#34d399"}.get(r["verdict"],"#7c6dfa")
                st.markdown(f"""
                <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);
                  border-left:3px solid {v_color};border-radius:10px;
                  padding:14px 18px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                  <div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#e8e8f0;">
                      {na}  <span style="color:rgba(255,255,255,0.25);">vs</span>  {nb}
                    </div>
                    <div style="margin-top:6px;">{badge(r['verdict'], v_color)}</div>
                  </div>
                  <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:{v_color};">
                    {r['score']}%
                  </div>
                </div>
                """, unsafe_allow_html=True)
    elif uploaded and len(uploaded) == 1:
        st.warning("Please upload at least 2 files for comparison.")
    else:
        st.markdown("""
        <div style="background:#18181e;border:1px dashed rgba(255,255,255,0.1);
          border-radius:14px;padding:40px;text-align:center;">
          <div style="font-size:32px;margin-bottom:10px;opacity:.4;">⊞</div>
          <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:rgba(255,255,255,0.3);">
            Upload 2 or more code files to compare all pairs simultaneously
          </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE — SETTINGS
# ─────────────────────────────────────────────
def page_settings():
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;margin:0;">
        Settings
      </h1>
      <p style="color:rgba(255,255,255,0.35);font-size:13px;font-family:'DM Sans',sans-serif;margin-top:6px;">
        Configure detection parameters and preferences.
      </p>
    </div>
    """, unsafe_allow_html=True)

    s = st.session_state["settings"]

    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;
        color:rgba(255,255,255,0.5);letter-spacing:.8px;text-transform:uppercase;margin-bottom:12px;">
        Detection Defaults</div>""", unsafe_allow_html=True)

    sc1, sc2 = st.columns(2)
    with sc1:
        new_lang = st.selectbox("Default Language", ["Python","Java","C++","C","JavaScript","Other"],
                                index=["Python","Java","C++","C","JavaScript","Other"].index(s["language"]))
        new_method = st.selectbox("Default Method", ["Hybrid (AST + Token)","Token Only","Sequence"],
                                  index=["Hybrid (AST + Token)","Token Only","Sequence"].index(s["method"]))
    with sc2:
        new_sens = st.slider("Default Sensitivity", 40, 95, s["sensitivity"], 5)
        new_save = st.checkbox("Auto-save scan history", value=s["save_history"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;
        color:rgba(255,255,255,0.5);letter-spacing:.8px;text-transform:uppercase;margin-bottom:12px;">
        Danger Zone</div>""", unsafe_allow_html=True)

    dc1, dc2 = st.columns(2)
    with dc1:
        if st.button("🗑  Clear All History"):
            st.session_state["history"] = []
            st.success("History cleared.")
    with dc2:
        if st.button("↺  Reset to Defaults"):
            st.session_state["settings"] = {
                "sensitivity":70,"language":"Python",
                "method":"Hybrid (AST + Token)","theme":"Dark","save_history":True,
            }
            st.rerun()

    if st.button("💾  Save Settings", key="save_settings"):
        st.session_state["settings"].update({
            "language": new_lang, "method": new_method,
            "sensitivity": new_sens, "save_history": new_save,
        })
        st.success("Settings saved successfully.")


# ─────────────────────────────────────────────
#  PAGE — ABOUT
# ─────────────────────────────────────────────
def page_about():
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;margin:0;">
        About CodeScan
      </h1>
    </div>

    <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:28px 32px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;">
        <div style="width:44px;height:44px;background:linear-gradient(135deg,#7c6dfa,#a78bfa);
          border-radius:12px;display:flex;align-items:center;justify-content:center;
          font-size:20px;box-shadow:0 4px 20px rgba(124,109,250,.4);">⬡</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:#e8e8f0;">CodeScan</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;letter-spacing:1px;">
            AI-Powered Code Plagiarism Detector
          </div>
        </div>
      </div>
      <p style="font-family:'DM Sans',sans-serif;font-size:13.5px;color:rgba(255,255,255,0.55);line-height:1.75;">
        CodeScan is a final-semester AI project focused on detecting similarity and potential plagiarism in
        source code submissions. It combines multiple detection techniques — sequence alignment, token-based
        Jaccard similarity, n-gram fingerprinting, and AST structural analysis — to produce a reliable,
        multi-dimensional plagiarism score.
      </p>
    </div>

    <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 32px;margin-bottom:16px;">
      <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:#e8e8f0;margin-bottom:16px;">
        Detection Techniques
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        <div style="background:rgba(124,109,250,0.08);border:1px solid rgba(124,109,250,0.2);
          border-radius:10px;padding:14px 16px;">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:#a78bfa;margin-bottom:4px;">
            Sequence Alignment
          </div>
          <div style="font-size:12px;color:rgba(255,255,255,0.4);font-family:'DM Sans',sans-serif;line-height:1.6;">
            Uses Python's SequenceMatcher to compare normalized code character-by-character.
          </div>
        </div>
        <div style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);
          border-radius:10px;padding:14px 16px;">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:#34d399;margin-bottom:4px;">
            Token Jaccard
          </div>
          <div style="font-size:12px;color:rgba(255,255,255,0.4);font-family:'DM Sans',sans-serif;line-height:1.6;">
            Tokenizes code and computes the Jaccard index over token vocabulary sets.
          </div>
        </div>
        <div style="background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);
          border-radius:10px;padding:14px 16px;">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:#60a5fa;margin-bottom:4px;">
            N-gram Fingerprinting
          </div>
          <div style="font-size:12px;color:rgba(255,255,255,0.4);font-family:'DM Sans',sans-serif;line-height:1.6;">
            Extracts 4-gram token sequences and computes set similarity to catch reordering.
          </div>
        </div>
        <div style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.2);
          border-radius:10px;padding:14px 16px;">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:#fbbf24;margin-bottom:4px;">
            AST Structural Analysis
          </div>
          <div style="font-size:12px;color:rgba(255,255,255,0.4);font-family:'DM Sans',sans-serif;line-height:1.6;">
            Parses Python AST and compares node-type distributions to detect structural plagiarism.
          </div>
        </div>
      </div>
    </div>

    <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:20px 28px;">
      <div style="display:flex;flex-wrap:wrap;gap:8px;">
        <span style="font-size:11px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;
          padding:4px 10px;background:rgba(255,255,255,0.04);border-radius:5px;">Python 3.x</span>
        <span style="font-size:11px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;
          padding:4px 10px;background:rgba(255,255,255,0.04);border-radius:5px;">Streamlit</span>
        <span style="font-size:11px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;
          padding:4px 10px;background:rgba(255,255,255,0.04);border-radius:5px;">difflib</span>
        <span style="font-size:11px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;
          padding:4px 10px;background:rgba(255,255,255,0.04);border-radius:5px;">ast</span>
        <span style="font-size:11px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;
          padding:4px 10px;background:rgba(255,255,255,0.04);border-radius:5px;">hashlib</span>
        <span style="font-size:11px;color:rgba(255,255,255,0.3);font-family:'DM Sans',sans-serif;
          padding:4px 10px;background:rgba(255,255,255,0.04);border-radius:5px;">re</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
page = st.session_state["page"]
if   page == "Analyze":   page_analyze()
elif page == "History":   page_history()
elif page == "Analytics": page_analytics()
elif page == "Batch":     page_batch()
elif page == "Settings":  page_settings()
elif page == "About":     page_about()
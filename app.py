import streamlit as st
import warnings
warnings.filterwarnings('ignore')
import ast
import re
import math
import difflib
import hashlib
import time
import dis
import io
import sys
import itertools
from datetime import datetime
from collections import Counter
from typing import List, Dict, Tuple, Set, Optional


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

from config import init_state, HAS_PLOTLY, HAS_PANDAS
from database import db
from pages.analyze import page_analyze
from pages.history import page_history
from pages.analytics import page_analytics
from pages.batch import page_batch
from pages.settings import page_settings
from pages.about import page_about

# ============================================================
# STREAMLIT PAGE CONFIG - ONLY ONCE!
# ============================================================
st.set_page_config(
    page_title="CodeScan — Ultimate Plagiarism Detector",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<script>
// This will run when the page loads
console.log("CodeScan AI - JavaScript loaded!");

// Function to show a notification
function showNotification(message) {
    alert(message);
}

// Function to update timer display
function updateTimer(seconds) {
    const timerElement = document.getElementById('batch-timer');
    if (timerElement) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        timerElement.innerHTML = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

// Function to play sound when analysis completes
function playCompletionSound() {
    const audio = new Audio('data:audio/wav;base64,U3RlYWx0aCBpcyBhIHN0ZWFsdGggc291bmQ=');
    audio.play().catch(e => console.log('Audio not supported'));
}

// Function to show countdown
function startCountdown(seconds, elementId) {
    let remaining = seconds;
    const timer = setInterval(() => {
        if (remaining <= 0) {
            clearInterval(timer);
            const el = document.getElementById(elementId);
            if (el) el.innerHTML = "✅ Done!";
        } else {
            const el = document.getElementById(elementId);
            if (el) {
                const mins = Math.floor(remaining / 60);
                const secs = remaining % 60;
                el.innerHTML = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
            remaining--;
        }
    }, 1000);
}
</script>

<style>
/* Add any custom CSS here */
.countdown-timer {
    font-family: 'Syne', sans-serif;
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, var(--accent)15, var(--accent2)08);
    border-radius: 16px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HIDE DEFAULT STREAMLIT NAVIGATION
# ============================================================
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
header { display: none !important; }
button[kind="header"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
init_state()

# ── Theme toggle state ──────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"   # default dark

is_dark = st.session_state["theme"] == "dark"

# ============================================================
# THEME TOKENS
# ============================================================
if is_dark:
    # ── DARK ────────────────────────────────────────────────
    css_vars = """
  --bg:        #04070d;
  --bg2:       #060b14;
  --surface:   rgba(8,16,26,0.72);
  --surface2:  rgba(10,20,32,0.66);
  --surface3:  rgba(14,28,42,0.78);
  --border:    rgba(34,211,238,0.14);
  --border2:   rgba(34,211,238,0.28);
  --accent:    #22d3ee;
  --accent2:   #2dffb3;
  --neon:      #22d3ee;
  --neon2:     #00ff9c;
  --neon3:     #ff2d78;
  --green:     #00ff9c;
  --red:       #ff3b5c;
  --amber:     #ffb627;
  --text:      #d7f7ff;
  --text2:     #8fb6c4;
  --muted:     #5d8294;
  --muted2:    #2c4654;
  --shadow:    rgba(0,0,0,0.6);
  --logo-glow: rgba(34,211,238,.75);
  --btn-hover-shadow: rgba(34,211,238,.45);
  --primary-btn-hover-shadow: rgba(34,211,238,.6);
  --input-focus-shadow: rgba(34,211,238,.22);
  --tab-shadow: rgba(0,0,0,.5);
  --metric-bg: rgba(8,18,28,0.6);
  --status-bg: rgba(34,211,238,0.06);
  --status-val-scans: #22d3ee;
  --status-val-flagged: #ff3b5c;
  --status-text: rgba(143,182,196,0.7);
  --status-cb: rgba(143,182,196,0.85);
  --status-cb-bg: rgba(34,211,238,0.05);
  --divider: rgba(34,211,238,0.16);
  --nav-label-color: rgba(34,211,238,0.5);
  --forensic-bg: rgba(8,18,28,0.6);
  --forensic-border: rgba(34,211,238,0.16);
  --forensic-sub: rgba(143,182,196,0.7);
  --forensic-chip-bg: rgba(34,211,238,0.05);
  --forensic-chip-border: rgba(34,211,238,0.18);
  --forensic-chip-lbl: rgba(143,182,196,0.7);
  --forensic-empty-color: rgba(143,182,196,0.5);
  --insight-bg1: rgba(34,211,238,0.10);
  --insight-bg2: rgba(0,255,156,0.04);
  --insight-border: rgba(34,211,238,0.30);
  --insight-title: #22d3ee;
  --insight-body: rgba(215,247,255,0.75);
  --glass-blur: 16px;
  --glass-hi: rgba(34,211,238,0.18);
  --glass-shadow: 0 0 0 1px rgba(34,211,238,0.05), 0 8px 30px rgba(0,0,0,0.5), inset 0 1px 0 rgba(34,211,238,0.10);
  --neon-glow: 0 0 8px rgba(34,211,238,.6), 0 0 22px rgba(34,211,238,.25);
  --grid1: rgba(34,211,238,0.06);
  --grid2: rgba(0,255,156,0.05);
  --aurora-opacity: 1;
"""
    toggle_icon = "☀️"
    toggle_label = "Light Mode"
    toggle_bg = "rgba(34,211,238,0.08)"
    toggle_hover_bg = "rgba(34,211,238,0.16)"
    toggle_color = "#d7f7ff"
    logo_name_color = "#d7f7ff"
    logo_sub_color = "rgba(34,211,238,0.7)"
    sidebar_bg_inline = "#060b14"

else:
    # ── LIGHT ───────────────────────────────────────────────
    css_vars = """
  --bg:        #eef0f7;
  --surface:   rgba(255,255,255,0.65);
  --surface2:  rgba(255,255,255,0.50);
  --surface3:  rgba(255,255,255,0.75);
  --border:    rgba(0,0,0,0.07);
  --border2:   rgba(0,0,0,0.11);
  --accent:    #6c5ce7;
  --accent2:   #a78bfa;
  --green:     #059669;
  --red:       #dc2626;
  --amber:     #d97706;
  --text:      #1a1a2e;
  --text2:     #3a3a5c;
  --muted:     #7070a0;
  --muted2:    #b0b0cc;
  --shadow:    rgba(0,0,0,0.10);
  --logo-glow: rgba(108,92,231,.30);
  --btn-hover-shadow: rgba(108,92,231,.25);
  --primary-btn-hover-shadow: rgba(108,92,231,.4);
  --input-focus-shadow: rgba(108,92,231,.12);
  --tab-shadow: rgba(0,0,0,.10);
  --metric-bg: rgba(255,255,255,0.55);
  --status-bg: rgba(255,255,255,0.55);
  --status-val-scans: #6c5ce7;
  --status-val-flagged: #dc2626;
  --status-text: rgba(0,0,0,0.45);
  --status-cb: rgba(0,0,0,0.45);
  --status-cb-bg: rgba(255,255,255,0.45);
  --divider: rgba(0,0,0,0.08);
  --nav-label-color: rgba(0,0,0,0.35);
  --forensic-bg: rgba(255,255,255,0.55);
  --forensic-border: rgba(0,0,0,0.07);
  --forensic-sub: rgba(0,0,0,0.40);
  --forensic-chip-bg: rgba(255,255,255,0.55);
  --forensic-chip-border: rgba(0,0,0,0.08);
  --forensic-chip-lbl: rgba(0,0,0,0.40);
  --forensic-empty-color: rgba(0,0,0,0.28);
  --insight-bg1: rgba(108,92,231,0.10);
  --insight-bg2: rgba(167,139,250,0.05);
  --insight-border: rgba(108,92,231,0.22);
  --insight-title: #6c5ce7;
  --insight-body: rgba(0,0,0,0.60);
  --glass-blur: 22px;
  --glass-hi: rgba(255,255,255,0.65);
  --glass-shadow: 0 8px 32px rgba(80,80,140,0.12), inset 0 1px 0 rgba(255,255,255,0.6);
  --bg2:       #e3e6f2;
  --neon:      #6c5ce7;
  --neon2:     #0ea5e9;
  --neon3:     #ec4899;
  --neon-glow: 0 0 6px rgba(108,92,231,.35);
  --grid1:     rgba(108,92,231,0.07);
  --grid2:     rgba(14,165,233,0.05);
  --aurora1: rgba(124,109,250,0.28);
  --aurora2: rgba(236,72,153,0.16);
  --aurora3: rgba(52,211,153,0.14);
  --aurora4: rgba(6,182,212,0.16);
  --aurora-opacity: 0.85;
"""
    toggle_icon = "🌙"
    toggle_label = "Dark Mode"
    toggle_bg = "rgba(0,0,0,0.06)"
    toggle_hover_bg = "rgba(0,0,0,0.12)"
    toggle_color = "#1a1a2e"
    logo_name_color = "#1a1a2e"
    logo_sub_color = "rgba(0,0,0,0.40)"
    sidebar_bg_inline = "#ffffff"


# ============================================================
# GLOBAL CSS
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600;700&family=Share+Tech+Mono&family=Orbitron:wght@500;600;700;800&family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
{css_vars}
  --font-head: 'Orbitron', 'Chakra Petch', sans-serif;
  --font-body: 'Chakra Petch', 'JetBrains Mono', monospace;
  --font-mono: 'JetBrains Mono', monospace;
  --font-term: 'Share Tech Mono', monospace;
}}

/* ── App shell ── */
.stApp {{ background: var(--bg) !important; font-family: var(--font-body); color: var(--text); transition: background .25s, color .25s; }}
.stApp > header {{ background: transparent !important; }}
#MainMenu, footer, .stDeployButton {{ display: none !important; }}

/* ── Neon perspective grid + radial vignette ── */
.stApp::before {{
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 70% 55% at 50% 0%, rgba(34,211,238,0.10), transparent 60%),
    radial-gradient(ellipse 60% 50% at 100% 100%, rgba(0,255,156,0.07), transparent 55%),
    radial-gradient(ellipse 60% 50% at 0% 100%, rgba(255,45,120,0.05), transparent 55%),
    linear-gradient(var(--grid1) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid1) 1px, transparent 1px),
    var(--bg);
  background-size: 100% 100%, 100% 100%, 100% 100%, 44px 44px, 44px 44px, 100% 100%;
  animation: gridDrift 18s linear infinite;
}}
/* CRT scanlines + sweeping scan beam */
.stApp::after {{
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    repeating-linear-gradient(0deg, rgba(0,0,0,0.18) 0px, rgba(0,0,0,0.18) 1px, transparent 1px, transparent 3px),
    linear-gradient(180deg, transparent 0%, rgba(34,211,238,0.06) 50%, transparent 100%);
  background-size: 100% 3px, 100% 220px;
  background-repeat: repeat, no-repeat;
  mix-blend-mode: screen;
  opacity: .55;
  animation: scanBeam 7s linear infinite;
}}
@keyframes gridDrift {{
  0%   {{ background-position: 0 0, 0 0, 0 0, 0 0, 0 0, 0 0; }}
  100% {{ background-position: 0 0, 0 0, 0 0, 0 44px, 44px 0, 0 0; }}
}}
@keyframes scanBeam {{
  0%   {{ background-position: 0 0, 0 -240px; }}
  100% {{ background-position: 0 0, 0 110vh; }}
}}
/* keep all real content above background layers */
[data-testid="stSidebar"], section.main, .block-container, [data-testid="stAppViewContainer"] > .main {{
  position: relative;
  z-index: 1;
}}
.block-container {{ padding-top: 2.2rem !important; }}

/* selection */
::selection {{ background: rgba(34,211,238,0.30); color: #fff; }}

/* ── Sidebar (HUD console) ── */
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, rgba(6,12,20,0.92), rgba(4,8,14,0.96)) !important;
  border-right: 1px solid var(--border2) !important;
  backdrop-filter: blur(18px) saturate(150%) !important;
  -webkit-backdrop-filter: blur(18px) saturate(150%) !important;
  box-shadow: 1px 0 0 var(--border2) inset, 14px 0 50px rgba(0,0,0,.5), 0 0 60px rgba(34,211,238,0.06) inset;
  transition: background .25s;
}}
[data-testid="stSidebar"] > div:first-child {{ padding: 0 !important; }}
section[data-testid="stSidebarContent"] {{ padding: 0 !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: linear-gradient(var(--accent), var(--accent2)); border-radius: 10px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent2); }}

/* ── Buttons (neon HUD) ── */
.stButton > button {{
  position: relative;
  overflow: hidden;
  font-family: var(--font-body) !important;
  font-size: 12.5px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  background: rgba(34,211,238,0.04) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 4px !important;
  padding: 9px 18px !important;
  transition: all .2s cubic-bezier(.4,.1,.2,1) !important;
  letter-spacing: 1px !important;
  box-shadow: inset 0 0 0 1px rgba(34,211,238,0.04) !important;
}}
/* neon sheen swipe on hover */
.stButton > button::after {{
  content: "";
  position: absolute;
  top: 0; left: -120%;
  width: 60%; height: 100%;
  background: linear-gradient(100deg, transparent, rgba(34,211,238,.35), transparent);
  transform: skewX(-18deg);
  transition: left .6s ease;
}}
.stButton > button:hover {{
  background: rgba(34,211,238,0.12) !important;
  border-color: var(--accent) !important;
  color: #eafdff !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 0 16px var(--btn-hover-shadow), inset 0 0 12px rgba(34,211,238,0.15), 0 0 0 1px var(--accent) !important;
  text-shadow: 0 0 8px rgba(34,211,238,.7) !important;
}}
.stButton > button:hover::after {{ left: 140%; }}
.stButton > button:active {{ transform: translateY(0) scale(.99) !important; }}
.primary-btn button {{
  background: linear-gradient(135deg, rgba(34,211,238,0.22), rgba(0,255,156,0.18)) !important;
  border: 1px solid var(--accent) !important;
  color: #eafdff !important;
  font-size: 13.5px !important;
  font-weight: 700 !important;
  padding: 13px 28px !important;
  letter-spacing: 1.5px !important;
  box-shadow: 0 0 22px var(--primary-btn-hover-shadow), inset 0 0 18px rgba(34,211,238,0.12) !important;
  text-shadow: 0 0 10px rgba(34,211,238,.6) !important;
}}
.primary-btn button:hover {{
  background: linear-gradient(135deg, rgba(34,211,238,0.38), rgba(0,255,156,0.30)) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 0 38px var(--primary-btn-hover-shadow), inset 0 0 26px rgba(34,211,238,0.2) !important;
}}

/* ── Sidebar nav buttons ── */
[data-testid="stSidebar"] .stButton > button {{
  justify-content: flex-start !important;
  text-align: left !important;
  background: transparent !important;
  border-color: transparent !important;
  box-shadow: none !important;
  color: var(--text2) !important;
  font-weight: 500 !important;
  border-radius: 12px !important;
}}
[data-testid="stSidebar"] .stButton > button {{
  border-radius: 4px !important;
  text-transform: none !important;
  letter-spacing: .5px !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  background: rgba(34,211,238,0.08) !important;
  color: var(--text) !important;
  border-color: var(--border2) !important;
  transform: translateX(4px) !important;
  box-shadow: -2px 0 0 var(--accent), 0 0 14px rgba(34,211,238,0.15) !important;
}}
[data-testid="stSidebar"] .stButton > button:hover::after {{ left: -120%; }}
/* active page pill */
.nav-pill {{
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 16px;
  margin: 0 0 4px 0;
  border-radius: 4px;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: .8px;
  text-transform: uppercase;
  color: #eafdff;
  background: linear-gradient(135deg, rgba(34,211,238,0.18), rgba(0,255,156,0.10));
  border: 1px solid var(--accent);
  box-shadow: 0 0 18px var(--btn-hover-shadow), inset 0 0 14px rgba(34,211,238,0.12);
  text-shadow: 0 0 10px rgba(34,211,238,.6);
  position: relative;
  overflow: hidden;
}}
.nav-pill::before {{
  content: "";
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  background: var(--accent2);
  box-shadow: 0 0 14px var(--accent2);
}}

/* ── Inputs (neon HUD) ── */
.stTextArea textarea, .stTextInput input {{
  background: rgba(4,10,18,0.6) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 4px !important;
  color: var(--text) !important;
  font-family: var(--font-mono) !important;
  font-size: 12.5px !important;
  padding: 12px 14px !important;
  transition: border-color .2s, box-shadow .2s !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px var(--input-focus-shadow), 0 0 18px rgba(34,211,238,.18), inset 0 0 14px rgba(34,211,238,.05) !important;
}}
.stTextArea label, .stTextInput label, .stSelectbox label, .stFileUploader label, .stSlider label {{
  color: var(--accent) !important;
  font-size: 10.5px !important;
  font-weight: 600 !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  font-family: var(--font-mono) !important;
}}

/* ── Select (glass) ── */
.stSelectbox > div > div {{
  background: rgba(4,10,18,0.6) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 4px !important;
  color: var(--text) !important;
}}

/* ── File uploader (HUD dropzone) ── */
[data-testid="stFileUploader"] {{
  background: rgba(34,211,238,0.03) !important;
  border: 1.5px dashed var(--border2) !important;
  border-radius: 4px !important;
  padding: 10px !important;
  transition: border-color .2s, box-shadow .2s, transform .2s !important;
}}
[data-testid="stFileUploader"]:hover {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 22px rgba(34,211,238,.18), inset 0 0 18px rgba(34,211,238,0.05) !important;
}}

/* ── Misc ── */
hr {{ border: none; border-top: 1px solid var(--border); margin: 16px 0; }}

/* ── Metrics (HUD panels with corner brackets) ── */
[data-testid="stMetric"] {{
  position: relative;
  background: var(--metric-bg);
  border: 1px solid var(--border2);
  border-radius: 4px;
  padding: 18px 20px;
  box-shadow: var(--glass-shadow);
  transition: transform .2s cubic-bezier(.4,.1,.2,1), box-shadow .2s, border-color .2s;
}}
[data-testid="stMetric"]::before, [data-testid="stMetric"]::after {{
  content: "";
  position: absolute;
  width: 12px; height: 12px;
  pointer-events: none;
  border-color: var(--accent);
  border-style: solid;
}}
[data-testid="stMetric"]::before {{ top: 6px; left: 6px; border-width: 2px 0 0 2px; }}
[data-testid="stMetric"]::after  {{ bottom: 6px; right: 6px; border-width: 0 2px 2px 0; }}
[data-testid="stMetric"]:hover {{
  transform: translateY(-3px);
  border-color: var(--accent);
  box-shadow: 0 0 26px rgba(34,211,238,.18), inset 0 0 18px rgba(34,211,238,.05);
}}
[data-testid="stMetricLabel"] {{ color: var(--accent) !important; font-family: var(--font-mono) !important; font-size: 10.5px !important; text-transform: uppercase; letter-spacing: 1.5px; }}
[data-testid="stMetricValue"] {{ color: var(--text) !important; font-family: var(--font-head) !important; font-size: 28px !important; text-shadow: 0 0 14px rgba(34,211,238,.35); }}

/* ── Expanders (HUD) ── */
.streamlit-expanderHeader, details > summary, [data-testid="stExpander"] summary {{
  background: rgba(34,211,238,0.04) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 4px !important;
  color: var(--text) !important;
  font-family: var(--font-mono) !important;
  font-size: 12.5px !important;
  letter-spacing: .6px !important;
  text-transform: uppercase !important;
}}
[data-testid="stExpander"] {{
  border-radius: 4px !important;
  border: 1px solid var(--border) !important;
  background: var(--surface) !important;
  box-shadow: var(--glass-shadow) !important;
  overflow: hidden;
}}
.streamlit-expanderContent {{
  background: transparent !important;
  border: none !important;
}}

/* ── Tabs (HUD segmented) ── */
.stTabs [data-baseweb="tab-list"] {{
  background: rgba(4,10,18,0.5) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  padding: 4px !important;
  gap: 3px !important;
  border-bottom: 1px solid var(--border) !important;
  box-shadow: var(--glass-shadow) !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  color: var(--muted) !important;
  border-radius: 3px !important;
  font-family: var(--font-mono) !important;
  font-size: 12px !important;
  letter-spacing: .8px !important;
  text-transform: uppercase !important;
  padding: 7px 18px !important;
  border: none !important;
  transition: color .2s, background .2s, box-shadow .2s !important;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: var(--text) !important; }}
.stTabs [aria-selected="true"] {{
  background: linear-gradient(135deg, rgba(34,211,238,0.20), rgba(0,255,156,0.12)) !important;
  color: #eafdff !important;
  box-shadow: inset 0 0 0 1px var(--accent), 0 0 14px var(--btn-hover-shadow) !important;
  text-shadow: 0 0 8px rgba(34,211,238,.6) !important;
}}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ background: transparent !important; }}

/* ── Progress ── */
.stProgress > div > div > div {{
  background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
  border-radius: 2px !important;
  box-shadow: 0 0 12px var(--accent) !important;
}}

/* ── Slider ── */
.stSlider [data-baseweb="slider"] [role="slider"] {{ box-shadow: 0 0 10px var(--accent) !important; }}
.stSlider .rc-slider-track {{ background: var(--accent) !important; }}
.stSlider .rc-slider-handle {{ border-color: var(--accent) !important; background: var(--accent) !important; box-shadow: 0 0 10px var(--accent) !important; }}

/* ── Checkbox / Radio ── */
.stCheckbox label, .stRadio label {{ color: var(--text) !important; font-family: var(--font-body) !important; font-size: 13px !important; }}

/* ── Headings (neon) ── */
h1, h2, h3 {{ font-family: var(--font-head) !important; letter-spacing: .5px !important; }}
h1 {{ text-shadow: 0 0 18px rgba(34,211,238,.35) !important; }}

/* ── Alert (glass) ── */
.stAlert {{
  border-radius: 14px !important;
  font-family: var(--font-body) !important;
  font-size: 13px !important;
  border-left-width: 3px !important;
  backdrop-filter: blur(16px) saturate(150%) !important;
  -webkit-backdrop-filter: blur(16px) saturate(150%) !important;
  box-shadow: var(--glass-shadow) !important;
}}

/* ── Code ── */
code, .stCode {{ font-family: var(--font-mono) !important; font-size: 12px !important; }}

/* ── Spinner ── */
.stSpinner > div {{ border-top-color: var(--accent) !important; }}

/* ── Heatmap ── */
.heatmap-table {{ border-collapse: collapse; font-size: 10px; width: 100%; }}
.heatmap-table th {{ padding: 6px 8px; color: var(--muted); font-weight: 500; }}
.heatmap-table td {{ padding: 8px; text-align: center; font-weight: 700; }}

/* ── Forensic Statistics panel ── */
.forensic-panel {{
  background: var(--forensic-bg);
  border: 1px solid var(--forensic-border);
  border-radius: 20px;
  padding: 28px 28px 20px 28px;
  margin-bottom: 24px;
  backdrop-filter: blur(var(--glass-blur)) saturate(160%);
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(160%);
  box-shadow: var(--glass-shadow);
}}
.forensic-section-title {{
  font-family: 'Syne', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}}
.forensic-section-sub {{
  font-family: 'DM Sans', sans-serif;
  font-size: 12px;
  color: var(--forensic-sub);
  margin-bottom: 20px;
}}
.forensic-insight {{
  background: linear-gradient(135deg, var(--insight-bg1), var(--insight-bg2));
  border: 1px solid var(--insight-border);
  border-left: 3px solid var(--accent);
  border-radius: 10px;
  padding: 14px 18px;
  margin-top: 18px;
}}
.forensic-insight-title {{
  font-family: 'Syne', sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: var(--insight-title);
  margin-bottom: 6px;
  letter-spacing: 0.4px;
}}
.forensic-insight p {{
  font-family: 'DM Sans', sans-serif;
  font-size: 12.5px;
  color: var(--insight-body);
  line-height: 1.7;
  margin: 0;
}}
.forensic-insight p span.highlight   {{ color: var(--red);   font-weight: 600; }}
.forensic-insight p span.highlight-y {{ color: var(--amber); font-weight: 600; }}
.forensic-insight p span.highlight-g {{ color: var(--green); font-weight: 600; }}
.forensic-stat-chips {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }}
.forensic-chip {{
  background: var(--forensic-chip-bg);
  border: 1px solid var(--forensic-chip-border);
  border-radius: 8px;
  padding: 8px 14px;
  text-align: center;
  min-width: 90px;
}}
.forensic-chip-val {{ font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: var(--text); }}
.forensic-chip-lbl {{
  font-family: 'DM Sans', sans-serif;
  font-size: 10px;
  color: var(--forensic-chip-lbl);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-top: 2px;
}}
.forensic-empty {{
  text-align: center;
  padding: 48px 20px;
  color: var(--forensic-empty-color);
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
}}
.forensic-empty .icon {{ font-size: 36px; margin-bottom: 10px; }}

/* ── Theme toggle button ── */
.theme-toggle-btn {{
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: {toggle_bg};
  border: 1px solid var(--border2);
  border-radius: 20px;
  padding: 6px 14px;
  font-family: 'DM Sans', sans-serif;
  font-size: 12px;
  font-weight: 500;
  color: {toggle_color};
  cursor: pointer;
  transition: background .2s, transform .15s;
  letter-spacing: .3px;
  width: 100%;
  justify-content: center;
  margin-bottom: 4px;
}}
.theme-toggle-btn:hover {{
  background: {toggle_hover_bg};
  transform: translateY(-1px);
}}
</style>
""", unsafe_allow_html=True)


# ============================================================
# LIGHT MODE READABILITY OVERRIDES
# (the cyber theme hard-codes light-on-dark colors inline; in light
#  mode we flip near-white text to dark, lighten dark panels, and
#  strip neon glows so everything stays readable.)
# ============================================================
if not is_dark:
    st.markdown("""
<style>
/* near-white inline text -> dark ink */
.stApp [style*="#d7f7ff"], .stApp [style*="#e8e8f0"], .stApp [style*="#eafdff"],
.stApp [style*="#edecf6"] { color:#0f2236 !important; }

/* muted inline text -> readable slate */
.stApp [style*="#9fc4d2"], .stApp [style*="#8fb6c4"], .stApp [style*="#5d8294"],
.stApp [style*="rgba(255,255,255"], .stApp [style*="rgba(143,182,196"] { color:#3a566b !important; }

/* neon accent text -> deep teal / green (keeps brand, gains contrast) */
.stApp [style*="#22d3ee"] { color:#0e7490 !important; }
.stApp [style*="#00ff9c"] { color:#047857 !important; }

/* dark hard-coded panels / code blocks -> light surfaces */
.stApp [style*="rgba(8,18,28"], .stApp [style*="#04080e"], .stApp [style*="#04070d"],
.stApp [style*="#0d0d10"] { background:rgba(255,255,255,0.78) !important; }

/* stylesheet-level dark fills (inputs, selects, tabs) -> light */
.stTextArea textarea, .stTextInput input, .stSelectbox > div > div,
.stTabs [data-baseweb="tab-list"] { background:rgba(255,255,255,0.82) !important; color:#0f2236 !important; }

/* default body / widget text dark */
.stApp, .stMarkdown, .stMarkdown p, .stMarkdown li, label, .stCheckbox label,
.stRadio label, [data-testid="stMetricValue"] { color:#1a1a2e !important; }

/* all headings forced dark regardless of inline color */
.stApp h1, .stApp h2, .stApp h3 { color:#0f2236 !important; }

/* kill neon glows that smear on a light background */
.stApp *, [data-testid="stSidebar"] * { text-shadow:none !important; }

/* soften the neon background wash so text stays high-contrast */
.stApp::before { opacity:.4 !important; }
.stApp::after { opacity:.25 !important; }

/* sidebar console -> light panel */
[data-testid="stSidebar"] {
  background:linear-gradient(180deg, rgba(255,255,255,0.92), rgba(244,246,252,0.96)) !important;
}

/* active nav pill -> dark text on its pale gradient */
.nav-pill { color:#0f2236 !important; background:linear-gradient(135deg, rgba(34,211,238,0.22), rgba(0,255,156,0.14)) !important; }
.nav-pill * { color:#0f2236 !important; }
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

    # Restore persisted training data from the database (survives restarts)
    # and retrain the ML model so its state is not lost between sessions.
    if not st.session_state.get("training_data") and not st.session_state.get("_training_loaded"):
        st.session_state["_training_loaded"] = True
        try:
            from database import db
            from datetime import datetime as _dt
            rows = db.get_training_data()
            if rows:
                st.session_state["training_data"] = [
                    {"features": feats, "label": lbl, "timestamp": _dt.now().isoformat()}
                    for feats, lbl in rows
                ]
                if HAS_SKLEARN and len(rows) >= 10:
                    from engines.ml_classifier import ml_classifier
                    ml_classifier.train(st.session_state["training_data"])
        except Exception:
            pass

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
    # WEIGHTED SCORING (structural & semantic > lexical)
    # ============================================================
    weights = {
        'codebert_sim': 5.0,
        'big_o_match': 5.0,
        'bytecode_sim': 4.0,
        'ast_sim': 3.0,
        'type_agnostic_jac_sim': 2.5,
        'ted_sim': 2.5,
        'cfg_sim': 2.0,
        'type_agnostic_seq_sim': 1.5,
        'winnowing_sim': 0.5,
        'jac_sim': 0.3,
        'seq_sim': 0.2,
        'ngram_sim': 0.2,
    }

    if not active_metrics:
        final_score = 0.0
    else:
        weighted_sum = 0.0
        total_weight = 0.0
        for metric_name, metric_value in active_metrics.items():
            w = weights.get(metric_name, 1.0)
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
  Code Pattern Match:     {result.get('type_agnostic_seq_sim', 0):.1f}%
  Similarity Score: {result.get('type_agnostic_jac_sim', 0):.1f}%
  Tree Edit Distance:    {result.get('ted_sim', 0):.1f}%
  Control Flow Graph:    {result.get('cfg_sim', 0):.1f}%
  Copied Code Detection:      {result.get('winnowing_sim', 0):.1f}%
  Logic Similarity:     {result.get('codebert_sim', 0):.1f}%
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
with st.sidebar:

    # ── Logo ────────────────────────────────────────────────
    st.markdown(f"""
    <style>
      @keyframes logoPulse {{
        0%,100% {{ box-shadow: 0 0 14px var(--logo-glow), inset 0 0 10px rgba(34,211,238,.3); }}
        50%     {{ box-shadow: 0 0 26px var(--logo-glow), inset 0 0 16px rgba(34,211,238,.5); }}
      }}
      @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:.25}} }}
    </style>
    <div style="padding:26px 18px 14px 18px;">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="width:42px;height:42px;background:rgba(34,211,238,0.06);border:1px solid var(--accent);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:20px;color:var(--accent);animation:logoPulse 2.8s ease-in-out infinite;text-shadow:0 0 12px var(--accent);">⬡</div>
        <div>
          <div style="font-family:var(--font-head);font-size:18px;font-weight:800;color:#d7f7ff;letter-spacing:2px;text-shadow:0 0 14px rgba(34,211,238,.6);">CODESCAN</div>
          <div style="font-size:9px;color:var(--accent);font-family:var(--font-mono);letter-spacing:2.5px;text-transform:uppercase;margin-top:2px;">// Forensic Engine</div>
        </div>
      </div>
      <div style="margin-top:14px;font-family:var(--font-term);font-size:9.5px;color:var(--accent2);letter-spacing:.5px;opacity:.8;">> 6 cores online <span style="animation:blink 1s step-end infinite;">_</span></div>
      <div style="height:1px;background:linear-gradient(90deg,var(--accent),transparent);margin-top:14px;box-shadow:0 0 8px var(--accent);"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Nav buttons ─────────────────────────────────────────
    nav_pages = [
        ("⬡", "Analyze"),
        ("📊", "History"),
        ("📈", "Analytics"),
        ("📁", "Batch"),
        ("⚙️", "Settings"),
        ("ℹ️", "About"),
    ]

    current_page = st.session_state.get("page", "Analyze")
    for icon, page_name in nav_pages:
        if page_name == current_page:
            st.markdown(
                f'<div class="nav-pill"><span style="font-size:14px;">{icon}</span>{page_name}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button(f"{icon}  {page_name}", key=f"nav_{page_name}", use_container_width=True):
                st.session_state["page"] = page_name
                st.rerun()

    st.markdown(f'<div style="height:1px;background:var(--divider);margin:16px 0;"></div>', unsafe_allow_html=True)

    # ── Theme Toggle ─────────────────────────────────────────
    if st.button(f"{toggle_icon}  {toggle_label}", key="theme_toggle", use_container_width=True):
        st.session_state["theme"] = "light" if is_dark else "dark"
        st.rerun()

    st.markdown(f'<div style="height:1px;background:var(--divider);margin:12px 0 16px 0;"></div>', unsafe_allow_html=True)

    # ── System Status ────────────────────────────────────────
    n_hist = len(st.session_state["history"])
    flagged = sum(1 for h in st.session_state["history"] if h["verdict"] != "ORIGINAL")

    from engines.codebert_engine import codebert_analyzer
    cb_status = codebert_analyzer.get_status()

    st.markdown(f"""
    <div style="padding:0 14px 20px;">
      <div style="font-size:9px;color:var(--nav-label-color);letter-spacing:2px;text-transform:uppercase;font-family:var(--font-mono);margin-bottom:10px;">▚ System Status</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
        <div style="background:var(--status-bg);border:1px solid var(--border2);border-radius:4px;padding:10px 8px;text-align:center;">
          <div style="font-family:var(--font-head);font-size:20px;font-weight:700;color:var(--status-val-scans);text-shadow:0 0 12px rgba(34,211,238,.5);">{n_hist}</div>
          <div style="font-size:9px;color:var(--status-text);letter-spacing:1.5px;text-transform:uppercase;font-family:var(--font-mono);">Scans</div>
        </div>
        <div style="background:var(--status-bg);border:1px solid var(--border2);border-radius:4px;padding:10px 8px;text-align:center;">
          <div style="font-family:var(--font-head);font-size:20px;font-weight:700;color:var(--status-val-flagged);text-shadow:0 0 12px rgba(255,59,92,.5);">{flagged}</div>
          <div style="font-size:9px;color:var(--status-text);letter-spacing:1.5px;text-transform:uppercase;font-family:var(--font-mono);">Flagged</div>
        </div>
      </div>
      <div style="font-size:9px;color:var(--status-cb);padding:7px 8px;background:var(--status-cb-bg);border:1px solid var(--border);border-radius:4px;word-break:break-word;font-family:var(--font-term);">> {cb_status}</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ROUTER
# ============================================================
page = st.session_state.get("page", "Analyze")

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
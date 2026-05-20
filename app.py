import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

import streamlit as st
import warnings
warnings.filterwarnings('ignore')

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
  --text2:     #b0b0c8;
  --muted:     #6b6b80;
  --muted2:    #4a4a5a;
  --shadow:    rgba(0,0,0,0.5);
  --logo-glow: rgba(124,109,250,.4);
  --btn-hover-shadow: rgba(124,109,250,.35);
  --primary-btn-hover-shadow: rgba(124,109,250,.5);
  --input-focus-shadow: rgba(124,109,250,.15);
  --tab-shadow: rgba(0,0,0,.4);
  --metric-bg: #18181e;
  --status-bg: rgba(255,255,255,0.04);
  --status-val-scans: #a78bfa;
  --status-val-flagged: #f87171;
  --status-text: rgba(255,255,255,0.3);
  --status-cb: rgba(255,255,255,0.4);
  --status-cb-bg: rgba(255,255,255,0.02);
  --divider: rgba(255,255,255,0.06);
  --nav-label-color: rgba(255,255,255,0.25);
  --forensic-bg: #18181e;
  --forensic-border: rgba(255,255,255,0.07);
  --forensic-sub: rgba(255,255,255,0.35);
  --forensic-chip-bg: rgba(255,255,255,0.04);
  --forensic-chip-border: rgba(255,255,255,0.08);
  --forensic-chip-lbl: rgba(255,255,255,0.3);
  --forensic-empty-color: rgba(255,255,255,0.2);
  --insight-bg1: rgba(124,109,250,0.12);
  --insight-bg2: rgba(167,139,250,0.06);
  --insight-border: rgba(124,109,250,0.25);
  --insight-title: #a78bfa;
  --insight-body: rgba(255,255,255,0.6);
"""
    toggle_icon = "☀️"
    toggle_label = "Light Mode"
    toggle_bg = "rgba(255,255,255,0.06)"
    toggle_hover_bg = "rgba(255,255,255,0.12)"
    toggle_color = "#e8e8f0"
    logo_name_color = "#e8e8f0"
    logo_sub_color = "rgba(255,255,255,0.3)"
    sidebar_bg_inline = "#111115"

else:
    # ── LIGHT ───────────────────────────────────────────────
    css_vars = """
  --bg:        #f4f4f8;
  --surface:   #ffffff;
  --surface2:  #f0f0f5;
  --surface3:  #e8e8f0;
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
  --metric-bg: #f0f0f5;
  --status-bg: rgba(0,0,0,0.04);
  --status-val-scans: #6c5ce7;
  --status-val-flagged: #dc2626;
  --status-text: rgba(0,0,0,0.45);
  --status-cb: rgba(0,0,0,0.45);
  --status-cb-bg: rgba(0,0,0,0.03);
  --divider: rgba(0,0,0,0.08);
  --nav-label-color: rgba(0,0,0,0.35);
  --forensic-bg: #f8f8fc;
  --forensic-border: rgba(0,0,0,0.07);
  --forensic-sub: rgba(0,0,0,0.40);
  --forensic-chip-bg: rgba(0,0,0,0.03);
  --forensic-chip-border: rgba(0,0,0,0.08);
  --forensic-chip-lbl: rgba(0,0,0,0.40);
  --forensic-empty-color: rgba(0,0,0,0.28);
  --insight-bg1: rgba(108,92,231,0.08);
  --insight-bg2: rgba(167,139,250,0.04);
  --insight-border: rgba(108,92,231,0.20);
  --insight-title: #6c5ce7;
  --insight-body: rgba(0,0,0,0.60);
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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
{css_vars}
  --font-head: 'Syne', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}}

/* ── App shell ── */
.stApp {{ background: var(--bg) !important; font-family: var(--font-body); color: var(--text); transition: background .25s, color .25s; }}
.stApp > header {{ background: transparent !important; }}
#MainMenu, footer, .stDeployButton {{ display: none !important; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: var(--surface) !important;
  border-right: 1px solid var(--border2) !important;
  transition: background .25s;
}}
[data-testid="stSidebar"] > div:first-child {{ padding: 0 !important; }}
section[data-testid="stSidebarContent"] {{ padding: 0 !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--muted2); border-radius: 10px; }}

/* ── Buttons ── */
.stButton > button {{
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
}}
.stButton > button:hover {{
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 20px var(--btn-hover-shadow) !important;
}}
.primary-btn button {{
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
  font-size: 14px !important;
  padding: 10px 28px !important;
}}
.primary-btn button:hover {{
  background: var(--accent2) !important;
  border-color: var(--accent2) !important;
  box-shadow: 0 6px 28px var(--primary-btn-hover-shadow) !important;
}}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {{
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: var(--font-mono) !important;
  font-size: 12.5px !important;
  padding: 12px 14px !important;
  transition: border-color .2s !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--input-focus-shadow) !important;
}}
.stTextArea label, .stTextInput label, .stSelectbox label, .stFileUploader label {{
  color: var(--muted) !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  letter-spacing: .8px !important;
  text-transform: uppercase !important;
  font-family: var(--font-body) !important;
}}

/* ── Select ── */
.stSelectbox > div > div {{
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
  background: var(--surface2) !important;
  border: 1px dashed var(--border2) !important;
  border-radius: 12px !important;
  padding: 8px !important;
}}
[data-testid="stFileUploader"]:hover {{ border-color: var(--accent) !important; }}

/* ── Misc ── */
hr {{ border: none; border-top: 1px solid var(--border); margin: 16px 0; }}

/* ── Metrics ── */
[data-testid="stMetric"] {{
  background: var(--metric-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
}}
[data-testid="stMetricLabel"] {{ color: var(--muted) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .7px; }}
[data-testid="stMetricValue"] {{ color: var(--text) !important; font-family: var(--font-head) !important; font-size: 28px !important; }}

/* ── Expanders ── */
.streamlit-expanderHeader {{
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: var(--font-body) !important;
  font-size: 13px !important;
}}
.streamlit-expanderContent {{
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 10px 10px !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  background: var(--surface2) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 2px !important;
  border-bottom: none !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  color: var(--muted) !important;
  border-radius: 7px !important;
  font-family: var(--font-body) !important;
  font-size: 13px !important;
  padding: 6px 16px !important;
  border: none !important;
}}
.stTabs [aria-selected="true"] {{
  background: var(--surface3) !important;
  color: var(--text) !important;
  box-shadow: 0 1px 6px var(--tab-shadow) !important;
}}

/* ── Progress ── */
.stProgress > div > div > div {{
  background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
  border-radius: 4px !important;
}}

/* ── Slider ── */
.stSlider .rc-slider-track {{ background: var(--accent) !important; }}
.stSlider .rc-slider-handle {{ border-color: var(--accent) !important; background: var(--accent) !important; }}

/* ── Checkbox / Radio ── */
.stCheckbox label, .stRadio label {{ color: var(--text) !important; font-family: var(--font-body) !important; font-size: 13px !important; }}

/* ── Alert ── */
.stAlert {{ border-radius: 10px !important; font-family: var(--font-body) !important; font-size: 13px !important; border-left-width: 3px !important; }}

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
  border-radius: 16px;
  padding: 28px 28px 20px 28px;
  margin-bottom: 24px;
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
# SIDEBAR
# ============================================================
with st.sidebar:

    # ── Logo ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="padding:28px 20px 18px 20px;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:34px;height:34px;background:linear-gradient(135deg,#7c6dfa,#a78bfa);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:0 4px 16px {logo_sub_color};">⬡</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:{logo_name_color};letter-spacing:.5px;">CodeScan</div>
          <div style="font-size:10px;color:{logo_sub_color};font-family:'DM Sans',sans-serif;letter-spacing:1.2px;text-transform:uppercase;margin-top:1px;">Ultimate Detector</div>
        </div>
      </div>
      <div style="height:1px;background:var(--divider);margin-top:20px;"></div>
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

    for icon, page_name in nav_pages:
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
      <div style="font-size:10px;color:var(--nav-label-color);letter-spacing:1px;text-transform:uppercase;font-family:'DM Sans',sans-serif;margin-bottom:10px;">System Status</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
        <div style="background:var(--status-bg);border:1px solid var(--border);border-radius:8px;padding:10px 8px;text-align:center;">
          <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:var(--status-val-scans);">{n_hist}</div>
          <div style="font-size:10px;color:var(--status-text);">Scans</div>
        </div>
        <div style="background:var(--status-bg);border:1px solid var(--border);border-radius:8px;padding:10px 8px;text-align:center;">
          <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:var(--status-val-flagged);">{flagged}</div>
          <div style="font-size:10px;color:var(--status-text);">Flagged</div>
        </div>
      </div>
      <div style="font-size:9px;color:var(--status-cb);padding:6px;background:var(--status-cb-bg);border-radius:6px;word-break:break-word;">{cb_status}</div>
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
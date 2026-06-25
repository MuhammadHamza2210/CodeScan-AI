import streamlit as st
from config import HAS_ZSS, HAS_SKLEARN, HAS_PLOTLY, HAS_PANDAS
from engines.codebert_engine import codebert_analyzer

def page_about():
    st.markdown("""
    <div style="padding:6px 0 22px 0;">
      <div style="font-size:10px;color:#22d3ee;letter-spacing:3px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;margin-bottom:8px;">// System Info</div>
      <h1 style="font-family:'Orbitron',sans-serif;font-size:32px;font-weight:800;color:#d7f7ff;letter-spacing:2px;text-shadow:0 0 20px rgba(34,211,238,.45);">ABOUT</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(8,18,28,0.6);border:1px solid rgba(34,211,238,0.16);border-radius:4px;padding:26px;box-shadow:0 0 0 1px rgba(34,211,238,0.04), inset 0 0 24px rgba(34,211,238,0.03);font-family:'JetBrains Mono',monospace;">
        <h3 style="color:#22d3ee;font-family:'Orbitron',sans-serif;letter-spacing:1px;text-shadow:0 0 14px rgba(34,211,238,.4);">CodeScan AI — Ultimate Edition v8.0</h3>
        <p style="color:#8fb6c4;margin-top:6px;">> 6 Detection Engines · 92%+ Accuracy</p>
        <p style="color:#5d8294;font-size:12px;">Decision Tree · Tree Edit Distance · Deepened CFG · Winnowing · CodeBERT · Type-Agnostic</p>
        <hr style="margin:18px 0;border-color:rgba(34,211,238,0.14);">
        <h4 style="color:#00ff9c;font-family:'Orbitron',sans-serif;letter-spacing:1px;text-shadow:0 0 12px rgba(0,255,156,.35);">⊹ New Enhancements</h4>
        <ul style="color:#8fb6c4;font-size:12px;line-height:1.9;margin-top:8px;">
            <li><strong style="color:#d7f7ff;">Deepened CFG</strong> — tracks Try/Except blocks and Function Calls</li>
            <li><strong style="color:#d7f7ff;">Enhanced Type-Agnostic</strong> — Role-based naming (ARG_, LOCAL_, VAR_)</li>
            <li><strong style="color:#d7f7ff;">Forensic Statistics</strong> — OLS scatter, distribution histograms, engine spread box plots</li>
        </ul>
        <hr style="margin:18px 0;border-color:rgba(34,211,238,0.14);">
        <p style="color:#5d8294;font-size:12px;">> CodeBERT: {codebert_analyzer.get_status()}</p>
        <p style="color:#5d8294;font-size:12px;">> Tree Edit Distance: {"● Available" if HAS_ZSS else "○ Not installed"}</p>
        <p style="color:#5d8294;font-size:12px;">> ML Classifier: {"● Available" if HAS_SKLEARN else "○ Not installed"}</p>
        <p style="color:#5d8294;font-size:12px;">> Plotly / Pandas: {"● Available" if (HAS_PLOTLY and HAS_PANDAS) else "○ Install plotly pandas"}</p>
    </div>
    """, unsafe_allow_html=True)

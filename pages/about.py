import streamlit as st
from config import HAS_ZSS, HAS_SKLEARN, HAS_PLOTLY, HAS_PANDAS
from engines.codebert_engine import codebert_analyzer

def page_about():
    st.markdown("""<div style="padding:8px 0 24px 0;"><h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;">About</h1></div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px;">
        <h3 style="color:#a78bfa;">CodeScan AI Ultimate Edition v8.0</h3>
        <p style="color:#888;">6 Detection Engines for 92%+ Accuracy</p>
        <p style="color:#666;">Decision Tree • Tree Edit Distance • Deepened CFG • Winnowing • CodeBERT • Type-Agnostic (Role-based)</p>
        <hr style="margin:16px 0;">
        <h4 style="color:#a78bfa;">✨ New Enhancements</h4>
        <ul style="color:#888;font-size:12px;">
            <li><strong>Deepened CFG</strong> - Now tracks Try/Except blocks and Function Calls</li>
            <li><strong>Enhanced Type-Agnostic</strong> - Role-based naming (ARG_, LOCAL_, VAR_)</li>
            <li><strong>Forensic Statistics</strong> - OLS scatter, distribution histograms, engine spread box plots</li>
        </ul>
        <hr style="margin:16px 0;">
        <p style="color:#666;font-size:12px;">CodeBERT: {codebert_analyzer.get_status()}</p>
        <p style="color:#666;font-size:12px;">Tree Edit Distance: {"✅ Available" if HAS_ZSS else "❌ Not installed"}</p>
        <p style="color:#666;font-size:12px;">ML Classifier: {"✅ Available" if HAS_SKLEARN else "❌ Not installed"}</p>
        <p style="color:#666;font-size:12px;">Plotly / Pandas: {"✅ Available" if (HAS_PLOTLY and HAS_PANDAS) else "❌ Install plotly pandas"}</p>
    </div>
    """, unsafe_allow_html=True) 

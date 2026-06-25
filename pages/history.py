import streamlit as st
import pandas as pd
from ui_components import badge
from database import db

def safe_float(value, default=0.0):
    """Safely convert any value to float"""
    try:
        if isinstance(value, bytes):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def page_history():
    st.markdown("""
    <div style="padding:6px 0 22px 0;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#00ff9c;box-shadow:0 0 10px #00ff9c;"></span>
        <span style="font-size:10px;color:#22d3ee;letter-spacing:3px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">// Scan Archive</span>
      </div>
      <h1 style="font-family:'Orbitron',sans-serif;font-size:34px;font-weight:800;color:#d7f7ff;margin:0;line-height:1.15;letter-spacing:2px;text-shadow:0 0 22px rgba(34,211,238,.45);">SCAN HISTORY</h1>
      <p style="color:rgba(143,182,196,0.7);font-size:12px;font-family:'JetBrains Mono',monospace;margin-top:8px;letter-spacing:.5px;">> persistent forensic log · sqlite-backed</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load from database
    df = db.get_all_scans()
    
    if df.empty:
        st.info("No scans yet. Run some analyses to see history here!")
        return
    
    # Clear button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Clear All History", use_container_width=True):
            db.clear_history()
            st.session_state["history"] = []
            st.rerun()
    
    # Display statistics
    stats = db.get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Scans", stats['total_scans'])
    with col2:
        st.metric("Plagiarized", stats['plagiarized'], delta="⚠️")
    with col3:
        st.metric("Original", stats['original'], delta="✅")
    with col4:
        st.metric("Avg Score", f"{safe_float(stats['avg_score'])}%")
    
    st.markdown("---")
    
    # Display history
    for _, row in df.iterrows():
        vc = {"PLAGIARIZED": "#ff3b5c", "SUSPICIOUS": "#ffb627", "ORIGINAL": "#00ff9c"}.get(row['verdict'], "#22d3ee")
        
        # Safely get values
        score_val = safe_float(row['score'])
        cb_val = safe_float(row['codebert_sim'])
        ast_val = safe_float(row['ast_sim'])
        win_val = safe_float(row['winnowing_sim'])
        cfg_val = safe_float(row['cfg_sim'])
        engines_val = safe_float(row['engines_used'], default=0)
        
        with st.expander(f"📊 {str(row['timestamp'])[:19]} - Score: {score_val:.1f}% - {row['verdict']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Files:** {row['code_a_name']} vs {row['code_b_name']}")
                st.markdown(f"**Language:** {row['language']}")
                st.markdown(f"**Engines Used:** {engines_val:.0f}")
                st.markdown(f"**Risk Level:** {row['risk']}")
            with col2:
                st.markdown(f"**CodeBERT:** {cb_val:.1f}%")
                st.markdown(f"**AST Similarity:** {ast_val:.1f}%")
                st.markdown(f"**Winnowing:** {win_val:.1f}%")
                st.markdown(f"**CFG:** {cfg_val:.1f}%")
            
            # Preview of code
            if row['code_a_preview'] and row['code_b_preview']:
                st.markdown("---")
                st.markdown("**📝 Code Preview:**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.code(str(row['code_a_preview'])[:500], language="python")
                with col_b:
                    st.code(str(row['code_b_preview'])[:500], language="python")
            
            # Delete button
            if st.button(f"🗑️ Delete", key=f"del_{row['id']}"):
                db.delete_scan(row['id'])
                st.rerun()
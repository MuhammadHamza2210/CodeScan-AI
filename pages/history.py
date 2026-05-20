import streamlit as st
import pandas as pd
from ui_components import badge
from database import db

def page_history():
    st.markdown("""<div style="padding:8px 0 24px 0;"><h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;">Scan History</h1></div>""", unsafe_allow_html=True)
    
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
        st.metric("Avg Score", f"{stats['avg_score']}%")
    
    st.markdown("---")
    
    # Display history
    for _, row in df.iterrows():
        vc = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(row['verdict'], "#7c6dfa")
        
        with st.expander(f"📊 {row['timestamp'][:19]} - Score: {row['score']:.1f}% - {row['verdict']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Files:** {row['code_a_name']} vs {row['code_b_name']}")
                st.markdown(f"**Language:** {row['language']}")
                st.markdown(f"**Engines Used:** {row['engines_used']}")
                st.markdown(f"**Risk Level:** {row['risk']}")
            with col2:
                st.markdown(f"**CodeBERT:** {row['codebert_sim']:.1f}%")
                st.markdown(f"**AST Similarity:** {row['ast_sim']:.1f}%")
                st.markdown(f"**Winnowing:** {row['winnowing_sim']:.1f}%")
                st.markdown(f"**CFG:** {row['cfg_sim']:.1f}%")
            
            # Preview of code - NO nested expander! Use st.code directly
            if row['code_a_preview']:
                st.markdown("---")
                st.markdown("**📝 Code Preview:**")
                st.code(row['code_a_preview'][:500], language="python")
                st.code(row['code_b_preview'][:500], language="python")
            
            # Delete button
            if st.button(f"🗑️ Delete", key=f"del_{row['id']}"):
                db.delete_scan(row['id'])
                st.rerun()
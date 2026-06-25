import streamlit as st
from config import HAS_ZSS, HAS_TRANSFORMERS, HAS_SKLEARN

def page_settings():
    st.markdown("""
    <div style="padding:6px 0 22px 0;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#22d3ee;box-shadow:0 0 10px #22d3ee;"></span>
        <span style="font-size:10px;color:#22d3ee;letter-spacing:3px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">// Configuration</span>
      </div>
      <h1 style="font-family:'Orbitron',sans-serif;font-size:34px;font-weight:800;color:#d7f7ff;margin:0;line-height:1.15;letter-spacing:2px;text-shadow:0 0 22px rgba(34,211,238,.45);">SETTINGS</h1>
      <p style="color:rgba(143,182,196,0.7);font-size:12px;font-family:'JetBrains Mono',monospace;margin-top:8px;letter-spacing:.5px;">> toggle detection cores · changes persist instantly</p>
    </div>
    """, unsafe_allow_html=True)

    s = st.session_state["settings"]

    st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#22d3ee;letter-spacing:1px;text-shadow:0 0 10px rgba(34,211,238,.4);margin:8px 0 4px;">▚ Detection Engines</div>""", unsafe_allow_html=True)
    st.caption("⚡ Settings save automatically when you change them")
    
    # Auto-save on change using callback
    def on_change():
        # This runs immediately when checkbox changes
        st.session_state["settings"] = {
            "use_type_agnostic": st.session_state.get("cb_type_agnostic", True),
            "use_ast_ted": st.session_state.get("cb_ast_ted", HAS_ZSS),
            "use_cfg": st.session_state.get("cb_cfg", True),
            "use_winnowing": st.session_state.get("cb_winnowing", True),
            "use_codebert": st.session_state.get("cb_codebert", HAS_TRANSFORMERS),
            "use_ml": st.session_state.get("cb_ml", HAS_SKLEARN),
        }
        # Keep other settings
        st.session_state["settings"]["sensitivity"] = s.get("sensitivity", 70)
        st.session_state["settings"]["language"] = s.get("language", "Python")
        st.session_state["settings"]["method"] = s.get("method", "Hybrid (All Engines)")
        st.session_state["settings"]["theme"] = s.get("theme", "Dark")
        st.session_state["settings"]["save_history"] = s.get("save_history", True)
        st.session_state["settings"]["use_bytecode"] = s.get("use_bytecode", True)
        st.session_state["settings"]["use_big_o"] = s.get("use_big_o", True)
        
        st.toast("✅ Setting saved!", icon="✅")
    
    # Checkboxes with auto-save
    st.checkbox(
        "Type-Agnostic Normalization", 
        value=s.get("use_type_agnostic", True),
        key="cb_type_agnostic",
        on_change=on_change
    )
    
    st.checkbox(
        "Tree Edit Distance (AST)", 
        value=s.get("use_ast_ted", HAS_ZSS), 
        disabled=not HAS_ZSS,
        key="cb_ast_ted",
        on_change=on_change
    )
    
    st.checkbox(
        "Control Flow Graph", 
        value=s.get("use_cfg", True),
        key="cb_cfg",
        on_change=on_change
    )
    
    st.checkbox(
        "Winnowing (MOSS)", 
        value=s.get("use_winnowing", True),
        key="cb_winnowing",
        on_change=on_change
    )
    
    st.checkbox(
        "CodeBERT Semantic", 
        value=s.get("use_codebert", HAS_TRANSFORMERS), 
        disabled=not HAS_TRANSFORMERS,
        key="cb_codebert",
        on_change=on_change
    )
    
    st.checkbox(
        "ML Decision Tree", 
        value=s.get("use_ml", HAS_SKLEARN), 
        disabled=not HAS_SKLEARN,
        key="cb_ml",
        on_change=on_change
    )
    
    st.success("✅ Settings auto-save when you click any checkbox!")
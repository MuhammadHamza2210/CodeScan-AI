import streamlit as st
from config import HAS_ZSS, HAS_TRANSFORMERS, HAS_SKLEARN

def page_settings():
    st.markdown("""<div style="padding:8px 0 24px 0;"><h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;">Settings</h1></div>""", unsafe_allow_html=True)
    
    s = st.session_state["settings"]
    
    st.markdown("### 🎯 Detection Engines")
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
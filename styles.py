# styles.py
import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        .gradient-text {
            background: linear-gradient(135deg, #00FFAA 0%, #00B4FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(0, 255, 170, 0.1), rgba(0, 180, 255, 0.1));
            border: 1px solid rgba(0, 255, 170, 0.3);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 900;
            background: linear-gradient(135deg, #00FFAA, #00B4FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 170, 0.2);
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #00FFAA, #00B4FF);
            color: #0a0a1a;
            border: none;
            padding: 0.8rem 2rem;
            font-weight: 700;
            border-radius: 12px;
        }
        
        .badge-high {
            background: rgba(255, 59, 48, 0.2);
            border: 1px solid #FF3B30;
            color: #FF3B30;
            padding: 0.3rem 1rem;
            border-radius: 20px;
        }
        
        .badge-medium {
            background: rgba(255, 149, 0, 0.2);
            border: 1px solid #FF9500;
            color: #FF9500;
            padding: 0.3rem 1rem;
            border-radius: 20px;
        }
        
        .badge-low {
            background: rgba(52, 199, 89, 0.2);
            border: 1px solid #34C759;
            color: #34C759;
            padding: 0.3rem 1rem;
            border-radius: 20px;
        }
        
        .custom-progress {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
        }
        
        .custom-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00FFAA, #00B4FF);
            border-radius: 4px;
        }
    </style>
    """, unsafe_allow_html=True)
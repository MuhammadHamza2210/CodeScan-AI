import streamlit as st
import pandas as pd
import plotly.express as px
from config import HAS_PLOTLY, HAS_PANDAS
from database import db  # Add this import

def render_forensic_statistics(history_list=None):
    """Renders the Forensic Statistics section using database data"""
    
    st.markdown("""
    <div style="margin-top:32px;margin-bottom:6px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
        <div style="width:4px;height:22px;background:linear-gradient(180deg,#7c6dfa,#a78bfa);border-radius:2px;"></div>
        <span style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;color:#e8e8f0;">
          Forensic Statistics
        </span>
      </div>
      <p style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.3);margin-left:14px;">
        Correlation analysis · OLS trendlines · Obfuscation topology · Structural plagiarism detection
      </p>
    </div>
    """, unsafe_allow_html=True)

    if not HAS_PLOTLY or not HAS_PANDAS:
        missing = []
        if not HAS_PLOTLY:
            missing.append("plotly")
        if not HAS_PANDAS:
            missing.append("pandas")
        st.markdown(f"""
        <div class="forensic-panel">
          <div class="forensic-empty">
            <div class="icon">📦</div>
            <strong style="color:#a78bfa;">Missing dependencies</strong><br>
            Run <code style="color:#fbbf24;">pip install {' '.join(missing)}</code> to enable Forensic Statistics.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Load from DATABASE instead of session state
    df = db.get_all_scans()
    
    if df.empty or len(df) < 2:
        st.markdown("""
        <div class="forensic-panel">
          <div class="forensic-empty">
            <div class="icon">🔬</div>
            <strong style="color:#a78bfa;">Not enough data yet</strong><br>
            Run at least <strong style="color:#e8e8f0;">2 scans</strong> to unlock forensic charts.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Rename columns to match expected format
    df = df.rename(columns={
        'score': 'score',
        'verdict': 'verdict',
        'codebert_sim': 'codebert_sim',
        'bytecode_sim': 'bytecode_sim',
        'seq_sim': 'seq_sim',
        'timestamp': 'timestamp'
    })
    
    # Calculate structural avg
    df['structural_avg'] = (df['codebert_sim'] + df['bytecode_sim']) / 2

    n_total = len(df)
    n_plag = int((df["verdict"] == "PLAGIARIZED").sum())
    n_susp = int((df["verdict"] == "SUSPICIOUS").sum())
    n_orig = int((df["verdict"] == "ORIGINAL").sum())
    avg_score = df["score"].mean()

    st.markdown(f"""
    <div class="forensic-panel" style="padding-bottom:4px;">
      <div class="forensic-stat-chips">
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#a78bfa;">{n_total}</div><div class="forensic-chip-lbl">Total Scans</div></div>
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#f87171;">{n_plag}</div><div class="forensic-chip-lbl">Plagiarized</div></div>
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#fbbf24;">{n_susp}</div><div class="forensic-chip-lbl">Suspicious</div></div>
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#34d399;">{n_orig}</div><div class="forensic-chip-lbl">Original</div></div>
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#7c6dfa;">{avg_score:.1f}%</div><div class="forensic-chip-lbl">Avg Score</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    COLOR_MAP = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}
    for v in df["verdict"].unique():
        if v not in COLOR_MAP:
            COLOR_MAP[v] = "#7c6dfa"

    DARK_LAYOUT = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(17,17,21,0)",
        plot_bgcolor="rgba(17,17,21,0)",
        font=dict(family="DM Sans, sans-serif", color="#e8e8f0", size=12),
        title_font=dict(family="Syne, sans-serif", size=15, color="#a78bfa"),
        legend=dict(bgcolor="rgba(255,255,255,0.04)", bordercolor="rgba(255,255,255,0.08)", borderwidth=1, font=dict(size=11)),
        margin=dict(l=50, r=30, t=50, b=50),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)"),
    )

    st.markdown("""
    <div style="margin-top:24px;margin-bottom:10px;padding-left:4px;">
      <span style="font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:#e8e8f0;">
        ① Structural vs Lexical Similarity — Correlation Scatter
      </span>
    </div>
    """, unsafe_allow_html=True)

    fig_scatter = px.scatter(
        df, x="seq_sim", y="structural_avg", color="verdict",
        color_discrete_map=COLOR_MAP, marginal_x="histogram", marginal_y="histogram",
        trendline="ols", trendline_scope="overall", trendline_color_override="#7c6dfa",
        hover_data={"seq_sim": ":.1f", "structural_avg": ":.1f", "codebert_sim": ":.1f", "bytecode_sim": ":.1f", "score": ":.1f", "timestamp": True},
        labels={"seq_sim": "Lexical Similarity — seq_sim (%)", "structural_avg": "Structural Score — avg(CodeBERT, Bytecode) (%)"},
        height=540,
    )
    for trace in fig_scatter.data:
        if hasattr(trace, 'mode') and trace.mode == 'markers':
            trace.marker.size = 10
            trace.marker.opacity = 0.85
            trace.marker.line = dict(width=1, color="rgba(255,255,255,0.15)")
    fig_scatter.update_layout(**DARK_LAYOUT)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("""
    <div class="forensic-insight">
      <div class="forensic-insight-title">🔍 How to Read This Chart — Obfuscation Topology</div>
      <p><span class="highlight">● High-Y / Low-X points</span> indicate <strong>Structural Plagiarism</strong> — logic copied, surface tokens changed.</p>
      <p><span class="highlight-y">● High-X / Low-Y points</span> suggest <strong>Template Reuse</strong> — identical boilerplate, different logic.</p>
      <p><span class="highlight-g">● Low-X / Low-Y points</span> are <strong>genuinely independent</strong> submissions.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    fig_hist = px.histogram(df, x="score", color="verdict", color_discrete_map=COLOR_MAP, nbins=20, barmode="overlay", opacity=0.75, marginal="rug", height=360)
    fig_hist.update_layout(**DARK_LAYOUT)
    st.plotly_chart(fig_hist, use_container_width=True)

    if n_total >= 3:
        engine_cols = {"seq_sim": "Sequence", "structural_avg": "Structural Avg", "codebert_sim": "CodeBERT", "bytecode_sim": "Bytecode", "score": "Final Score"}
        melted_rows = []
        for _, row in df.iterrows():
            for col, label in engine_cols.items():
                melted_rows.append({"Engine": label, "Score": row[col], "Verdict": row["verdict"]})
        df_melted = pd.DataFrame(melted_rows)
        fig_box = px.box(df_melted, x="Engine", y="Score", color="Verdict", color_discrete_map=COLOR_MAP, points="all", height=420)
        fig_box.update_layout(**DARK_LAYOUT)
        st.plotly_chart(fig_box, use_container_width=True)


def page_analytics():
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
        <span style="font-size:11px;color:rgba(255,255,255,0.25);letter-spacing:1.5px;text-transform:uppercase;font-family:'DM Sans',sans-serif;">Dashboard</span>
      </div>
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;margin:0;line-height:1.2;">Analytics</h1>
      <p style="color:rgba(255,255,255,0.35);font-size:13px;font-family:'DM Sans',sans-serif;margin-top:6px;">Session metrics · Engine health · Forensic deep-dive</p>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        # Get total from database
        all_scans = db.get_all_scans()
        st.metric("Total Scans", len(all_scans))
    with m2:
        st.metric("Training Examples", len(st.session_state["training_data"]))
    with m3:
        from engines.codebert_engine import codebert_analyzer
        st.metric("CodeBERT Status", codebert_analyzer.get_status())

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Enhanced CFG now tracks Try/Except blocks and Function Calls!")
    
    # Render forensic stats from database
    render_forensic_statistics()
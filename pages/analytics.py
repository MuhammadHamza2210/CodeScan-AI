import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import HAS_PLOTLY, HAS_PANDAS
from database import db

def safe_float_series(series):
    """Safely convert series to float, handling bytes and corrupted data"""
    def convert(val):
        try:
            if isinstance(val, bytes):
                return 0.0
            return float(val)
        except (ValueError, TypeError):
            return 0.0
    return series.apply(convert)

def safe_float_val(value, default=0.0):
    """Safely convert a single value to float"""
    try:
        if isinstance(value, bytes):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def render_forensic_statistics(history_list=None):
    """Renders the Forensic Statistics section using database data"""
    
    st.markdown("""
    <div style="margin-top:32px;margin-bottom:6px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
        <div style="width:4px;height:22px;background:linear-gradient(180deg,#22d3ee,#00ff9c);border-radius:2px;box-shadow:0 0 10px #22d3ee;"></div>
        <span style="font-family:'Orbitron',sans-serif;font-size:19px;font-weight:700;color:#d7f7ff;letter-spacing:1.5px;text-shadow:0 0 14px rgba(34,211,238,.4);">
          FORENSIC STATISTICS
        </span>
      </div>
      <p style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(143,182,196,0.6);margin-left:14px;letter-spacing:.5px;">
        > correlation · OLS_trendlines · obfuscation_topology · structural_detection
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
            <strong style="color:#22d3ee;">Missing dependencies</strong><br>
            Run <code style="color:#ffb627;">pip install {' '.join(missing)}</code> to enable Forensic Statistics.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Load from DATABASE
    df = db.get_all_scans()
    
    if df.empty or len(df) < 2:
        st.markdown("""
        <div class="forensic-panel">
          <div class="forensic-empty">
            <div class="icon">🔬</div>
            <strong style="color:#22d3ee;">Not enough data yet</strong><br>
            Run at least <strong style="color:#d7f7ff;">2 scans</strong> to unlock forensic charts.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Safely convert numeric columns
    numeric_cols = ['score', 'codebert_sim', 'bytecode_sim', 'seq_sim', 
                    'ast_sim', 'cfg_sim', 'winnowing_sim', 'big_o_match',
                    'type_agnostic_seq_sim', 'type_agnostic_jac_sim', 'ted_sim']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = safe_float_series(df[col])
    
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
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#22d3ee;">{n_total}</div><div class="forensic-chip-lbl">Total Scans</div></div>
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#ff3b5c;">{n_plag}</div><div class="forensic-chip-lbl">Plagiarized</div></div>
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#ffb627;">{n_susp}</div><div class="forensic-chip-lbl">Suspicious</div></div>
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#00ff9c;">{n_orig}</div><div class="forensic-chip-lbl">Original</div></div>
        <div class="forensic-chip"><div class="forensic-chip-val" style="color:#5eead4;">{avg_score:.1f}%</div><div class="forensic-chip-lbl">Avg Score</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    COLOR_MAP = {"PLAGIARIZED": "#ff3b5c", "SUSPICIOUS": "#ffb627", "ORIGINAL": "#00ff9c"}
    for v in df["verdict"].unique():
        if v not in COLOR_MAP:
            COLOR_MAP[v] = "#22d3ee"

    # ── Neon Plotly helpers ──────────────────────────────────
    def _rgba(hexc, a):
        hexc = hexc.lstrip("#")
        r, g, b = int(hexc[0:2], 16), int(hexc[2:4], 16), int(hexc[4:6], 16)
        return f"rgba({r},{g},{b},{a})"

    def neon_layout(height, **extra):
        base = dict(
            height=height,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono, monospace", color="#9fc4d2", size=12),
            legend=dict(bgcolor="rgba(34,211,238,0.04)", bordercolor="rgba(34,211,238,0.18)",
                        borderwidth=1, font=dict(size=11, color="#d7f7ff")),
            margin=dict(l=40, r=30, t=30, b=40),
            hoverlabel=dict(bgcolor="#071018", bordercolor="#22d3ee",
                            font=dict(family="JetBrains Mono, monospace", color="#d7f7ff", size=11)),
        )
        base.update(extra)
        return base

    def section(title, sub=""):
        subhtml = f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10.5px;color:rgba(143,182,196,0.55);margin-left:16px;letter-spacing:.3px;">{sub}</div>' if sub else ""
        st.markdown(f"""
        <div style="margin:30px 0 10px;padding-left:4px;">
          <span style="font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:600;color:#22d3ee;letter-spacing:1px;text-shadow:0 0 10px rgba(34,211,238,.4);">{title}</span>
          {subhtml}
        </div>
        """, unsafe_allow_html=True)

    engine_meta = [
        ("codebert_sim", "CodeBERT"), ("bytecode_sim", "Bytecode"), ("ast_sim", "AST"),
        ("cfg_sim", "CFG"), ("winnowing_sim", "Winnowing"), ("ted_sim", "TED"),
        ("type_agnostic_seq_sim", "Type-Seq"), ("type_agnostic_jac_sim", "Type-Jac"),
        ("big_o_match", "Big-O"), ("seq_sim", "Sequence"), ("jac_sim", "Jaccard"),
        ("ngram_sim", "N-gram"),
    ]
    eng_cols = [c for c, _ in engine_meta if c in df.columns]
    label_of = dict(engine_meta)
    for c in eng_cols:
        df[c] = safe_float_series(df[c])

    verdict_order = [v for v in ["PLAGIARIZED", "SUSPICIOUS", "ORIGINAL"] if v in df["verdict"].values]

    # ── 01 · Verdict donut + risk gauge ──────────────────────
    section("◚ 01 · Verdict Distribution & Risk Index",
            "live breakdown of every scan in the forensic log")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        counts = df["verdict"].value_counts()
        order = [v for v in verdict_order if v in counts.index] or list(counts.index)
        fig_d = go.Figure(go.Pie(
            labels=order, values=[int(counts[v]) for v in order], hole=0.66, sort=False,
            direction="clockwise", rotation=90,
            marker=dict(colors=[COLOR_MAP.get(v, "#22d3ee") for v in order],
                        line=dict(color="#04070d", width=3)),
            textinfo="percent", textfont=dict(family="JetBrains Mono, monospace", size=12, color="#04070d"),
            hovertemplate="%{label}: %{value} scans (%{percent})<extra></extra>",
        ))
        fig_d.add_annotation(text=f"<b>{n_total}</b><br><span style='font-size:11px'>SCANS</span>",
                             showarrow=False, font=dict(family="Orbitron, sans-serif", size=26, color="#22d3ee"))
        fig_d.update_layout(**neon_layout(330, showlegend=True,
                            legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center",
                                        font=dict(size=11, color="#d7f7ff"), bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(fig_d, use_container_width=True)
    with col_b:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=float(avg_score),
            number=dict(suffix="%", font=dict(family="Orbitron, sans-serif", color="#22d3ee", size=38)),
            title=dict(text="MEAN SIMILARITY INDEX", font=dict(family="JetBrains Mono, monospace", size=11, color="#5d8294")),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=1, tickcolor="#3a5a68", tickfont=dict(size=9)),
                bar=dict(color="#22d3ee", thickness=0.28),
                bgcolor="rgba(8,18,28,0.35)", borderwidth=0,
                steps=[dict(range=[0, 42], color="rgba(0,255,156,0.16)"),
                       dict(range=[42, 70], color="rgba(255,182,39,0.16)"),
                       dict(range=[70, 100], color="rgba(255,59,92,0.16)")],
                threshold=dict(line=dict(color="#ff2d78", width=3), thickness=0.85, value=70),
            ),
        ))
        fig_g.update_layout(**neon_layout(330, margin=dict(l=30, r=30, t=60, b=10)))
        st.plotly_chart(fig_g, use_container_width=True)

    # ── 02 · Engine fingerprint radar ────────────────────────
    section("◚ 02 · Engine Fingerprint — Avg Similarity by Verdict",
            "which detection engines fire hardest for each outcome")
    fig_r = go.Figure()
    for v in (verdict_order or ["ALL"]):
        sub = df if v == "ALL" else df[df["verdict"] == v]
        if sub.empty:
            continue
        vals = [float(sub[c].mean()) for c in eng_cols]
        col = COLOR_MAP.get(v, "#22d3ee")
        fig_r.add_trace(go.Scatterpolar(
            r=vals + vals[:1],
            theta=[label_of[c] for c in eng_cols] + [label_of[eng_cols[0]]],
            fill="toself", name=v, line=dict(color=col, width=2),
            fillcolor=_rgba(col, 0.10), marker=dict(size=5, color=col),
            hovertemplate="%{theta}: %{r:.1f}%<extra>" + v + "</extra>",
        ))
    fig_r.update_layout(**neon_layout(470, polar=dict(
        bgcolor="rgba(8,18,28,0.35)",
        radialaxis=dict(range=[0, 100], gridcolor="rgba(34,211,238,0.15)",
                        linecolor="rgba(34,211,238,0.2)", tickfont=dict(size=9, color="#5d8294"), angle=90),
        angularaxis=dict(gridcolor="rgba(34,211,238,0.12)", linecolor="rgba(34,211,238,0.2)",
                         tickfont=dict(size=10, color="#9fc4d2")),
    ), legend=dict(orientation="h", y=-0.06, x=0.5, xanchor="center",
                   font=dict(size=11, color="#d7f7ff"), bgcolor="rgba(0,0,0,0)")))
    st.plotly_chart(fig_r, use_container_width=True)

    # ── 03 · Detection timeline ──────────────────────────────
    section("◚ 03 · Detection Timeline — Score Trajectory",
            "every scan in chronological order, colored by verdict")
    dft = df.sort_values("id") if "id" in df.columns else df.iloc[::-1]
    x = list(range(1, len(dft) + 1))
    ys = dft["score"].astype(float).tolist()
    mcols = [COLOR_MAP.get(v, "#22d3ee") for v in dft["verdict"]]
    htext = [f"{str(a)} vs {str(b)}<br>{v} · {s:.1f}%"
             for a, b, v, s in zip(dft["code_a_name"], dft["code_b_name"], dft["verdict"], ys)]
    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(x=x, y=ys, mode="lines", line=dict(color="#22d3ee", width=2.5, shape="spline"),
                               fill="tozeroy", fillcolor="rgba(34,211,238,0.10)", hoverinfo="skip", showlegend=False))
    fig_t.add_trace(go.Scatter(x=x, y=ys, mode="markers",
                               marker=dict(size=9, color=mcols, line=dict(width=1.5, color="#04070d")),
                               text=htext, hovertemplate="%{text}<extra></extra>", showlegend=False))
    fig_t.add_hline(y=70, line=dict(color="#ff2d78", width=1.2, dash="dot"),
                    annotation_text="PLAGIARISM THRESHOLD",
                    annotation_position="top right", annotation_font=dict(color="#ff2d78", size=10))
    fig_t.update_layout(**neon_layout(360,
        xaxis=dict(title="Scan #", gridcolor="rgba(34,211,238,0.06)", zerolinecolor="rgba(34,211,238,0.12)"),
        yaxis=dict(title="Similarity %", range=[0, 105], gridcolor="rgba(34,211,238,0.06)", zerolinecolor="rgba(34,211,238,0.12)"),
    ))
    st.plotly_chart(fig_t, use_container_width=True)

    # ── 04 · Engine correlation matrix ───────────────────────
    if n_total >= 3:
        section("◚ 04 · Engine Correlation Matrix — Co-firing Patterns",
                "blue = engines agree, pink = engines diverge")
        cc = [c for c in eng_cols if df[c].std() > 0]
        if df["score"].std() > 0:
            cc = cc + ["score"]
        if len(cc) >= 2:
            corr = df[cc].corr().fillna(0)
            lab = [label_of.get(c, "Score") for c in cc]
            fig_h = go.Figure(go.Heatmap(
                z=corr.values, x=lab, y=lab,
                colorscale=[[0, "#ff2d78"], [0.5, "#071018"], [1, "#22d3ee"]],
                zmin=-1, zmax=1, zmid=0, xgap=2, ygap=2,
                colorbar=dict(tickfont=dict(size=9, color="#9fc4d2"), outlinewidth=0, len=0.85),
                hovertemplate="%{y} ↔ %{x}<br>r = %{z:.2f}<extra></extra>",
            ))
            fig_h.update_layout(**neon_layout(500,
                xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
                yaxis=dict(tickfont=dict(size=10), autorange="reversed")))
            st.plotly_chart(fig_h, use_container_width=True)

    st.markdown("""
    <div class="forensic-insight">
      <div class="forensic-insight-title">◈ Reading the Forensics</div>
      <p><span class="highlight">Radar spikes</span> reveal the engines driving each verdict — a tall <strong>CodeBERT/AST</strong> arm on PLAGIARIZED means structural copying.</p>
      <p><span class="highlight-y">Timeline points above the threshold line</span> are flagged scans; clusters hint at a batch of copied submissions.</p>
      <p><span class="highlight-g">Bright-blue cells</span> in the matrix are engines that consistently agree — redundant signal you can trust.</p>
    </div>
    """, unsafe_allow_html=True)


def page_analytics():
    st.markdown("""
    <div style="padding:6px 0 22px 0;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#22d3ee;box-shadow:0 0 10px #22d3ee;"></span>
        <span style="font-size:10px;color:#22d3ee;letter-spacing:3px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">// Forensic Dashboard</span>
      </div>
      <h1 style="font-family:'Orbitron',sans-serif;font-size:34px;font-weight:800;color:#d7f7ff;margin:0;line-height:1.15;letter-spacing:2px;text-shadow:0 0 22px rgba(34,211,238,.45);">ANALYTICS</h1>
      <p style="color:rgba(143,182,196,0.7);font-size:12px;font-family:'JetBrains Mono',monospace;margin-top:8px;letter-spacing:.5px;">> session_metrics · engine_health · forensic_deep_dive</p>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        all_scans = db.get_all_scans()
        st.metric("Total Scans", len(all_scans))
    with m2:
        st.metric("Training Examples", len(st.session_state["training_data"]))
    with m3:
        from engines.codebert_engine import codebert_analyzer
        st.metric("CodeBERT Status", codebert_analyzer.get_status())

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Enhanced CFG now tracks Try/Except blocks and Function Calls!")
    
    render_forensic_statistics()
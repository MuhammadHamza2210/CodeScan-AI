import streamlit as st
import itertools
import pandas as pd
import time
from datetime import datetime
from pages.analyze import detect_plagiarism
from ui_components import generate_heatmap, badge

# Neon palette
NEON = "#22d3ee"
NEON2 = "#00ff9c"
MUTED = "rgba(143,182,196,0.7)"
VC = {"PLAGIARIZED": "#ff3b5c", "SUSPICIOUS": "#ffb627", "ORIGINAL": "#00ff9c"}


def page_batch():
    # ── Header ───────────────────────────────────────────────
    st.markdown("""
    <div style="padding:6px 0 22px 0;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#22d3ee;box-shadow:0 0 10px #22d3ee;"></span>
        <span style="font-size:10px;color:#22d3ee;letter-spacing:3px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">// Batch Processing</span>
      </div>
      <h1 style="font-family:'Orbitron',sans-serif;font-size:34px;font-weight:800;color:#d7f7ff;margin:0;line-height:1.15;letter-spacing:2px;text-shadow:0 0 22px rgba(34,211,238,.45);">BATCH<span style="color:#22d3ee;"> ANALYSIS</span></h1>
      <p style="color:rgba(143,182,196,0.7);font-size:12px;font-family:'JetBrains Mono',monospace;margin-top:8px;letter-spacing:.5px;">> upload N files · compare every pair · all 6 engines</p>
    </div>
    """, unsafe_allow_html=True)

    # ── File upload ──────────────────────────────────────────
    uploaded_files = st.file_uploader(
        "📁 Upload Code Files",
        type=["py", "java", "cpp", "c", "js", "txt", "html", "css"],
        accept_multiple_files=True,
        key="batch_files",
    )

    if uploaded_files:
        chips = "".join(
            f"""<div style="background:rgba(34,211,238,0.06);border:1px solid rgba(34,211,238,0.2);border-radius:4px;padding:5px 12px;font-size:11.5px;color:#d7f7ff;font-family:'JetBrains Mono',monospace;">▸ {f.name}</div>"""
            for f in uploaded_files
        )
        st.markdown(f"""
        <div style="background:rgba(8,18,28,0.6);border:1px solid rgba(34,211,238,0.16);border-radius:4px;padding:18px;margin:16px 0;box-shadow:inset 0 0 22px rgba(34,211,238,0.03);">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#22d3ee;">▚ Loaded Files ({len(uploaded_files)})</span>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">{chips}</div>
        </div>
        """, unsafe_allow_html=True)

        num_files = len(uploaded_files)
        num_comparisons = num_files * (num_files - 1) // 2
        st.info(f"📊 {num_files} files → {num_comparisons} pairwise comparisons")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            run_btn = st.button("⬡  Run Batch Analysis", use_container_width=True, key="batch_run")
            st.markdown("</div>", unsafe_allow_html=True)

        if run_btn:
            if len(uploaded_files) < 2:
                st.warning("⚠️ Please upload at least 2 files to compare.")
            else:
                codes = {}
                for f in uploaded_files:
                    try:
                        codes[f.name] = f.read().decode("utf-8")
                    except Exception:
                        codes[f.name] = f.read().decode("utf-8", errors="replace")

                names = list(codes.keys())
                results = []

                st.markdown('<div style="height:1px;background:rgba(34,211,238,0.16);margin:20px 0;"></div>', unsafe_allow_html=True)
                st.markdown("""<div style="font-family:'Orbitron',sans-serif;font-size:16px;font-weight:700;color:#d7f7ff;letter-spacing:1.5px;text-shadow:0 0 14px rgba(34,211,238,.4);margin-bottom:10px;">⟁ ANALYZING</div>""", unsafe_allow_html=True)

                pairs = list(itertools.combinations(range(len(names)), 2))
                total_pairs = len(pairs)

                if total_pairs == 0:
                    st.warning("⚠️ No comparisons to make. Please upload different files.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    start_time = time.time()

                    for idx, (i, j) in enumerate(pairs):
                        current = idx + 1
                        progress_bar.progress(current / total_pairs)
                        status_text.markdown(f"""
                        <div style="background:rgba(8,18,28,0.6);border:1px solid rgba(34,211,238,0.16);border-radius:4px;padding:11px 14px;margin:5px 0;font-family:'JetBrains Mono',monospace;">
                            <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;">
                                <div style="color:#9fc4d2;">
                                    <span style="color:#22d3ee;">&gt;</span> comparing
                                    <span style="color:#22d3ee;">{names[i]}</span>
                                    <span style="color:#5d8294;">↔</span>
                                    <span style="color:#00ff9c;">{names[j]}</span>
                                </div>
                                <div style="color:#22d3ee;font-weight:600;">[{current}/{total_pairs}]</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        try:
                            r = detect_plagiarism(codes[names[i]], codes[names[j]], "Hybrid (All Engines)", 70, "Python")
                            results.append((names[i], names[j], r["score"], r["verdict"]))
                        except Exception as e:
                            results.append((names[i], names[j], 0, "ERROR"))
                            st.error(f"Error comparing {names[i]} vs {names[j]}: {str(e)[:100]}")

                    progress_bar.empty()
                    status_text.empty()

                    total_time = int(time.time() - start_time)
                    total_mins, total_secs = total_time // 60, total_time % 60
                    avg_time = total_time / total_pairs if total_pairs > 0 else 0

                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,rgba(0,255,156,0.12),rgba(34,211,238,0.06));border:1px solid rgba(0,255,156,0.4);border-radius:4px;padding:18px;text-align:center;margin:16px 0;box-shadow:0 0 24px rgba(0,255,156,0.12);">
                        <div style="font-family:'Orbitron',sans-serif;font-weight:700;font-size:18px;color:#00ff9c;letter-spacing:1.5px;text-shadow:0 0 14px rgba(0,255,156,.5);">✓ ANALYSIS COMPLETE</div>
                        <div style="color:#9fc4d2;margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:12px;">{total_pairs} comparisons · {total_mins}m {total_secs}s · avg {avg_time:.1f}s/pair</div>
                    </div>
                    """, unsafe_allow_html=True)

                    results.sort(key=lambda x: x[2], reverse=True)

                    st.markdown('<div style="height:1px;background:rgba(34,211,238,0.16);margin:20px 0;"></div>', unsafe_allow_html=True)
                    st.markdown("""<div style="font-family:'Orbitron',sans-serif;font-size:18px;font-weight:700;color:#d7f7ff;letter-spacing:1.5px;text-shadow:0 0 14px rgba(34,211,238,.4);margin-bottom:14px;">⬡ RESULTS</div>""", unsafe_allow_html=True)

                    plag_count = sum(1 for _, _, _, v in results if v == "PLAGIARIZED")
                    susp_count = sum(1 for _, _, _, v in results if v == "SUSPICIOUS")
                    orig_count = sum(1 for _, _, _, v in results if v == "ORIGINAL")
                    avg_score = sum(r[2] for r in results) / len(results) if results else 0

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Comparisons", len(results))
                    c2.metric("Plagiarized", plag_count)
                    c3.metric("Suspicious", susp_count)
                    c4.metric("Original", orig_count)

                    st.markdown('<div style="height:1px;background:rgba(34,211,238,0.16);margin:20px 0;"></div>', unsafe_allow_html=True)

                    st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#22d3ee;letter-spacing:1px;text-shadow:0 0 10px rgba(34,211,238,.4);margin-bottom:10px;">▚ Similarity Heatmap</div>""", unsafe_allow_html=True)
                    st.markdown(generate_heatmap(names, results), unsafe_allow_html=True)

                    st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#22d3ee;letter-spacing:1px;text-shadow:0 0 10px rgba(34,211,238,.4);margin:20px 0 10px;">▚ Detailed Comparisons</div>""", unsafe_allow_html=True)

                    for na, nb, score, verdict in results:
                        color = VC.get(verdict, "#22d3ee")
                        st.markdown(f"""
                        <div style="background:{color}12;border:1px solid {color}40;border-left:3px solid {color};border-radius:4px;padding:13px 18px;margin-bottom:10px;box-shadow:0 0 16px {color}1a;">
                            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                                <div style="display:flex;align-items:center;gap:8px;font-family:'JetBrains Mono',monospace;font-size:13px;color:#d7f7ff;">
                                    <span style="color:#22d3ee;">▸</span> {na}
                                    <span style="color:#5d8294;">↔</span> {nb}
                                </div>
                                <div style="display:flex;align-items:center;gap:14px;">
                                    <span style="font-family:'Orbitron',sans-serif;font-size:22px;font-weight:800;color:{color};text-shadow:0 0 14px {color}66;">{score:.1f}%</span>
                                    <span style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;letter-spacing:1px;color:{color};border:1px solid {color}66;border-radius:4px;padding:3px 10px;">{verdict}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown('<div style="height:1px;background:rgba(34,211,238,0.16);margin:20px 0;"></div>', unsafe_allow_html=True)
                    st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#22d3ee;letter-spacing:1px;text-shadow:0 0 10px rgba(34,211,238,.4);margin-bottom:10px;">▚ Export</div>""", unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        df = pd.DataFrame(results, columns=["File A", "File B", "Similarity Score", "Verdict"])
                        st.download_button(
                            "📥 Download CSV", df.to_csv(index=False),
                            f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            "text/csv", use_container_width=True,
                        )
                    with col2:
                        report = f"""
╔══════════════════════════════════════════╗
║   CODESCAN AI — BATCH ANALYSIS REPORT     ║
╚══════════════════════════════════════════╝

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Files: {len(names)}
Total Comparisons: {len(results)}
Analysis Time: {total_mins} min {total_secs} sec

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESULTS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Plagiarized: {plag_count}
Suspicious:  {susp_count}
Original:    {orig_count}
Average Score: {avg_score:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DETAILED RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                        for na, nb, score, verdict in results:
                            report += f"\n{na} vs {nb}: {score:.1f}% - {verdict}"
                        report += "\n\n═══════════════════════════════════════════\nCodeScan AI Ultimate Edition © 2026"
                        st.download_button(
                            "📄 Download TXT", report,
                            f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            "text/plain", use_container_width=True,
                        )

    else:
        # ── Empty state ──────────────────────────────────────
        st.markdown("""
        <div style="background:rgba(8,18,28,0.5);border:1px dashed rgba(34,211,238,0.25);border-radius:6px;padding:48px 32px;text-align:center;margin-top:20px;box-shadow:inset 0 0 30px rgba(34,211,238,0.03);">
            <div style="font-size:46px;margin-bottom:14px;filter:drop-shadow(0 0 14px rgba(34,211,238,.5));">⬡</div>
            <h3 style="font-family:'Orbitron',sans-serif;color:#d7f7ff;margin-bottom:8px;letter-spacing:1.5px;text-shadow:0 0 14px rgba(34,211,238,.4);">NO FILES LOADED</h3>
            <p style="color:rgba(143,182,196,0.7);font-family:'JetBrains Mono',monospace;font-size:12px;">> upload 2 or more code files to begin batch comparison</p>
            <div style="margin-top:20px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap;font-family:'JetBrains Mono',monospace;">
                <span style="background:rgba(34,211,238,0.06);border:1px solid rgba(34,211,238,0.2);border-radius:4px;padding:4px 12px;font-size:11px;color:#9fc4d2;">.py</span>
                <span style="background:rgba(34,211,238,0.06);border:1px solid rgba(34,211,238,0.2);border-radius:4px;padding:4px 12px;font-size:11px;color:#9fc4d2;">.java</span>
                <span style="background:rgba(34,211,238,0.06);border:1px solid rgba(34,211,238,0.2);border-radius:4px;padding:4px 12px;font-size:11px;color:#9fc4d2;">.cpp</span>
                <span style="background:rgba(34,211,238,0.06);border:1px solid rgba(34,211,238,0.2);border-radius:4px;padding:4px 12px;font-size:11px;color:#9fc4d2;">.js</span>
                <span style="background:rgba(34,211,238,0.06);border:1px solid rgba(34,211,238,0.2);border-radius:4px;padding:4px 12px;font-size:11px;color:#9fc4d2;">.txt</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

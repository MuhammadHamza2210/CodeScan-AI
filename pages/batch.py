import streamlit as st
import itertools
import pandas as pd
import time
from datetime import datetime
from pages.analyze import detect_plagiarism
from ui_components import generate_heatmap, badge

def page_batch():
    # Header
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
        <span style="font-size:11px;color:var(--text-muted);letter-spacing:1.5px;text-transform:uppercase;">Batch Processing</span>
      </div>
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:var(--text);margin:0;line-height:1.2;">Batch Analysis</h1>
      <p style="color:var(--text-muted);font-size:13px;margin-top:6px;">Upload multiple files to compare all pairs at once</p>
    </div>
    """, unsafe_allow_html=True)

    # File upload area
    uploaded_files = st.file_uploader(
        "📁 Upload Code Files",
        type=["py", "java", "cpp", "c", "js", "txt", "html", "css"],
        accept_multiple_files=True,
        key="batch_files"
    )

    if uploaded_files:
        # Show uploaded files
        st.markdown(f"""
        <div style="background:var(--surface2);border-radius:12px;padding:16px;margin:16px 0;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <span style="font-size:20px;">📄</span>
                <span style="font-weight:600;color:var(--text);">Uploaded Files ({len(uploaded_files)})</span>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
        """, unsafe_allow_html=True)
        
        for f in uploaded_files:
            st.markdown(f"""
                <div style="background:var(--surface3);border-radius:6px;padding:4px 12px;font-size:12px;color:var(--text);">
                    📄 {f.name}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Calculate number of comparisons
        num_files = len(uploaded_files)
        num_comparisons = num_files * (num_files - 1) // 2
        
        # Show info
        st.info(f"📊 {num_files} files will create {num_comparisons} comparisons")
        
        # Run button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            run_btn = st.button("🚀 Run Batch Analysis", type="primary", use_container_width=True)
        
        if run_btn:
            if len(uploaded_files) < 2:
                st.warning("⚠️ Please upload at least 2 files to compare.")
            else:
                # Read all files
                codes = {}
                for f in uploaded_files:
                    try:
                        codes[f.name] = f.read().decode("utf-8")
                    except:
                        codes[f.name] = f.read().decode("utf-8", errors="replace")
                
                names = list(codes.keys())
                results = []
                
                # Progress section
                st.markdown("---")
                st.markdown("### 🔄 Analyzing Files")
                
                pairs = list(itertools.combinations(range(len(names)), 2))
                total_pairs = len(pairs)
                
                # Check if there are any pairs to compare
                if total_pairs == 0:
                    st.warning("⚠️ No comparisons to make. Please upload different files.")
                else:
                    # Progress bar only - no countdown timer
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    start_time = time.time()
                    
                    for idx, (i, j) in enumerate(pairs):
                        current = idx + 1
                        progress = current / total_pairs
                        
                        # Update progress bar
                        progress_bar.progress(progress)
                        
                        # Update status text (simple, without timer)
                        status_text.markdown(f"""
                        <div style="background:var(--surface2);border-radius:8px;padding:12px;margin:5px 0;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div>
                                    <span style="font-size:14px;">🔄</span> 
                                    <strong>Comparing:</strong> 
                                    <code style="color:var(--accent);">{names[i]}</code> 
                                    <span style="color:var(--text-muted);">vs</span> 
                                    <code style="color:var(--accent);">{names[j]}</code>
                                </div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--accent);">
                                    {current}/{total_pairs}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Run the actual comparison
                        try:
                            r = detect_plagiarism(
                                codes[names[i]], 
                                codes[names[j]], 
                                "Hybrid (All Engines)", 
                                70, 
                                "Python"
                            )
                            results.append((names[i], names[j], r["score"], r["verdict"]))
                        except Exception as e:
                            results.append((names[i], names[j], 0, "ERROR"))
                            st.error(f"Error comparing {names[i]} vs {names[j]}: {str(e)[:100]}")
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Total time taken (only shown at the end)
                    total_time = int(time.time() - start_time)
                    total_mins = total_time // 60
                    total_secs = total_time % 60
                    
                    # Calculate average safely (prevent division by zero)
                    avg_time = total_time / total_pairs if total_pairs > 0 else 0
                    
                    # Show success with time
                    st.markdown(f"""
                    <div style="background:var(--green)15;border:1px solid var(--green)30;border-radius:12px;padding:16px;text-align:center;margin:16px 0;">
                        <span style="font-size:32px;">✅</span>
                        <div style="font-weight:700;font-size:18px;color:var(--green);margin-top:8px;">Analysis Complete!</div>
                        <div style="color:var(--text-muted);margin-top:4px;">Completed {total_pairs} comparisons in {total_mins} minutes {total_secs} seconds</div>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">⚡ Average: {avg_time:.1f} seconds per comparison</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Sort results
                    results.sort(key=lambda x: x[2], reverse=True)
                    
                    # Results section
                    st.markdown("---")
                    st.markdown("## 📊 Analysis Results")
                    
                    # Stats cards
                    plag_count = sum(1 for _, _, _, v in results if v == "PLAGIARIZED")
                    susp_count = sum(1 for _, _, _, v in results if v == "SUSPICIOUS")
                    orig_count = sum(1 for _, _, _, v in results if v == "ORIGINAL")
                    avg_score = sum(r[2] for r in results) / len(results) if results else 0
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Total Comparisons", len(results))
                    with col2:
                        st.metric("🔴 Plagiarized", plag_count)
                    with col3:
                        st.metric("🟡 Suspicious", susp_count)
                    with col4:
                        st.metric("🟢 Original", orig_count)
                    
                    st.markdown("---")
                    
                    # Heatmap
                    st.markdown("### 🗺️ Similarity Heatmap")
                    st.markdown(generate_heatmap(names, results), unsafe_allow_html=True)
                    
                    # Detailed results
                    st.markdown("### 📋 Detailed Comparison Results")
                    
                    for na, nb, score, verdict in results:
                        if verdict == "PLAGIARIZED":
                            color = "#f87171"
                            bg = "rgba(248,113,113,0.1)"
                            icon = "🔴"
                        elif verdict == "SUSPICIOUS":
                            color = "#fbbf24"
                            bg = "rgba(251,191,36,0.1)"
                            icon = "🟡"
                        else:
                            color = "#34d399"
                            bg = "rgba(52,211,153,0.1)"
                            icon = "🟢"
                        
                        st.markdown(f"""
                        <div style="background:{bg};border-radius:10px;padding:14px 18px;margin-bottom:10px;border-left:3px solid {color};">
                            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                                <div style="display:flex;align-items:center;gap:8px;">
                                    <span style="font-size:18px;">📄</span>
                                    <span style="font-family:'JetBrains Mono',monospace;font-weight:500;">{na}</span>
                                    <span style="color:var(--text-muted);">vs</span>
                                    <span style="font-family:'JetBrains Mono',monospace;font-weight:500;">{nb}</span>
                                </div>
                                <div style="display:flex;align-items:center;gap:12px;">
                                    <div style="background:{color}20;border-radius:20px;padding:4px 16px;">
                                        <span style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:{color};">{score:.1f}%</span>
                                    </div>
                                    <span style="font-size:18px;">{icon}</span>
                                    <span style="font-weight:600;color:{color};">{verdict}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Export section
                    st.markdown("---")
                    st.markdown("### 💾 Export Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        df = pd.DataFrame(results, columns=["File A", "File B", "Similarity Score", "Verdict"])
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "📥 Download as CSV",
                            csv,
                            f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            "text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        report = f"""
╔══════════════════════════════════════════╗
║   CODESCAN AI — BATCH ANALYSIS REPORT   ║
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
                            "📄 Download as TXT",
                            report,
                            f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            "text/plain",
                            use_container_width=True
                        )
    
    else:
        # Empty state
        st.markdown("""
        <div style="background:var(--surface2);border-radius:16px;padding:48px 32px;text-align:center;margin-top:20px;">
            <div style="font-size:48px;margin-bottom:16px;">📁</div>
            <h3 style="color:var(--text);margin-bottom:8px;">No Files Uploaded</h3>
            <p style="color:var(--text-muted);">Upload 2 or more code files to start batch analysis</p>
            <div style="margin-top:20px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap;">
                <span style="background:var(--surface3);border-radius:20px;padding:4px 12px;font-size:12px;">🐍 Python (.py)</span>
                <span style="background:var(--surface3);border-radius:20px;padding:4px 12px;font-size:12px;">☕ Java (.java)</span>
                <span style="background:var(--surface3);border-radius:20px;padding:4px 12px;font-size:12px;">⚙️ C++ (.cpp)</span>
                <span style="background:var(--surface3);border-radius:20px;padding:4px 12px;font-size:12px;">📜 JavaScript (.js)</span>
                <span style="background:var(--surface3);border-radius:20px;padding:4px 12px;font-size:12px;">📄 Text (.txt)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
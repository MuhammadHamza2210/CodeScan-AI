# ============================================
# CodeGuard AI - UI Components Module
# ============================================

import streamlit as st

def hero_section():
    """Display hero banner"""
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 class='gradient-text' style='font-size: 4rem; margin: 0;'>
                🛡️ CodeGuard AI
            </h1>
            <p style='color: #888; font-size: 1.3rem;'>
                Advanced AI-Powered Code Plagiarism Detection
            </p>
        </div>
    """, unsafe_allow_html=True)

def stats_overview(statistics):
    """Display statistics cards"""
    if not statistics:
        statistics = {
            'total_pairs': 0,
            'high_similarity': 0,
            'medium_similarity': 0,
            'avg_similarity': 0
        }
    
    cols = st.columns(4)
    
    metrics = [
        ("🔍 Total Pairs", statistics['total_pairs'], "#00FFAA"),
        ("🚨 High Risk", statistics['high_similarity'], "#FF3B30"),
        ("⚠️ Medium Risk", statistics['medium_similarity'], "#FF9500"),
        ("📈 Avg Similarity", f"{statistics['avg_similarity']}%", "#00B4FF")
    ]
    
    for col, (label, value, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-label'>{label}</div>
                    <div class='stat-number' style='-webkit-text-fill-color: {color};'>{value}</div>
                </div>
            """, unsafe_allow_html=True)

def file_upload_section():
    """File upload interface"""
    st.markdown("## 📤 Upload Source Code")
    
    tab1, tab2 = st.tabs(["📂 Browse Files", "✏️ Paste Code"])
    
    with tab1:
        files = st.file_uploader(
            "Choose Python files",
            type=['py', 'txt'],
            accept_multiple_files=True,
            help="Upload .py files for comparison"
        )
        if files:
            st.success(f"✅ {len(files)} files ready!")
    
    with tab2:
        code = st.text_area(
            "Paste Python code:",
            height=200,
            placeholder="def function():\n    pass"
        )
        if code:
            st.info("💡 Code ready for analysis!")
    
    return files if 'files' in locals() else []

def comparison_card(pair):
    """Display a single comparison result card"""
    severity = pair.get('severity', 'low')
    
    color_map = {
        'high': ('#FF3B30', 'badge-high'),
        'medium': ('#FF9500', 'badge-medium'),
        'low': ('#34C759', 'badge-low')
    }
    
    color, badge_class = color_map.get(severity, ('#888', ''))
    
    st.markdown(f"""
        <div class='glass-card' style='border-left: 4px solid {color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h4 style='color: white; margin: 0;'>
                        📄 {pair['file1']} ↔ 📄 {pair['file2']}
                    </h4>
                    <p style='color: #888; margin: 0.5rem 0 0 0;'>
                        Text: {pair['text_similarity']}% | Structure: {pair['structure_similarity']}%
                    </p>
                </div>
                <div style='text-align: right;'>
                    <span class='{badge_class}'>{severity.upper()}</span>
                    <h2 style='color: {color}; margin: 0.5rem 0 0 0;'>{pair['final_similarity']}%</h2>
                </div>
            </div>
            <div class='custom-progress' style='margin-top: 1rem;'>
                <div class='custom-progress-fill' style='width: {pair['final_similarity']}%;'></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def file_details_card(filename, code, metrics):
    """Display file details and metrics"""
    with st.expander(f"📄 {filename} - {metrics.get('code_lines', '?')} lines"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            display_code = code[:1000] + ('...' if len(code) > 1000 else '')
            st.code(display_code, language='python', line_numbers=True)
        
        with col2:
            st.markdown("#### 📊 Code Metrics")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    st.metric(label=key.replace('_', ' ').title(), value=value)

def export_section(results):
    """Export functionality"""
    st.markdown("## 📥 Export & Share")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        report = "CodeGuard AI - Plagiarism Report\n" + "="*40 + "\n\n"
        if results and 'pairs' in results:
            for pair in results['pairs']:
                report += f"{pair['file1']} vs {pair['file2']}: {pair['final_similarity']}%\n"
        
        st.download_button(
            label="📄 TXT Report",
            data=report,
            file_name="report.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 New Scan", use_container_width=True):
            st.session_state.results = None
            st.rerun()
    
    with col3:
        if st.button("📋 Copy Results", use_container_width=True):
            st.toast("✅ Copied to clipboard!", icon="📋")
    
    with col4:
        if st.button("💾 Save Session", use_container_width=True):
            st.toast("✅ Session saved!", icon="💾")

def ai_insights_box(results):
    """Display AI-generated insights"""
    if not results or 'pairs' not in results:
        return
    
    st.markdown("## 🤖 AI Insights")
    
    pairs = results['pairs']
    stats = results.get('statistics', {})
    
    high_pairs = [p for p in pairs if p['severity'] == 'high']
    
    insights = []
    
    if len(high_pairs) > 0:
        insights.append(f"🚨 **{len(high_pairs)} file pairs** show dangerously high similarity (>70%). Immediate investigation recommended.")
    
    if stats.get('avg_similarity', 0) > 50:
        insights.append(f"📈 The overall similarity average is **{stats['avg_similarity']}%**, which is above normal thresholds.")
    
    if stats.get('medium_similarity', 0) > 3:
        insights.append(f"⚠️ **{stats['medium_similarity']} pairs** show moderate similarity. Manual review suggested.")
    
    if len(high_pairs) == 0 and stats.get('medium_similarity', 0) == 0:
        insights.append("✅ **All clear!** No suspicious similarities detected. All files appear to be original work.")
    
    if stats.get('total_pairs', 0) > 10:
        insights.append(f"📊 Large dataset detected: **{stats['total_pairs']} comparisons** performed across {results.get('n_files', '?')} files.")
    
    for i, insight in enumerate(insights[:5]):
        st.markdown(f"""
            <div class='glass-card' style='padding: 1rem; margin: 0.5rem 0;'>
                <p style='margin: 0; font-size: 0.95rem;'>{insight}</p>
            </div>
        """, unsafe_allow_html=True)

def history_section(history):
    """Display recent analysis history"""
    if not history:
        return
    
    st.markdown("## 📚 Recent Analyses")
    
    cols = st.columns(min(len(history), 3))
    
    for i, (col, analysis) in enumerate(zip(cols, history[-3:])):
        with col:
            stats = analysis.get('statistics', {})
            high = stats.get('high_similarity', 0)
            risk_color = '#FF3B30' if high > 0 else '#34C759'
            risk_icon = '🚨' if high > 0 else '✅'
            
            st.markdown(f"""
                <div class='glass-card' style='padding: 1rem; text-align: center;'>
                    <h4 style='color: #00FFAA; margin: 0;'>🔍 Batch #{i+1}</h4>
                    <p style='color: #888; font-size: 0.8rem; margin: 0.5rem 0;'>
                        Files: {analysis.get('n_files', 0)}<br>
                        Pairs: {stats.get('total_pairs', 0)}<br>
                        Avg: {stats.get('avg_similarity', 0)}%
                    </p>
                    <p style='color: {risk_color}; font-size: 1.5rem; margin: 0;'>
                        {risk_icon}
                    </p>
                    <p style='color: {risk_color}; font-size: 0.9rem; margin: 0;'>
                        {high} high risk
                    </p>
                </div>
            """, unsafe_allow_html=True)
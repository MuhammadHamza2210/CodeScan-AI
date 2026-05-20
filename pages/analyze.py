import streamlit as st
import time
from datetime import datetime
from config import HAS_ZSS, HAS_TRANSFORMERS, HAS_SKLEARN
from engines.type_agnostic import type_normalizer
from engines.tree_edit_distance import ted_engine
from engines.control_flow import cfg_engine
from engines.winnowing import winnowing_engine, WinnowingFingerprint
from engines.codebert_engine import codebert_analyzer, CodeBERTAnalyzer
from engines.ml_classifier import ml_classifier, add_training_example
from utils import *
from ui_components import badge, score_ring, stat_row, mini_bar, diff_viewer
from report import generate_report, generate_html_report
from database import db  # ADD THIS IMPORT

def detect_plagiarism(code_a: str, code_b: str, method: str, sensitivity: int, language: str) -> dict:
    settings = st.session_state["settings"]

    norm_a = normalize_code(code_a, language)
    norm_b = normalize_code(code_b, language)
    tok_a = get_tokens(norm_a)
    tok_b = get_tokens(norm_b)

    seq_sim = sequence_similarity(norm_a, norm_b) * 100
    jac_sim = jaccard_similarity(set(tok_a), set(tok_b)) * 100
    ngram_sim = ngram_similarity(tok_a, tok_b, n=4) * 100
    ast_sim = ast_similarity(code_a, code_b) * 100 if language == "Python" else 0

    if settings.get("use_type_agnostic", True):
        ta_a = type_normalizer.normalize(code_a, language)
        ta_b = type_normalizer.normalize(code_b, language)
        ta_norm_a = normalize_code(ta_a, language)
        ta_norm_b = normalize_code(ta_b, language)
        ta_tok_a = get_tokens(ta_norm_a)
        ta_tok_b = get_tokens(ta_norm_b)
        ta_seq_sim = sequence_similarity(ta_norm_a, ta_norm_b) * 100
        ta_jac_sim = jaccard_similarity(set(ta_tok_a), set(ta_tok_b)) * 100
    else:
        ta_seq_sim = 0
        ta_jac_sim = 0

    bytecode_sim = bytecode_similarity(code_a, code_b) if settings.get("use_bytecode", True) else 0
    big_o_match = big_o_similarity(code_a, code_b) if settings.get("use_big_o", True) else 0

    ted_result = ted_engine.compute_ted(code_a, code_b) if settings.get("use_ast_ted", True) and HAS_ZSS else None
    ted_sim = ted_result if ted_result is not None and ted_result > 0.0 else 0.0

    cfg_sim = cfg_engine.compare_cfgs(
        cfg_engine.build_cfg(code_a),
        cfg_engine.build_cfg(code_b)
    ) if settings.get("use_cfg", True) else 0

    if settings.get("use_winnowing", True):
        fp_a = winnowing_engine.generate_fingerprint(code_a)
        fp_b = winnowing_engine.generate_fingerprint(code_b)
        winnowing_sim = winnowing_engine.compare_fingerprints(fp_a, fp_b)
    else:
        winnowing_sim = 0

    if settings.get("use_codebert", True) and codebert_analyzer.is_available():
        emb_a = codebert_analyzer.encode(code_a[:512])
        emb_b = codebert_analyzer.encode(code_b[:512])
        cb_result = codebert_analyzer.cosine_similarity(emb_a, emb_b)
        codebert_sim = cb_result if cb_result is not None and cb_result > 0.0 else 0.0
    else:
        codebert_sim = 0.0

    all_metrics = {
        'type_agnostic_seq_sim': ta_seq_sim,
        'type_agnostic_jac_sim': ta_jac_sim,
        'ted_sim': ted_sim,
        'cfg_sim': cfg_sim,
        'winnowing_sim': winnowing_sim,
        'codebert_sim': codebert_sim,
        'bytecode_sim': bytecode_sim,
        'big_o_match': big_o_match,
        'ast_sim': ast_sim,
        'seq_sim': seq_sim,
        'jac_sim': jac_sim,
        'ngram_sim': ngram_sim,
    }

    active_metrics = {}
    dead_engines = []

    for metric_name, metric_value in all_metrics.items():
        if metric_value is not None and metric_value > 0.0:
            active_metrics[metric_name] = metric_value
        else:
            dead_engines.append(metric_name)

    if len(active_metrics) >= 4:
        values = list(active_metrics.values())
        values.sort()
        median = values[len(values) // 2]
        filtered_metrics = {}
        for k, v in active_metrics.items():
            if abs(v - median) <= 60:
                filtered_metrics[k] = v
        if filtered_metrics:
            active_metrics = filtered_metrics

    weights = {
        'bytecode_sim': 3.5, 'big_o_match': 3.5, 'ted_sim': 3.0,
        'cfg_sim': 2.5, 'codebert_sim': 3.0, 'type_agnostic_jac_sim': 2.0,
        'type_agnostic_seq_sim': 1.5, 'ast_sim': 2.0, 'winnowing_sim': 1.5,
        'jac_sim': 0.5, 'seq_sim': 0.3, 'ngram_sim': 0.3,
    }

    if not active_metrics:
        final_score = 0.0
    else:
        weighted_sum = 0.0
        total_weight = 0.0
        median_val = sorted(active_metrics.values())[len(active_metrics) // 2]
        for metric_name, metric_value in active_metrics.items():
            w = weights.get(metric_name, 1.0)
            distance_from_median = abs(metric_value - median_val)
            if distance_from_median < 20:
                w *= 1.3
            weighted_sum += metric_value * w
            total_weight += w
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    final_score = round(final_score, 2)

    ml_verdict = None
    ml_confidence = 0.0
    if settings.get("use_ml", True) and ml_classifier.is_trained:
        ml_verdict, ml_confidence = ml_classifier.predict(all_metrics)

    threshold = sensitivity
    if final_score >= threshold:
        verdict = "PLAGIARIZED"
        risk = "High"
    elif final_score >= threshold * 0.6:
        verdict = "SUSPICIOUS"
        risk = "Medium"
    else:
        verdict = "ORIGINAL"
        risk = "Low"

    if ml_verdict and ml_confidence > 75:
        if ml_verdict == "PLAGIARIZED" and final_score >= threshold * 0.5:
            verdict = "PLAGIARIZED"
            risk = "High"

    result = {
        **all_metrics,
        "score": final_score,
        "verdict": verdict,
        "risk": risk,
        "ml_verdict": ml_verdict,
        "ml_confidence": round(ml_confidence, 2),
        "diff": get_diff_lines(code_a, code_b),
        "shared_tokens": len(set(tok_a) & set(tok_b)),
        "unique_a": len(set(tok_a) - set(tok_b)),
        "unique_b": len(set(tok_b) - set(tok_a)),
        "fingerprint_a": compute_fingerprint(code_a),
        "fingerprint_b": compute_fingerprint(code_b),
        "tokens_a": len(tok_a),
        "tokens_b": len(tok_b),
        "lines_a": len(code_a.splitlines()),
        "lines_b": len(code_b.splitlines()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engines_used": len(active_metrics),
        "dead_engines": dead_engines,
    }

    if settings.get("use_ml", True) and len(st.session_state["training_data"]) < 100:
        if final_score > 80 or final_score < 20:
            add_training_example(all_metrics, verdict)

    return result


def page_analyze():
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
        <span style="font-size:11px;color:rgba(255,255,255,0.25);letter-spacing:1.5px;text-transform:uppercase;font-family:'DM Sans',sans-serif;">6-Engine Ultimate Detection</span>
      </div>
      <h1 style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#e8e8f0;margin:0;line-height:1.2;">Analyze Code Similarity</h1>
      <p style="color:rgba(255,255,255,0.35);font-size:13px;font-family:'DM Sans',sans-serif;margin-top:6px;">Decision Tree • Tree Edit Distance • CFG • Winnowing • CodeBERT • Type-Agnostic Normalization</p>
    </div>
    """, unsafe_allow_html=True)

    s = st.session_state["settings"]
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        lang = st.selectbox("Language", ["Python", "Java", "C++", "C", "JavaScript", "Other"], index=["Python","Java","C++","C","JavaScript","Other"].index(s["language"]))
    with c2:
        method = st.selectbox("Method", ["Hybrid (All Engines)", "Standard Only", "Advanced Only"], index=0)
    with c3:
        sensitivity = st.slider("Sensitivity", 40, 95, s["sensitivity"], 5)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 0 20px 0;"></div>', unsafe_allow_html=True)

    input_tab1, input_tab2 = st.tabs(["✏  Paste Code", "📁  Upload Files"])
    code_a, code_b = "", ""

    with input_tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        cola, colb = st.columns(2)
        with cola:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;"><div style="width:8px;height:8px;background:#7c6dfa;border-radius:50%;"></div><span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Code Snippet A</span></div>""", unsafe_allow_html=True)
            code_a = st.text_area("Code A", height=280, placeholder="# Paste first code snippet here...", label_visibility="collapsed", key="code_a_text") or ""
        with colb:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;"><div style="width:8px;height:8px;background:#a78bfa;border-radius:50%;"></div><span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Code Snippet B</span></div>""", unsafe_allow_html=True)
            code_b = st.text_area("Code B", height=280, placeholder="# Paste second code snippet here...", label_visibility="collapsed", key="code_b_text") or ""

    with input_tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;"><div style="width:8px;height:8px;background:#7c6dfa;border-radius:50%;"></div><span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Upload File A</span></div>""", unsafe_allow_html=True)
            file_a = st.file_uploader("File A", type=["py","java","cpp","c","js","txt"], label_visibility="collapsed", key="file_a")
            if file_a:
                code_a = file_a.read().decode("utf-8", errors="replace")
                st.markdown(f"<div style='margin-top:8px;'>{badge(file_a.name, '#34d399')}</div>", unsafe_allow_html=True)
        with fc2:
            st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;"><div style="width:8px;height:8px;background:#a78bfa;border-radius:50%;"></div><span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;color:#e8e8f0;">Upload File B</span></div>""", unsafe_allow_html=True)
            file_b = st.file_uploader("File B", type=["py","java","cpp","c","js","txt"], label_visibility="collapsed", key="file_b")
            if file_b:
                code_b = file_b.read().decode("utf-8", errors="replace")
                st.markdown(f"<div style='margin-top:8px;'>{badge(file_b.name, '#34d399')}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    bcol1, bcol2, bcol3 = st.columns([3, 2, 3])
    with bcol2:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        run = st.button("⬡  Run Full Analysis (6 Engines)", use_container_width=True, key="run_btn")
        st.markdown("</div>", unsafe_allow_html=True)

    if run:
        if not code_a.strip() or not code_b.strip():
            st.warning("⚠  Please provide both code snippets.")
        else:
            with st.spinner("Running all 6 detection engines..."):
                time.sleep(1.0)
                result = detect_plagiarism(code_a, code_b, method, sensitivity, lang)
            
            st.session_state["last_result"] = result
            
            if s["save_history"]:
                # Save to session state (for current session)
                entry = {**result, "lang": lang, "method": method, "code_a_preview": code_a[:120], "code_b_preview": code_b[:120]}
                st.session_state["history"].insert(0, entry)
                if len(st.session_state["history"]) > 100:
                    st.session_state["history"] = st.session_state["history"][:100]
                
                # Save to database (permanent) - ONLY if save_history is enabled
                try:
                    db.save_scan(result, code_a, code_b, "Code A", "Code B")
                except Exception as e:
                    st.sidebar.error(f"Database save error: {str(e)[:50]}")
    
    result = st.session_state.get("last_result")
    if result:
        v_color = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(result["verdict"], "#7c6dfa")
        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:24px 0 20px 0;"></div>', unsafe_allow_html=True)
        st.markdown(f"""<div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">⬡ Ultimate Analysis Results</div><div style="color:{v_color};font-size:11px;margin-bottom:16px;">{result.get('engines_used', 0)} Detection Engines Active</div>""", unsafe_allow_html=True)

        r1, r2 = st.columns([1, 2])
        with r1:
            st.markdown(score_ring(result["score"], result["verdict"]), unsafe_allow_html=True)
            st.markdown(stat_row([
                ("Tokens A", result["tokens_a"], "#7c6dfa"),
                ("Tokens B", result["tokens_b"], "#a78bfa"),
                ("Shared", result["shared_tokens"], "#34d399"),
            ]), unsafe_allow_html=True)
            if result.get("ml_verdict"):
                st.markdown(f"""<div style="text-align:center;margin-top:8px;">{badge("ML: " + result["ml_verdict"], "#ec4899")}</div>""", unsafe_allow_html=True)

        with r2:
            st.markdown(f"""
            <div style="background:#18181e;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:22px 24px;margin-bottom:14px;">
              <div style="font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:1px;text-transform:uppercase;font-family:'DM Sans',sans-serif;margin-bottom:14px;">All Detection Engines</div>
              <div style="margin-bottom:10px;padding:6px;background:rgba(124,109,250,0.1);border-radius:6px;">
                <span style="font-size:11px;color:#a78bfa;">🔬 Enhanced CFG: Try/Except + Call Detection Enabled</span>
              </div>
              {mini_bar("Type-Agnostic Sequence", result.get('type_agnostic_seq_sim', 0), "#a78bfa")}
              {mini_bar("Type-Agnostic Jaccard", result.get('type_agnostic_jac_sim', 0), "#c4b5fd")}
              {mini_bar("Tree Edit Distance (AST)", result.get('ted_sim', 0), "#f59e0b")}
              {mini_bar("Control Flow Graph (Deepened)", result.get('cfg_sim', 0), "#ef4444")}
              {mini_bar("Winnowing (MOSS)", result.get('winnowing_sim', 0), "#8b5cf6")}
              {mini_bar("CodeBERT Semantic", result.get('codebert_sim', 0), "#ec4899")}
              {mini_bar("Bytecode", result.get('bytecode_sim', 0), "#06b6d4")}
              {mini_bar("Big O Match", result.get('big_o_match', 0), "#10b981")}
              {mini_bar("AST Structure", result.get('ast_sim', 0), "#84cc16")}
              {mini_bar("Sequence", result.get('seq_sim', 0), "#6366f1")}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            st.download_button("📄 TXT Report", generate_report(result, code_a, code_b), f"codescan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", use_container_width=True)
        with exp_col2:
            st.download_button("🌐 HTML Report", generate_html_report(result, code_a, code_b), f"codescan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html", use_container_width=True)
        with exp_col3:
            if st.button("📋 Copy Score", use_container_width=True):
                st.toast(f"Score: {result['score']:.1f}%", icon="📋")

        with st.expander("⬡  View Unified Diff"):
            st.markdown(diff_viewer(result["diff"]), unsafe_allow_html=True)

        if result["verdict"] == "PLAGIARIZED":
            st.error(f"🔴 **PLAGIARISM DETECTED** — Score: {result['score']:.1f}% (Threshold: {sensitivity}%)")
        elif result["verdict"] == "SUSPICIOUS":
            st.warning(f"🟡 **SUSPICIOUS** — Score: {result['score']:.1f}%")
        else:
            st.success(f"🟢 **ORIGINAL** — Score: {result['score']:.1f}%")
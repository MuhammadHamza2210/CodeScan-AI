from datetime import datetime

def generate_report(result: dict, code_a: str, code_b: str) -> str:
    report = f"""
╔══════════════════════════════════════════╗
║   CODESCAN AI — ULTIMATE PLAGIARISM    ║
║   Multi-Engine Detection Report        ║
╚══════════════════════════════════════════╝

Generated: {result['timestamp']}
Detection Engines Active: {result.get('engines_used', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FINAL VERDICT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Similarity Score:  {result['score']:.1f}%
  Verdict:           {result['verdict']}
  Risk Level:        {result['risk']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ALL DETECTION METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Type-Agnostic Seq:     {result.get('type_agnostic_seq_sim', 0):.1f}%
  Type-Agnostic Jaccard: {result.get('type_agnostic_jac_sim', 0):.1f}%
  Tree Edit Distance:    {result.get('ted_sim', 0):.1f}%
  Control Flow Graph:    {result.get('cfg_sim', 0):.1f}%
  Winnowing (MOSS):      {result.get('winnowing_sim', 0):.1f}%
  CodeBERT Semantic:     {result.get('codebert_sim', 0):.1f}%
  Bytecode:              {result.get('bytecode_sim', 0):.1f}%
  Big O Match:           {result.get('big_o_match', 0):.1f}%
  AST Structure:         {result.get('ast_sim', 0):.1f}%
  Sequence:              {result.get('seq_sim', 0):.1f}%

═══════════════════════════════════════════
  CodeScan AI Ultimate Edition © 2026
═══════════════════════════════════════════
"""
    return report


def generate_html_report(result: dict, code_a: str, code_b: str) -> str:
    v_color = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(
        result["verdict"], "#7c6dfa"
    )
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CodeScan AI — Ultimate Plagiarism Report</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0a0a0c; color: #e8e8f0; padding: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #7c6dfa; font-size: 28px; margin: 0; }}
        .section {{ background: #18181e; border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 24px; margin: 16px 0; }}
        .section h3 {{ color: #a78bfa; font-size: 14px; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 1px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        table td {{ padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 13px; }}
        table td:first-child {{ color: #6b6b80; width: 40%; }}
        table td:last-child {{ color: #e8e8f0; font-weight: 600; text-align: right; }}
        .verdict {{ display: inline-block; padding: 8px 24px; border-radius: 8px; font-weight: 700; background: {v_color}22; color: {v_color}; border: 2px solid {v_color}55; }}
        .score {{ font-size: 48px; font-weight: 900; color: {v_color}; text-align: center; }}
        .footer {{ text-align: center; color: #4a4a5a; font-size: 11px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⬡ CodeScan AI — Plagiarism Report</h1>
        <p>Generated: {result['timestamp']}</p>
    </div>
    <div class="score">{result['score']:.1f}%</div>
    <div style="text-align:center;margin:16px 0;"><span class="verdict">{result['verdict']}</span></div>
    <div class="section">
        <h3>Detection Metrics</h3>
        <table>
            <tr><td>Type-Agnostic Sequence</td><td>{result.get('type_agnostic_seq_sim', 0):.1f}%</td></tr>
            <tr><td>Type-Agnostic Jaccard</td><td>{result.get('type_agnostic_jac_sim', 0):.1f}%</td></tr>
            <tr><td>Tree Edit Distance</td><td>{result.get('ted_sim', 0):.1f}%</td></tr>
            <tr><td>Control Flow Graph</td><td>{result.get('cfg_sim', 0):.1f}%</td></tr>
            <tr><td>Winnowing (MOSS)</td><td>{result.get('winnowing_sim', 0):.1f}%</td></tr>
            <tr><td>CodeBERT Semantic</td><td>{result.get('codebert_sim', 0):.1f}%</td></tr>
            <tr><td>Bytecode</td><td>{result.get('bytecode_sim', 0):.1f}%</td></tr>
            <tr><td>Big O Match</td><td>{result.get('big_o_match', 0):.1f}%</td></tr>
        </table>
    </div>
    <div class="footer">⬡ CodeScan AI Ultimate Edition © 2026</div>
</body>
</html>
"""
    return html 

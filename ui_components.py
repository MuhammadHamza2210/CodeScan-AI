import math
import streamlit as st

def generate_heatmap(filenames: list, results: list) -> str:
    n = len(filenames)
    matrix = [[0.0] * n for _ in range(n)]
    for na, nb, score, _ in results:
        i = filenames.index(na)
        j = filenames.index(nb)
        matrix[i][j] = score
        matrix[j][i] = score

    def heat_color(val):
        if val >= 70:
            return f"rgba(248,113,113,{val / 100})"
        elif val >= 40:
            return f"rgba(251,191,36,{val / 100})"
        else:
            return f"rgba(52,211,153,{val / 100})"

    html = '<table class="heatmap-table"><tr><th></th>'
    for f in filenames:
        html += f'<th>{f[:10]}</th>'
    html += '</tr>'
    for i, row in enumerate(matrix):
        html += f'<tr><td style="color:#6b6b80;">{filenames[i][:10]}</td>'
        for val in row:
            html += f'<td style="background:{heat_color(val)};color:#fff;">{val:.0f}</td>'
        html += '</tr>'
    html += '</table>'
    return html

def badge(label: str, color: str = "#7c6dfa") -> str:
    return f"""<span style="display:inline-block;background:{color}22;color:{color};border:1px solid {color}55;border-radius:6px;padding:2px 10px;font-size:11px;font-family:'DM Sans',sans-serif;font-weight:600;letter-spacing:.5px;text-transform:uppercase;">{label}</span>"""


def score_ring(score: float, verdict: str) -> str:
    color = {"PLAGIARIZED": "#f87171", "SUSPICIOUS": "#fbbf24", "ORIGINAL": "#34d399"}.get(verdict, "#7c6dfa")
    radius = 54
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - score / 100)
    return f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:10px;padding:20px 0;">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="{color}" stroke-width="10" stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}" stroke-linecap="round" transform="rotate(-90 70 70)" style="transition:stroke-dashoffset 1s ease;filter:drop-shadow(0 0 8px {color}88)"/>
        <text x="70" y="66" text-anchor="middle" font-family="Syne,sans-serif" font-size="22" font-weight="700" fill="{color}">{score:.0f}%</text>
        <text x="70" y="84" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="10" fill="rgba(255,255,255,0.4)" letter-spacing="1.5">SIMILARITY</text>
      </svg>
      <div style="background:{color}22;color:{color};border:1px solid {color}55;border-radius:8px;padding:5px 20px;font-family:'Syne',sans-serif;font-size:13px;font-weight:700;letter-spacing:1.5px;">{verdict}</div>
    </div>"""


def mini_bar(label: str, value: float, color: str = "#7c6dfa") -> str:
    return f"""
    <div style="margin-bottom:10px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-size:12px;color:rgba(255,255,255,0.5);font-family:'DM Sans',sans-serif;">{label}</span>
        <span style="font-size:12px;color:rgba(255,255,255,0.8);font-family:'JetBrains Mono',monospace;font-weight:500;">{value:.1f}%</span>
      </div>
      <div style="height:5px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;">
        <div style="height:100%;width:{value}%;background:{color};border-radius:3px;box-shadow:0 0 6px {color}88;transition:width .8s ease;"></div>
      </div>
    </div>"""


def diff_viewer(diff_lines: list) -> str:
    if not diff_lines:
        return "<p style='color:var(--muted);font-size:12px;'>No differences found.</p>"
    html = """<div style="font-family:'JetBrains Mono',monospace;font-size:11.5px;background:#0d0d10;border-radius:10px;padding:16px;overflow-x:auto;border:1px solid rgba(255,255,255,0.06);max-height:340px;overflow-y:auto;">"""
    for line in diff_lines[:120]:
        esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if line.startswith('+++') or line.startswith('---'):
            html += f'<div style="color:#6b6b80;padding:1px 0;">{esc}</div>'
        elif line.startswith('+'):
            html += f'<div style="color:#34d399;background:#34d39912;padding:1px 4px;border-radius:2px;">{esc}</div>'
        elif line.startswith('-'):
            html += f'<div style="color:#f87171;background:#f8717112;padding:1px 4px;border-radius:2px;">{esc}</div>'
        elif line.startswith('@@'):
            html += f'<div style="color:#7c6dfa;padding:2px 0;">{esc}</div>'
        else:
            html += f'<div style="color:rgba(255,255,255,0.35);padding:1px 0;">{esc}</div>'
    html += "</div>"
    return html


def stat_row(items: list) -> str:
    cols = "".join(
        f"""<div style="flex:1;text-align:center;padding:12px 8px;background:rgba(255,255,255,0.03);border-radius:10px;margin:0 4px;"><div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;color:{c};">{v}</div><div style="font-size:10px;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:.8px;margin-top:3px;font-family:'DM Sans',sans-serif;">{l}</div></div>"""
        for l, v, c in items
    )
    return f'<div style="display:flex;gap:6px;margin-top:4px;">{cols}</div>'
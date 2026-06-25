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

def badge(label: str, color: str = "#22d3ee") -> str:
    return f"""<span style="display:inline-block;background:{color}1a;color:{color};border:1px solid {color}66;border-radius:4px;padding:3px 11px;font-size:10.5px;font-family:'JetBrains Mono',monospace;font-weight:600;letter-spacing:1px;text-transform:uppercase;box-shadow:0 0 12px {color}33;text-shadow:0 0 8px {color}88;">[ {label} ]</span>"""


def score_ring(score: float, verdict: str) -> str:
    color = {"PLAGIARIZED": "#ff3b5c", "SUSPICIOUS": "#ffb627", "ORIGINAL": "#00ff9c"}.get(verdict, "#22d3ee")
    radius = 54
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - score / 100)
    return f"""
    <div style="display:flex;flex-direction:column;align-items:center;gap:12px;padding:18px 0;">
      <svg width="150" height="150" viewBox="0 0 150 150">
        <circle cx="75" cy="75" r="{radius}" fill="none" stroke="rgba(34,211,238,0.10)" stroke-width="3"/>
        <circle cx="75" cy="75" r="{radius}" fill="none" stroke="rgba(34,211,238,0.06)" stroke-width="11"/>
        <circle cx="75" cy="75" r="{radius}" fill="none" stroke="{color}" stroke-width="6" stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}" stroke-linecap="round" transform="rotate(-90 75 75)" style="transition:stroke-dashoffset 1s ease;filter:drop-shadow(0 0 10px {color})"/>
        <text x="75" y="71" text-anchor="middle" font-family="Orbitron,sans-serif" font-size="28" font-weight="700" fill="{color}" style="filter:drop-shadow(0 0 8px {color});">{score:.0f}%</text>
        <text x="75" y="90" text-anchor="middle" font-family="'Share Tech Mono',monospace" font-size="9" fill="rgba(143,182,196,0.8)" letter-spacing="2.5">SIMILARITY</text>
      </svg>
      <div style="background:{color}1a;color:{color};border:1px solid {color};border-radius:4px;padding:6px 22px;font-family:'Orbitron',sans-serif;font-size:13px;font-weight:700;letter-spacing:2px;box-shadow:0 0 18px {color}55, inset 0 0 12px {color}22;text-shadow:0 0 10px {color};">{verdict}</div>
    </div>"""


def mini_bar(label: str, value: float, color: str = "#22d3ee") -> str:
    filled = int(round(value / 5))
    segs = "".join(
        f'<span style="flex:1;height:100%;border-radius:1px;background:{color if i < filled else "rgba(34,211,238,0.08)"};box-shadow:{f"0 0 6px {color}aa" if i < filled else "none"};"></span>'
        for i in range(20)
    )
    return f"""
    <div style="margin-bottom:11px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
        <span style="font-size:11px;color:rgba(143,182,196,0.85);font-family:'JetBrains Mono',monospace;letter-spacing:.5px;">{label}</span>
        <span style="font-size:11px;color:{color};font-family:'JetBrains Mono',monospace;font-weight:600;text-shadow:0 0 8px {color}66;">{value:.1f}%</span>
      </div>
      <div style="display:flex;gap:2px;height:8px;">{segs}</div>
    </div>"""


def diff_viewer(diff_lines: list) -> str:
    if not diff_lines:
        return "<p style='color:var(--muted);font-size:12px;'>No differences found.</p>"
    html = """<div style="font-family:'JetBrains Mono',monospace;font-size:11.5px;background:#04080e;border-radius:4px;padding:16px;overflow-x:auto;border:1px solid rgba(34,211,238,0.14);max-height:340px;overflow-y:auto;">"""
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
        f"""<div style="flex:1;text-align:center;padding:12px 8px;background:rgba(34,211,238,0.04);border:1px solid rgba(34,211,238,0.14);border-radius:4px;margin:0 4px;"><div style="font-family:'Orbitron',sans-serif;font-size:20px;font-weight:700;color:{c};text-shadow:0 0 12px {c}66;">{v}</div><div style="font-size:9px;color:rgba(143,182,196,0.7);text-transform:uppercase;letter-spacing:1.2px;margin-top:4px;font-family:'JetBrains Mono',monospace;">{l}</div></div>"""
        for l, v, c in items
    )
    return f'<div style="display:flex;gap:6px;margin-top:4px;">{cols}</div>'
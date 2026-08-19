"""
Hand-authored neofetch-style SVG info card for DevShlok.
Each line fades + slides in with CSS keyframes, staggered top -> bottom.

Run with:
    python scripts/make_info_card.py            # animated
    STATIC=1 python scripts/make_info_card.py   # frozen frame (for preview)

Output: info-card.svg
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")

STATIC = bool(os.environ.get("STATIC"))

# ── edit these to match your actual details ──────────────────────────────────
TITLE     = "DevShlok"
SUBTITLE  = "shlok@github"

FIELDS = [
    ("Languages", "Python · Java · C/C++ · JS · TS · HTML/CSS · SQL"),
    ("Frameworks","TensorFlow · PyTorch · HuggingFace · React · Node.js · Flutter"),
    ("Tools",     "Git · MySQL · PostgreSQL · Spark · Kafka · Docker"),
    ("Platforms", "Linux · GitHub · GitLab · AWS · GCP · Ollama"),
    ("AI",        "Claude Code · MCPs · LangChain · RAG · VectorDB"),
    ("Data Eng",  "BigData · DevOps · MLOps · ETL/ELT · CI/CD · REST APIs"),
]
# ─────────────────────────────────────────────────────────────────────────────

W = 660
TITLEBAR_H = 30
PAD = 20
LINE_H = 26
FIELD_AREA_H = len(FIELDS) * LINE_H + PAD
CANVAS_H = TITLEBAR_H + PAD + LINE_H + PAD // 2 + FIELD_AREA_H + PAD

BG        = "#0d1117"
BG2       = "#111722"
FRAME     = "#30363d"
MUTED     = "#7d8590"
KEY_COL   = "#58a6ff"   # blue for key labels
VAL_COL   = "#e6edf3"   # near-white for values
TITLE_COL = "#39d353"   # green username
SUB_COL   = "#7d8590"

STAGGER   = 0.10   # seconds between each line
FADE_DUR  = 0.40

css_block = "" if STATIC else f"""<style>
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(8px); }}
  to   {{ opacity: 1; transform: translateY(0);   }}
}}
.row {{ opacity: 0; animation: fadeUp {FADE_DUR}s ease both; }}
</style>"""

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    css_block,
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
    '</linearGradient></defs>',
    f'<rect width="{W}" height="{CANVAS_H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{CANVAS_H-1}" rx="12" '
    f'fill="none" stroke="{FRAME}" stroke-width="1"/>',
    # title bar
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]

for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(
    f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
    f'text-anchor="middle">shlok@github: ~$ neofetch</text>'
)

# username + @ line
ty = TITLEBAR_H + PAD + LINE_H * 0.75

def row(idx, content, extra_cls=""):
    delay = idx * STAGGER
    if STATIC:
        return f'<text x="{PAD}" y="{ty + idx * LINE_H:.1f}" font-size="13">{content}</text>'
    return (
        f'<text class="row {extra_cls}" x="{PAD}" y="{ty + idx * LINE_H:.1f}" '
        f'font-size="13" style="animation-delay:{delay:.2f}s">{content}</text>'
    )

# title row
parts.append(row(0,
    f'<tspan fill="{TITLE_COL}" font-weight="700" font-size="15">{TITLE}</tspan>'
    f'<tspan fill="{MUTED}">@</tspan>'
    f'<tspan fill="{SUB_COL}">github</tspan>'
))

# separator bar
sep_y = ty + LINE_H * 1.1
parts.append(
    f'<line x1="{PAD}" y1="{sep_y:.1f}" x2="{W - PAD}" y2="{sep_y:.1f}" '
    f'stroke="{KEY_COL}" stroke-opacity="0.35" stroke-width="1"/>'
)

# field rows
for fi, (key, val) in enumerate(FIELDS):
    idx = fi + 1  # offset by title row
    key_escaped = key
    val_escaped = val
    content = (
        f'<tspan fill="{KEY_COL}" font-weight="600">{key_escaped}</tspan>'
        f'<tspan fill="{MUTED}">: </tspan>'
        f'<tspan fill="{VAL_COL}">{val_escaped}</tspan>'
    )
    parts.append(row(idx + 1, content))

parts.append("</svg>")

svg = "\n".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT}  ({len(svg)} bytes,  {W} x {CANVAS_H})")

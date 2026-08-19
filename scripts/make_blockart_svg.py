"""
Convert an existing ASCII/block-art text file into a self-typing terminal SVG.

Each line is revealed left-to-right with a SMIL clip-wipe + block cursor,
staggered top->bottom, then the whole thing freezes -- identical animation
to make_ascii_svg.py but reads from a pre-made text file instead of a photo.

The art uses Unicode block glyphs (█ ▓ ▒ ░) so we need a monospace font
that covers the Block Elements range (U+2580-U+259F).

    python scripts/make_blockart_svg.py [ascii-art.txt] [shlok-ascii.svg]
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "ascii-art.txt")
OUT  = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "shlok-ascii.svg")

STATIC = bool(os.environ.get("STATIC"))

# ── read the art ─────────────────────────────────────────────────────────────
with open(SRC, "r", encoding="utf-8") as f:
    raw_lines = f.read().splitlines()

# strip trailing blank lines but keep internal ones
while raw_lines and not raw_lines[-1].strip():
    raw_lines.pop()

# ── layout constants ──────────────────────────────────────────────────────────
ROWS   = len(raw_lines)
# measure the widest line (in characters)
COLS   = max(len(line) for line in raw_lines) if raw_lines else 100

# cell size for block glyphs: slightly wider than a standard ASCII cell so
# the blocks tile without gaps.  Tune CELL_W if the art looks stretched.
CELL_W   = 8.0    # px per character column
CELL_H   = 13.5   # px per row  (block glyphs are slightly squarer than ASCII)

PAD        = 20
TITLEBAR_H = 30
STATUS_H   = 30
ART_W      = COLS * CELL_W
ART_H      = ROWS * CELL_H
CANVAS_W   = int(ART_W + PAD * 2)
CANVAS_H   = int(TITLEBAR_H + ART_H + STATUS_H + PAD)

# ── colors ────────────────────────────────────────────────────────────────────
BG         = "#0d1117"
BG2        = "#111722"
FRAME      = "#30363d"
TITLE_TEXT = "#7d8590"
INK        = "#c9d1d9"   # glyph color  (single color → clean, not noisy)
CURSOR     = "#c9d1d9"

# ── animation timing ──────────────────────────────────────────────────────────
ROW_DUR = 0.08   # seconds per row wipe
STAGGER = 0.08   # stagger between rows (= ROW_DUR → single cursor sweeps down)

# ── SVG assembly ─────────────────────────────────────────────────────────────
art_top = TITLEBAR_H + PAD * 0.35

parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
    # DejaVu / Noto cover the block-elements range; ui-monospace as fallback
    f'font-family="\'DejaVu Sans Mono\', \'Noto Sans Mono\', '
    f'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
)

# gradient background + border
parts.append(
    '<defs>'
    f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/>'
    f'<stop offset="1" stop-color="{BG}"/>'
    '</linearGradient></defs>'
)
parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>')
parts.append(
    f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" '
    f'rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>'
)

# title bar
parts.append(
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" '
    f'y2="{TITLEBAR_H}" stroke="{FRAME}"/>'
)
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(
        f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>'
    )
parts.append(
    f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" '
    f'font-size="12" text-anchor="middle">shlok@github: ~$ ./portrait.sh</text>'
)

# one <text> per row with SMIL clip-wipe + cursor
font_size = CELL_H * 0.92   # slightly larger to fill the cell height

for ry, line in enumerate(raw_lines):
    y      = art_top + ry * CELL_H + CELL_H * 0.80
    row_y  = art_top + ry * CELL_H
    delay  = ry * STAGGER
    safe   = html.escape(line)
    row_w  = len(line) * CELL_W   # actual width of this specific line

    text_el = (
        f'<text xml:space="preserve" x="{PAD}" y="{y:.2f}" '
        f'fill="{INK}" font-size="{font_size:.1f}" '
        f'textLength="{ART_W:.1f}" lengthAdjust="spacing">{safe}</text>'
    )

    if STATIC:
        parts.append(text_el)
        continue

    # clip rect wipes left→right over ROW_DUR seconds
    parts.append(
        f'<clipPath id="r{ry}">'
        f'<rect x="{PAD}" y="{row_y:.2f}" height="{CELL_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W:.1f}" '
        f'begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
        f'</rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#r{ry})">{text_el}</g>')

    # block cursor rides the right edge of the wipe
    parts.append(
        f'<rect y="{row_y+1:.2f}" width="{CELL_W:.1f}" '
        f'height="{CELL_H-2:.1f}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W:.1f}" '
        f'begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/>'
        f'</rect>'
    )

# status bar
status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y      = status_line_y + 19
parts.append(
    f'<line x1="0" y1="{status_line_y:.1f}" '
    f'x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>'
)
parts.append(
    f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
    f'shlok@github:~$ whoami '
    f'<tspan fill="{INK}">DevShlok</tspan></text>'
)
# blinking cursor after the name
parts.append(
    f'<rect x="{PAD+179}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
    f'<animate attributeName="opacity" values="1;1;0;0" '
    f'keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>'
    f'</rect>'
)

parts.append("</svg>")
svg = "".join(parts)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT}  ({len(svg):,} bytes,  {CANVAS_W} × {CANVAS_H},  {ROWS} rows × {COLS} cols)")

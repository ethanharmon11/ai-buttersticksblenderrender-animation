"""Compose the flight intro's opening frame — vintage golf-poster style.

Eye-level with a cream golf ball marked "BSG" (real brand vectors), on a
stylized mid-century course: low horizon, flat trees, golden sun, paper
grain. Rendered by headless Chrome to reference/flight_start.png and fed
to Seedance 2.0 as --start-image so the whole video inherits the style.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = json.loads((ROOT / "gsap" / "groups.json").read_text(encoding="utf-8"))

CREAM = "#EADDC1"
BROWN = "#8C5E2E"
DARK = "#4B311A"
GOLDEN = "#D9B64E"
GREEN = "#21522A"
RUST = "#B15023"
GREEN_LIGHT = "#3A6B3F"   # sunlit fairway band
GREEN_MID = "#2C5C33"

# ---- ball geometry -------------------------------------------------------
BX, BY, BR = 640.0, 690.0, 215.0          # big, left-of-center, eye level
# bsg script bbox in badge coords (from extract_groups)
BSG_X0, BSG_Y0, BSG_X1, BSG_Y1 = 1611.4, 796.7, 1877.1, 960.9
BSG_CX, BSG_CY = (BSG_X0 + BSG_X1) / 2, (BSG_Y0 + BSG_Y1) / 2
S = (BR * 0.78) / ((BSG_X1 - BSG_X0) / 2)          # script ~78% of radius wide, inside the disc
TX, TY = BX - BSG_CX * S, BY - BSG_CY * S

bsg_paths = "\n".join(f'<path d="{p["d"]}" fill-rule="evenodd"/>' for p in G["bsg"])

# faint flat dimples on the upper-left quarter (poster style: sparse, subtle)
dimples = []
for r_, row in [(0.42, (-0.72, -0.30, 0.15)), (0.62, (-0.62, -0.18)), (0.80, (-0.45,))]:
    for a in row:
        dx, dy = BX + BR * r_ * a, BY - BR * (1 - r_ * 0.55) * 0.62
        dimples.append(f'<circle cx="{dx:.0f}" cy="{dy:.0f}" r="7" fill="#D8C9A6"/>')
DIMPLES = "\n".join(dimples)

HORIZON = BY  # true eye level: horizon crosses the ball's equator

svg = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>flight start frame</title>
<style>html,body{{margin:0;background:{CREAM};overflow:hidden}}</style></head><body>
<svg width="1920" height="1080" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" result="n"/>
      <feColorMatrix in="n" type="matrix"
        values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.6 0.6 0.6 0 0"/>
      <feComposite operator="in" in2="SourceGraphic"/>
    </filter>
    <radialGradient id="vig" cx="50%" cy="46%" r="75%">
      <stop offset="72%" stop-color="{DARK}" stop-opacity="0"/>
      <stop offset="100%" stop-color="{DARK}" stop-opacity="0.28"/>
    </radialGradient>
  </defs>

  <!-- sky -->
  <rect width="1920" height="{HORIZON}" fill="{CREAM}"/>
  <!-- sun, low and golden with poster ring -->
  <circle cx="1430" cy="330" r="128" fill="{GOLDEN}"/>
  <circle cx="1430" cy="330" r="128" fill="none" stroke="{CREAM}" stroke-width="10"/>
  <circle cx="1430" cy="330" r="150" fill="none" stroke="{GOLDEN}" stroke-width="6" opacity="0.55"/>
  <!-- flat clouds -->
  <g fill="#F4EAD3">
    <rect x="180" y="200" width="330" height="34" rx="17"/>
    <rect x="260" y="243" width="210" height="30" rx="15"/>
    <rect x="1050" y="140" width="260" height="30" rx="15"/>
  </g>

  <!-- distant course: layered fairway bands -->
  <rect x="0" y="{HORIZON - 4}" width="1920" height="8" fill="{DARK}" opacity="0.35"/>
  <rect x="0" y="{HORIZON}" width="1920" height="120" fill="{GREEN_LIGHT}"/>
  <rect x="0" y="{HORIZON + 120}" width="1920" height="150" fill="{GREEN_MID}"/>
  <rect x="0" y="{HORIZON + 270}" width="1920" height="{1080 - HORIZON - 270}" fill="{GREEN}"/>

  <!-- distant flat trees (lollipop poster trees) -->
  <g>
    <rect x="1706" y="{HORIZON - 74}" width="12" height="74" fill="{DARK}"/>
    <circle cx="1712" cy="{HORIZON - 104}" r="52" fill="{GREEN_MID}"/>
    <rect x="1590" y="{HORIZON - 52}" width="9" height="52" fill="{DARK}"/>
    <circle cx="1594" cy="{HORIZON - 74}" r="36" fill="{GREEN_LIGHT}"/>
    <rect x="112" y="{HORIZON - 60}" width="10" height="60" fill="{DARK}"/>
    <circle cx="117" cy="{HORIZON - 86}" r="42" fill="{GREEN_MID}"/>
  </g>
  <!-- distant bunker + flag -->
  <ellipse cx="1240" cy="{HORIZON + 74}" rx="130" ry="22" fill="{GOLDEN}" opacity="0.8"/>
  <g>
    <rect x="1585" y="{HORIZON + 6}" width="6" height="96" fill="{CREAM}"/>
    <path d="M1591 {HORIZON + 10} l64 16 -64 16 z" fill="{RUST}"/>
  </g>

  <!-- the ball: flat cream disc, crescent shade, dark outline -->
  <circle cx="{BX}" cy="{BY}" r="{BR}" fill="#F4EAD3"/>
  <path d="M {BX - BR * 0.1} {BY - BR}
           a {BR} {BR} 0 0 1 0 {BR * 2}
           a {BR * 1.32} {BR * 1.32} 0 0 0 0 {-BR * 2} z"
        fill="#D8C9A6" opacity="0.65"/>
  <circle cx="{BX}" cy="{BY}" r="{BR}" fill="none" stroke="{DARK}" stroke-width="8"/>
  {DIMPLES}

  <!-- BSG script, the real brand vectors, rust like the badge -->
  <g transform="translate({TX:.1f},{TY:.1f}) scale({S:.4f})" fill="{RUST}">
    {bsg_paths}
  </g>

  <!-- turf the ball sits in: grass blades at the base -->
  <g stroke="{DARK}" stroke-width="7" stroke-linecap="round" fill="none" opacity="0.9">
    <path d="M {BX - BR + 18} {BY + BR - 20} q -18 -22 -38 -28"/>
    <path d="M {BX - BR + 44} {BY + BR - 4} q -12 -26 -28 -34"/>
    <path d="M {BX + BR - 40} {BY + BR - 8} q 12 -26 30 -34"/>
    <path d="M {BX + BR - 68} {BY + BR - 22} q 16 -20 34 -26"/>
  </g>
  <ellipse cx="{BX}" cy="{BY + BR + 10}" rx="{BR * 1.12}" ry="26" fill="{DARK}" opacity="0.22"/>

  <!-- paper grain + vignette -->
  <rect width="1920" height="1080" filter="url(#grain)" opacity="0.10"/>
  <rect width="1920" height="1080" fill="url(#vig)"/>
</svg>
</body></html>
"""

out = ROOT / "gsap" / "flight_start.html"
out.write_text(svg, encoding="utf-8")
print(f"wrote {out}")

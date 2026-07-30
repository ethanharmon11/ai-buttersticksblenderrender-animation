"""Assemble gsap/intro.html — the Butter Sticks intro as a GSAP/SVG animation.

v2 "true liquid":
- fill-rule="evenodd" restored (letter counters render)
- the gold pat becomes a LIQUID: pat slab + ball-coat + slow runnels merged
  by a gooey filter into one molten mass; a dilated green copy underneath
  generates the brand outline from the liquid itself (the outline melts too)
- BSG stays in place, then liquefies (turbulence displacement) and dissolves
- ~9.2s total; slow ooze over the ball, gentle drops into the pond
Supports ?seek=<sec> for headless frame-grabs; prefers-reduced-motion jumps
to the final lockup; click to replay.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = json.loads((ROOT / "gsap" / "groups.json").read_text(encoding="utf-8"))
GSAP = (ROOT / "gsap" / "gsap.min.js").read_text(encoding="utf-8")

CREAM = "#EADDC1"
BROWN = "#8C5E2E"
GOLDEN = "#D9B64E"
DEEP = "#BD9A42"
GREEN = "#21522a"

# Ball geometry in native badge coords (from extraction bboxes)
BALL_CX, BALL_CY, BALL_R = 1742.1, 1104.6, 186


def paths(group, keep_fill=True, cls=""):
    out = []
    for it in G[group]:
        fill = f' fill="{it["fill"]}"' if keep_fill else ""
        c = f' class="{cls}"' if cls else ""
        out.append(f'<path d="{it["d"]}" fill-rule="evenodd"{fill}{c}/>')
    return "\n".join(out)


def wave(width=3600, x0=-1000, amp=30, wl=400, depth=1100):
    n = int(width / wl)
    seg = ""
    for _ in range(n):
        seg += f"q{wl / 4:.0f} {-amp} {wl / 2:.0f} 0 q{wl / 4:.0f} {amp} {wl / 2:.0f} 0 "
    return f"M{x0} 0 {seg} v{depth} h{-width} Z"


def molten_members(cls):
    """The liquid's building blocks; gooey filter merges them into one mass.
    Native badge coords. Same markup used for the gold body and green rim.
    Fringe drips hang under the pat body and later slide down the ball."""
    runnels = ""
    for i, (x0, drift) in enumerate([(1604, -50), (1676, -20), (1744, 0),
                                     (1814, 22), (1882, 52)]):
        runnels += (f'<ellipse class="{cls}Run{i}" cx="{x0}" cy="962" '
                    f'rx="{28 + (i % 3) * 5}" ry="34" data-drift="{drift}"/>\n')
    return f"""
    <rect class="{cls}Pat" x="1548" y="758" width="378" height="180" rx="24"/>
    <g clip-path="url(#coatClip)">
      <circle class="{cls}Coat" cx="{BALL_CX}" cy="{BALL_CY}" r="{BALL_R + 15}"/>
    </g>
    {runnels}"""


html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Butter Sticks Golf — Intro (GSAP/SVG)</title>
<style>
  html, body {{ margin: 0; height: 100%; background: {CREAM}; }}
  .stage {{ position: fixed; inset: 0; display: grid; place-items: center; }}
  svg {{ width: 100vw; height: 100vh; }}
</style>
</head>
<body>
<div class="stage">
<svg viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" aria-label="Butter Sticks Golf intro animation">
  <defs>
    <filter id="goo" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="b"/>
      <feColorMatrix in="b" mode="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -8"/>
    </filter>
    <filter id="gooRim" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="b"/>
      <feColorMatrix in="b" mode="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -8" result="thresh"/>
      <feMorphology in="thresh" operator="dilate" radius="10" result="fat"/>
      <feFlood flood-color="{GREEN}"/>
      <feComposite operator="in" in2="fat"/>
    </filter>
    <filter id="lettersMelt" x="-40%" y="-40%" width="180%" height="180%">
      <feTurbulence type="turbulence" baseFrequency="0.012 0.03" numOctaves="2" result="n"/>
      <feDisplacementMap id="dispMap" in="SourceGraphic" in2="n" scale="0"
        xChannelSelector="R" yChannelSelector="G"/>
    </filter>
    <clipPath id="coatClip">
      <path id="coatWave" d="M1520 600 H1968 V1062 q-37 24 -75 0 t-75 0 t-75 0 t-75 0 t-74 0 t-74 0 Z"/>
    </clipPath>
    <clipPath id="eraserClip">
      <rect id="eraserRect" x="1520" y="740" width="440" height="0"/>
    </clipPath>
  </defs>

  <rect id="bg" width="1600" height="900" fill="{CREAM}"/>

  <!-- gentle drops falling from the buttered ball into the pond -->
  <g id="dripLayer" filter="url(#goo)" fill="{GOLDEN}" transform="translate(105,22.3) scale(0.4)">
    <ellipse class="drop" cx="1688" cy="1112" rx="26" ry="34"/>
    <ellipse class="drop" cx="1748" cy="1120" rx="30" ry="38"/>
    <ellipse class="drop" cx="1806" cy="1110" rx="24" ry="32"/>
  </g>

  <!-- liquids -->
  <g id="pondBack"><path d="{wave(amp=34)}" fill="{DEEP}"/></g>
  <g id="pondFront"><path d="{wave(amp=26)}" fill="{GOLDEN}"/></g>
  <g id="tide"><path d="{wave(amp=38)}" fill="{BROWN}"/></g>

  <!-- the badge -->
  <g id="badgeMove">
    <g transform="translate(105,22.3) scale(0.4)">
      {paths("sil")}
      <!-- erases the emptied pat region (outline included) as butter departs -->
      <g clip-path="url(#eraserClip)"><g id="eraser" fill="{CREAM}" stroke="{CREAM}" stroke-width="9">{paths("sil", keep_fill=False)}</g></g>
      {paths("ball")}
      {paths("dimples_cream")}
      {paths("dimples_green")}
      <!-- hides the ball's sparkle accents once butter coats the crown -->
      <g id="hornCover" fill="{CREAM}" opacity="0">
        <rect x="1872" y="876" width="92" height="104" rx="14"/>
        <rect x="1522" y="886" width="84" height="90" rx="14"/>
      </g>
      <!-- original crisp artwork; crossfades into the liquid sim -->
      <g id="goldArt">{paths("gold")}</g>
      <!-- the molten butter: green rim generated from the liquid, gold body -->
      <g id="moltenRim" filter="url(#gooRim)" opacity="0">{molten_members("r")}</g>
      <g id="moltenGold" filter="url(#goo)" fill="{GOLDEN}" opacity="0">{molten_members("g")}</g>
      {paths("tee")}
      <g id="bsg" filter="url(#lettersMelt)">{paths("bsg")}</g>
      <g id="speed">{paths("speed")}</g>
    </g>
  </g>

  <!-- wordmark -->
  <g id="wmMove" transform="translate(551,452.6) scale(0.39)" fill="{CREAM}">
    <g id="wmButter">{paths("wm_butter", keep_fill=False)}</g>
    <g id="wmSticks">{paths("wm_sticks", keep_fill=False)}</g>
    <g id="wmGolf">{paths("wm_golf", keep_fill=False, cls="golfLetter")}</g>
  </g>
</svg>
</div>

<script>{GSAP}</script>
<script>
const $$ = (s) => gsap.utils.toArray(s);

gsap.set("#badgeMove", {{ autoAlpha: 0, scale: 0.92, transformOrigin: "50% 50%" }});
gsap.set(["#wmButter", "#wmSticks"], {{ autoAlpha: 0, y: 150 }});
gsap.set(".golfLetter", {{ autoAlpha: 0, y: 70 }});
gsap.set(".drop", {{ autoAlpha: 0 }});
gsap.set("#coatWave", {{ y: -185 }});
gsap.set(["#pondBack", "#pondFront", "#tide"], {{ y: 920 }});
gsap.set("svg", {{ scale: 1.07, transformOrigin: "50% 50%" }});
// runnels start tucked under the pat's bottom edge
gsap.set("[class*='Run']", {{ autoAlpha: 0 }});

// endless sideways drift on every liquid surface (wavelength = 400)
gsap.to("#pondBack path",  {{ x: -400, duration: 2.1, ease: "none", repeat: -1 }});
gsap.to("#pondFront path", {{ x: -400, duration: 2.8, ease: "none", repeat: -1 }});
gsap.to("#tide path",      {{ x: -400, duration: 2.4, ease: "none", repeat: -1 }});

const tl = gsap.timeline({{ defaults: {{ ease: "power2.out" }} }});

// ---- beat 1: arrival on cream (0 - 1.4s)
tl.addLabel("in", 0.15)
  .to("#badgeMove", {{ autoAlpha: 1, duration: 0.55, ease: "sine.out" }}, "in")
  .to("#badgeMove", {{ scale: 1.04, duration: 0.75, ease: "back.out(1.4)" }}, "in")
  .to("#badgeMove", {{ scale: 1.0, duration: 0.4 }}, "in+=0.78")
  .to("#badgeMove", {{ scaleY: 0.965, scaleX: 1.03, duration: 0.25, ease: "sine.inOut" }}, 1.3)
  .to("#badgeMove", {{ scaleY: 1, scaleX: 1, duration: 0.3, ease: "sine.out" }}, 1.56);

// ---- beat 2: the vector itself melts (1.6 - 4.6s) — slow ooze OVER the ball
tl.addLabel("melt", 1.6)
  // crisp art hands over to the liquid sim
  .to(["#moltenRim", "#moltenGold"], {{ opacity: 1, duration: 0.4, ease: "sine.inOut" }}, "melt")
  .to("#goldArt", {{ autoAlpha: 0, duration: 0.45, ease: "sine.inOut" }}, "melt+=0.1")
  .to("#speed", {{ autoAlpha: 0, duration: 0.4 }}, "melt+=0.1")
  // butter coats the ball's crown slowly, hugging the surface (stops ~45%)
  .to("#coatWave", {{ y: 0, duration: 2.8, ease: "power1.inOut" }}, "melt+=0.5")
  // the fringe drips wake up...
  .to("[class*='Run']", {{ autoAlpha: 1, duration: 0.4, stagger: 0.15 }}, "melt+=0.3")
  .to("#hornCover", {{ opacity: 1, duration: 0.5, ease: "sine.inOut" }}, "melt+=1.0");

// ...and become runnels sliding slowly down the ball, spreading with its curve
$$("[class*='Run']").forEach((r) => {{
  const drift = parseFloat(r.dataset.drift);
  const t0 = 0.9 + Math.abs(drift) / 80;
  tl.to(r, {{ attr: {{ cy: 1235, cx: "+=" + drift }}, scaleY: 1.6,
      transformOrigin: "50% 0%", duration: 2.4 + Math.abs(drift) / 55,
      ease: "sine.in" }}, "melt+=" + t0)
    .to(r, {{ autoAlpha: 0, duration: 0.4 }}, "melt+=" + (t0 + 2.3));
}});

// the pat slab empties from the top; its outline erases with it
tl.to([".rPat", ".gPat"], {{ scaleY: 0.16, transformOrigin: "50% 100%",
      duration: 1.8, ease: "power1.inOut" }}, "melt+=1.4")
  .to([".rPat", ".gPat"], {{ autoAlpha: 0, duration: 0.4 }}, "melt+=3.1")
  .to("#eraserRect", {{ attr: {{ height: 300 }}, duration: 1.8, ease: "power1.inOut" }}, "melt+=1.4")
  // BSG stays put, liquefies, and dissolves into the flow
  .to("#dispMap", {{ attr: {{ scale: 42 }}, duration: 1.1, ease: "sine.in" }}, "melt+=1.2")
  .to("#bsg", {{ autoAlpha: 0, duration: 0.8, ease: "sine.inOut" }}, "melt+=1.65");

// ---- beat 3: pond fills like a glass (3.4 - 4.9s)
tl.addLabel("pond", 3.4)
  .to("#pondBack", {{ y: 585, duration: 1.45, ease: "power1.inOut" }}, "pond")
  .to("#pondFront", {{ y: 606, duration: 1.45, ease: "power1.inOut" }}, "pond+=0.12");

// gentle drops from the buttered ball into the pond
$$(".drop").forEach((d, i) => {{
  [0, 1].forEach((w) => {{
    const t0 = 4.0 + i * 0.4 + w * 1.05;
    tl.fromTo(d, {{ autoAlpha: 1, y: 0, scaleY: 1, transformOrigin: "50% 0%" }},
      {{ y: 385, scaleY: 2.0, duration: 1.15, ease: "power1.in", immediateRender: false }}, t0)
      .to(d, {{ autoAlpha: 0, duration: 0.2 }}, t0 + 0.95);
  }});
}});

// ---- beat 4: the brown tide inversion (5.1 - 6.0s)
tl.addLabel("tideUp", 5.1)
  .to("#tide", {{ y: -85, duration: 0.9, ease: "power2.inOut" }}, "tideUp")
  // the erased pat region fakes the background; follow the tide's color
  .to(["#eraser", "#hornCover"], {{ fill: "{BROWN}", stroke: "{BROWN}", duration: 0.3, ease: "none" }}, "tideUp+=0.42");

// ---- beat 5: jelly settle + rise to lockup (6.0 - 6.9s)
tl.addLabel("settle", 6.0)
  .to("#badgeMove", {{ scaleY: 0.87, scaleX: 1.08, duration: 0.16, ease: "sine.in" }}, "settle")
  .to("#badgeMove", {{ scaleY: 1.05, scaleX: 0.97, duration: 0.18, ease: "sine.inOut" }}, "settle+=0.16")
  .to("#badgeMove", {{ scaleY: 1, scaleX: 1, duration: 0.24, ease: "sine.out" }}, "settle+=0.34")
  .to("#badgeMove", {{ y: -117.2, duration: 0.72, ease: "power2.inOut" }}, "settle+=0.18");

// ---- beat 6: wordmark reveal (6.6 - 8.2s)
tl.addLabel("type", 6.6)
  .to("#wmButter", {{ autoAlpha: 1, y: 0, duration: 0.6, ease: "power3.out" }}, "type")
  .to("#wmSticks", {{ autoAlpha: 1, y: 0, duration: 0.6, ease: "power3.out" }}, "type+=0.24")
  .to(".golfLetter", {{ autoAlpha: 1, y: 0, duration: 0.45, ease: "power2.out", stagger: 0.12 }}, "type+=0.6");

// ---- beat 7: breathing hold (8.4 - 9.2s)
tl.to("#badgeMove", {{ scale: 1.012, duration: 0.38, ease: "sine.inOut" }}, 8.4)
  .to("#badgeMove", {{ scale: 1.0, duration: 0.38, ease: "sine.inOut" }}, 8.78);

// slow camera push, whole film
tl.to("svg", {{ scale: 1.0, duration: 9.2, ease: "sine.out" }}, 0);

// reduced motion: land on the finished lockup immediately
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {{
  tl.progress(1).pause();
  gsap.set("#tide", {{ y: -85 }});
}}

// headless frame-grab support: ?seek=<seconds>
const seek = new URLSearchParams(location.search).get("seek");
if (seek !== null) {{
  tl.pause(parseFloat(seek));
  gsap.globalTimeline.pause();
}}
document.querySelector("svg").addEventListener("click", () => tl.restart());
window.introTimeline = tl;
</script>
</body>
</html>
"""

out = ROOT / "gsap" / "intro.html"
out.write_text(html, encoding="utf-8")
print(f"WROTE {out}  ({out.stat().st_size / 1024:.0f} KB incl. inlined GSAP)")

"""Assemble gsap/intro_putt.html — the stick-art putt intro:

A line-art putting scene draws itself on; a putter taps the ball; it
rolls across the green (no-slip rolling rotation) and drops in the cup;
the camera plunges into the hole; at the bottom, the ball rests in a
shaft of light with BSG on its face, and the wordmark surfaces.

Pure vector + GSAP. Builds gsap/intro_putt.html and the self-contained
gsap/intro_putt_artifact.html. ?seek=<sec>, reduced-motion, click replay.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = json.loads((ROOT / "gsap" / "groups.json").read_text(encoding="utf-8"))
GSAP = (ROOT / "gsap" / "gsap.min.js").read_text(encoding="utf-8")

CREAM = "#EADDC1"
GREEN = "#21522A"
RUST = "#B15023"
HOLE_DARK = "#2B1A0D"
INSIDE = "#3A2410"
GOLDEN = "#D9B64E"


def paths(group, keep_fill=True, cls=""):
    out = []
    for it in G[group]:
        fill = f' fill="{it["fill"]}"' if keep_fill else ""
        c = f' class="{cls}"' if cls else ""
        out.append(f'<path d="{it["d"]}" fill-rule="evenodd"{fill}{c}/>')
    return "\n".join(out)


# BSG letters fitted to the resting ball's face (ball center 800,470 r 150)
# bsg native bbox: x 1611.4-1877.1, y 796.7-960.9  -> center (1744.3, 878.8)
BSG_S = 0.62
BSG_TX = 800 - 1744.3 * BSG_S
BSG_TY = 470 - 878.8 * BSG_S

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Butter Sticks Golf — Putt Intro</title>
<style>
  html, body {{ margin: 0; height: 100%; background: {CREAM}; overflow: hidden; }}
  .stage {{ position: fixed; inset: 0; }}
  svg {{ width: 100vw; height: 100vh; }}
  .ln {{ fill: none; stroke: {GREEN}; stroke-linecap: round; stroke-linejoin: round; }}
</style>
</head>
<body>
<div class="stage">
<svg viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid meet" aria-label="Butter Sticks Golf intro: a putt rolls into the hole">
  <rect id="bg" width="1600" height="900" fill="{CREAM}"/>

  <!-- ACT 1: the putting green -->
  <g id="scene">
    <!-- green line, in two strokes leaving the cup gap -->
    <path id="turfL" class="ln" stroke-width="7"
      d="M140 562 C 380 554, 640 568, 900 560 S 1080 556, 1124 559"/>
    <path id="turfR" class="ln" stroke-width="7"
      d="M1180 559 C 1260 562, 1380 556, 1460 560"/>
    <!-- a few sketch blades of grass -->
    <path class="ln gr" stroke-width="5" d="M300 560 l-6 -22 M312 560 l5 -18"/>
    <path class="ln gr" stroke-width="5" d="M760 562 l-5 -20 M772 562 l6 -16"/>
    <path class="ln gr" stroke-width="5" d="M1330 559 l-5 -19 M1342 559 l5 -15"/>
    <!-- the cup -->
    <ellipse id="cupMouth" cx="1152" cy="560" rx="28" ry="9" fill="{HOLE_DARK}"/>
    <!-- flag -->
    <path id="pole" class="ln" stroke-width="6" d="M1152 552 V 336"/>
    <path id="flag" d="M1152 336 L1228 362 L1152 388 Z" fill="{RUST}"/>
    <!-- the ball (rolls) -->
    <g id="ball">
      <circle cx="0" cy="0" r="26" fill="{CREAM}" stroke="{GREEN}" stroke-width="6"/>
      <g id="ballSpin" fill="{GREEN}">
        <circle cx="-9" cy="-4" r="2.6"/><circle cx="8" cy="-7" r="2.6"/>
        <circle cx="2" cy="9" r="2.6"/>
      </g>
    </g>
    <!-- cup front lip covers the ball as it drops -->
    <path id="cupLip" d="M1124 559 A28 9 0 0 0 1180 559 L1180 585 L1124 585 Z" fill="{CREAM}" stroke="none"/>
    <ellipse id="cupRing" cx="1152" cy="560" rx="28" ry="9" fill="none" stroke="{GREEN}" stroke-width="6"/>
    <!-- the putter -->
    <g id="putter">
      <path class="ln" stroke-width="8" d="M404 214 L462 520"/>
      <path class="ln" stroke-width="8" d="M398 200 L410 262"/>
      <path class="ln" stroke-width="9" d="M446 530 Q470 546 502 540"/>
    </g>
    <!-- tap tick marks -->
    <g id="tick" class="ln" stroke-width="5" opacity="0">
      <path d="M540 486 l14 -12 M548 506 l18 -4"/>
    </g>
  </g>

  <!-- ACT 2: inside the hole -->
  <g id="inside" visibility="hidden">
    <rect width="1600" height="900" fill="{INSIDE}"/>
    <defs>
      <radialGradient id="beam" cx="0.5" cy="0" r="1">
        <stop offset="0" stop-color="{GOLDEN}" stop-opacity="0.55"/>
        <stop offset="0.45" stop-color="{GOLDEN}" stop-opacity="0.18"/>
        <stop offset="0.8" stop-color="{GOLDEN}" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <polygon id="light" points="640,0 960,0 1120,900 480,900" fill="url(#beam)"/>
    <g id="bigBall">
      <circle cx="800" cy="470" r="150" fill="{CREAM}" stroke="{GREEN}" stroke-width="10"/>
      <g fill="none" stroke="{GREEN}" stroke-width="5" stroke-linecap="round" opacity="0.5">
        <path d="M713 388 q10 12 24 14 M770 366 q12 10 27 10 M846 372 q12 8 26 6"/>
        <path d="M700 520 q12 10 26 10 M880 500 q12 8 25 5"/>
      </g>
      <g id="bsgFace" transform="translate({BSG_TX:.1f},{BSG_TY:.1f}) scale({BSG_S})">{paths("bsg")}</g>
    </g>
    <g id="wordmark" transform="translate(590.6,652.0) scale(0.328)" fill="{CREAM}">
      <g id="wmButter">{paths("wm_butter", keep_fill=False)}</g>
      <g id="wmSticks">{paths("wm_sticks", keep_fill=False)}</g>
      <g id="wmGolf">{paths("wm_golf", keep_fill=False, cls="golfLetter")}</g>
    </g>
  </g>
</svg>
</div>

<script>{GSAP}</script>
<script>
gsap.ticker.lagSmoothing(0);

const BALL_START = 512, CUP_X = 1152, BALL_R = 26;
const ROLL_DEG = (CUP_X - BALL_START) / BALL_R * 180 / Math.PI;

// draw-on preparation
const drawables = ["#turfL", "#turfR", "#pole", ".gr"];
gsap.utils.toArray(drawables.join(",")).forEach((p) => {{
  const len = p.getTotalLength ? p.getTotalLength() : 300;
  gsap.set(p, {{ strokeDasharray: len, strokeDashoffset: len }});
}});
gsap.set("#ball", {{ x: BALL_START, y: 528, transformOrigin: "0px 0px" }});
gsap.set("#ballSpin", {{ rotation: 0, transformOrigin: "0px 0px" }});
gsap.set("#putter", {{ rotation: 0, transformOrigin: "404px 214px", x: 0 }});
gsap.set("#flag", {{ transformOrigin: "1152px 336px", scaleX: 0 }});
gsap.set(["#cupMouth"], {{ autoAlpha: 0 }});
gsap.set("#scene", {{ transformOrigin: "{1152}px {560}px" }});
gsap.set("#bigBall", {{ y: -650 }});
gsap.set(["#wmButter", "#wmSticks"], {{ autoAlpha: 0, y: 46 }});
gsap.set(".golfLetter", {{ autoAlpha: 0, y: 28 }});

const tl = gsap.timeline({{ defaults: {{ ease: "power2.out" }} }});

// ---- the scene sketches itself in (0 - 1.5s)
tl.addLabel("draw", 0.15)
  .to("#turfL", {{ strokeDashoffset: 0, duration: 0.8, ease: "power1.inOut" }}, "draw")
  .to("#turfR", {{ strokeDashoffset: 0, duration: 0.25, ease: "power1.out" }}, "draw+=0.75")
  .to(".gr", {{ strokeDashoffset: 0, duration: 0.35, stagger: 0.08 }}, "draw+=0.5")
  .to("#cupMouth", {{ autoAlpha: 1, duration: 0.3 }}, "draw+=0.85")
  .to("#pole", {{ strokeDashoffset: 0, duration: 0.4, ease: "power1.out" }}, "draw+=0.95")
  .to("#flag", {{ scaleX: 1, duration: 0.35, ease: "back.out(2)" }}, "draw+=1.3")
  .from("#putter", {{ x: -160, autoAlpha: 0, duration: 0.5 }}, "draw+=0.6")
  .from("#ball", {{ autoAlpha: 0, scale: 0, duration: 0.35, ease: "back.out(2)" }}, "draw+=0.9");

// ---- the putt (1.8 - 2.2s)
tl.addLabel("putt", 1.8)
  .to("#putter", {{ rotation: -14, duration: 0.45, ease: "power1.inOut" }}, "putt")
  .to("#putter", {{ rotation: 7, duration: 0.14, ease: "power3.in" }}, "putt+=0.55")
  .to("#tick", {{ opacity: 1, duration: 0.05 }}, "putt+=0.66")
  .to("#tick", {{ opacity: 0, duration: 0.25 }}, "putt+=0.78")
  .to("#putter", {{ rotation: 3, duration: 0.4, ease: "sine.out" }}, "putt+=0.69");

// ---- the roll: no-slip rotation, decelerating (2.5 - 4.4s)
tl.addLabel("roll", 2.49)
  .to("#ball", {{ x: CUP_X, duration: 1.9, ease: "power2.out" }}, "roll")
  .to("#ballSpin", {{ rotation: ROLL_DEG, duration: 1.9, ease: "power2.out" }}, "roll")
  // flag shivers as the ball arrives
  .to("#flag", {{ skewY: -6, duration: 0.12, ease: "sine.inOut" }}, "roll+=1.75")
  .to("#flag", {{ skewY: 0, duration: 0.4, ease: "elastic.out(1, 0.4)" }}, "roll+=1.87")
  // ...and drops in
  .to("#ball", {{ y: 596, duration: 0.28, ease: "power2.in" }}, "roll+=1.86");

// ---- plunge into the hole (4.5 - 5.4s)
tl.addLabel("plunge", 4.5)
  .to("#scene", {{ scale: 26, duration: 0.95, ease: "power2.in" }}, "plunge")
  .to(["#cupLip", "#cupRing", "#pole", "#flag", "#putter"], {{ autoAlpha: 0, duration: 0.3,
      ease: "sine.in" }}, "plunge+=0.3")
  .to("#bg", {{ attr: {{ fill: "{HOLE_DARK}" }}, duration: 0.3, ease: "none" }}, "plunge+=0.75")
  .to("body", {{ backgroundColor: "{INSIDE}", duration: 0.3, ease: "none" }}, "plunge+=0.75")
  .set("#scene", {{ visibility: "hidden" }}, "plunge+=1.0")
  .set("#inside", {{ visibility: "visible" }}, "plunge+=1.0");

// ---- at the bottom of the cup (5.5 - 7s)
tl.addLabel("rest", 5.55)
  .to("#bigBall", {{ y: 0, duration: 0.75, ease: "bounce.out" }}, "rest")
  .from("#light", {{ autoAlpha: 0, duration: 0.9, ease: "sine.out" }}, "rest+=0.1");

// ---- the name surfaces (7.0 - 8.8s)
tl.addLabel("type", 7.0)
  .to("#wmButter", {{ autoAlpha: 1, y: 0, duration: 1.3, ease: "sine.out" }}, "type")
  .to("#wmSticks", {{ autoAlpha: 1, y: 0, duration: 1.3, ease: "sine.out" }}, "type+=0.14")
  .to(".golfLetter", {{ autoAlpha: 1, y: 0, duration: 1.0, ease: "sine.out", stagger: 0.09 }}, "type+=0.4");

// quiet hold
tl.to({{}}, {{ duration: 0.1 }}, 9.6);

// reduced motion: land on the finished lockup
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {{
  tl.progress(1).pause();
  gsap.set("body", {{ backgroundColor: "{INSIDE}" }});
}}

// headless frame-grab support: ?seek=<seconds>
const seekParam = new URLSearchParams(location.search).get("seek");
if (seekParam !== null) {{
  tl.pause(parseFloat(seekParam));
  gsap.globalTimeline.pause();
}}
document.body.addEventListener("click", () => tl.restart());
window.introTimeline = tl;
</script>
</body>
</html>
"""

out = ROOT / "gsap" / "intro_putt.html"
out.write_text(html, encoding="utf-8")

m_title = re.search(r"<title>.*?</title>", html, re.S)
m_style = re.search(r"<style>.*?</style>", html, re.S)
m_body = re.search(r"<body>(.*)</body>", html, re.S)
(ROOT / "gsap" / "intro_putt_artifact.html").write_text(
    m_title.group(0) + "\n" + m_style.group(0) + m_body.group(1), encoding="utf-8")

print(f"WROTE {out}  ({out.stat().st_size / 1024:.0f} KB incl. inlined GSAP)")

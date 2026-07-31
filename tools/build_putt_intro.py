"""Assemble gsap/intro_putt.html — the stick-art putt intro:

A line-art putting scene draws itself on; a putter taps the ball; it
rolls across the green (no-slip rolling rotation) and drops in the cup;
the camera plunges into the hole; at the bottom, the ball rests in a
shaft of light with BSG on its face, and the wordmark surfaces.

Pure vector + GSAP. Builds gsap/intro_putt.html and the self-contained
gsap/intro_putt_artifact.html. ?seek=<sec>, reduced-motion, click replay.
"""
import base64
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
SILVER = "#B9B6AC"
BROWN = "#8C5E2E"


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

  <defs><clipPath id="aboveGround"><rect x="0" y="0" width="1600" height="570"/></clipPath></defs>

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
    <!-- the ball (rolls); clipped so it sinks into the cup -->
    <g clip-path="url(#aboveGround)"><g id="ball">
      <circle cx="0" cy="0" r="26" fill="{CREAM}" stroke="{GREEN}" stroke-width="6"/>
      <g id="ballSpin" fill="{GREEN}">
        <circle r="12" fill="none" stroke="none"/>
        <circle cx="-9" cy="-4" r="2.6"/><circle cx="8" cy="-7" r="2.6"/>
        <circle cx="2" cy="9" r="2.6"/>
      </g>
    </g></g>
    <ellipse id="cupRing" cx="1152" cy="560" rx="28" ry="9" fill="none" stroke="{GREEN}" stroke-width="6"/>
    <!-- the putter: brown grip, silver shaft, bladed head -->
    <g id="putter">
      <path d="M404 272 L452 528" stroke="{SILVER}" stroke-width="7" stroke-linecap="round" fill="none"/>
      <path d="M388 188 L406 280" stroke="{BROWN}" stroke-width="17" stroke-linecap="round" fill="none"/>
      <path d="M391 210 l16 3 M394 228 l16 3 M397 246 l15 3" stroke="#6E4A24" stroke-width="3" stroke-linecap="round" fill="none"/>
      <path d="M441 524 q-9 3 -9 13 v3 q0 10 10 10 h55 q10 0 10 -10 v-4 q0 -10 -10 -10 l-40 -4 z"
            fill="{SILVER}" stroke="{GREEN}" stroke-width="5" stroke-linejoin="round"/>
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
    <defs>
      <radialGradient id="ballShade" cx="0.5" cy="0.34" r="0.85">
        <stop offset="0" stop-color="#F4EAD3"/>
        <stop offset="0.55" stop-color="{CREAM}"/>
        <stop offset="1" stop-color="#D2BF98"/>
      </radialGradient>
      <clipPath id="ballFace"><circle cx="800" cy="470" r="145"/></clipPath>
      <filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
        <feGaussianBlur stdDeviation="8"/>
      </filter>
    </defs>
    <polygon id="light" points="640,0 960,0 1120,900 480,900" fill="url(#beam)"/>
    <!-- the hole floor -->
    <ellipse cx="800" cy="648" rx="520" ry="64" fill="#33200E"/>
    <ellipse id="ballShadow" cx="800" cy="636" rx="150" ry="24" fill="#1B1004" opacity="0.55" filter="url(#soft)"/>
    <g id="bigBall">
      <circle cx="800" cy="470" r="150" fill="url(#ballShade)" stroke="{GREEN}" stroke-width="10"/>
      <g clip-path="url(#ballFace)">
        <g fill="#C4B28A">
        <circle cx="749" cy="380" r="6.5" opacity="0.31"/>
        <circle cx="783" cy="380" r="6.5" opacity="0.34"/>
        <circle cx="817" cy="380" r="6.5" opacity="0.34"/>
        <circle cx="851" cy="380" r="6.5" opacity="0.31"/>
        <circle cx="732" cy="410" r="6.5" opacity="0.34"/>
        <circle cx="766" cy="410" r="6.5" opacity="0.38"/>
        <circle cx="800" cy="410" r="6.5" opacity="0.40"/>
        <circle cx="834" cy="410" r="6.5" opacity="0.38"/>
        <circle cx="868" cy="410" r="6.5" opacity="0.34"/>
        <circle cx="715" cy="440" r="6.5" opacity="0.34"/>
        <circle cx="749" cy="440" r="6.5" opacity="0.40"/>
        <circle cx="783" cy="440" r="6.5" opacity="0.45"/>
        <circle cx="817" cy="440" r="6.5" opacity="0.45"/>
        <circle cx="851" cy="440" r="6.5" opacity="0.40"/>
        <circle cx="885" cy="440" r="6.5" opacity="0.34"/>
        <circle cx="698" cy="470" r="6.5" opacity="0.32"/>
        <circle cx="732" cy="470" r="6.5" opacity="0.38"/>
        <circle cx="766" cy="470" r="6.5" opacity="0.45"/>
        <circle cx="800" cy="470" r="6.5" opacity="0.52"/>
        <circle cx="834" cy="470" r="6.5" opacity="0.45"/>
        <circle cx="868" cy="470" r="6.5" opacity="0.38"/>
        <circle cx="902" cy="470" r="6.5" opacity="0.32"/>
        <circle cx="715" cy="500" r="6.5" opacity="0.34"/>
        <circle cx="749" cy="500" r="6.5" opacity="0.40"/>
        <circle cx="783" cy="500" r="6.5" opacity="0.45"/>
        <circle cx="817" cy="500" r="6.5" opacity="0.45"/>
        <circle cx="851" cy="500" r="6.5" opacity="0.40"/>
        <circle cx="885" cy="500" r="6.5" opacity="0.34"/>
        <circle cx="732" cy="530" r="6.5" opacity="0.34"/>
        <circle cx="766" cy="530" r="6.5" opacity="0.38"/>
        <circle cx="800" cy="530" r="6.5" opacity="0.40"/>
        <circle cx="834" cy="530" r="6.5" opacity="0.38"/>
        <circle cx="868" cy="530" r="6.5" opacity="0.34"/>
        <circle cx="749" cy="560" r="6.5" opacity="0.31"/>
        <circle cx="783" cy="560" r="6.5" opacity="0.34"/>
        <circle cx="817" cy="560" r="6.5" opacity="0.34"/>
        <circle cx="851" cy="560" r="6.5" opacity="0.31"/>
        </g>
        <!-- underside shade -->
        <ellipse cx="800" cy="560" rx="150" ry="88" fill="#4B311A" opacity="0.14" filter="url(#soft)"/>
        <!-- beam catch on the crown -->
        <ellipse cx="778" cy="360" rx="72" ry="30" fill="#FFF6DE" opacity="0.55" filter="url(#soft)" transform="rotate(-14 778 360)"/>
      </g>
      <g id="bsgFace" transform="translate({BSG_TX:.1f},{BSG_TY:.1f}) scale({BSG_S})">{paths("bsg")}</g>
    </g>
    <g id="wordmark" transform="translate(590.6,652.0) scale(0.328)" fill="{CREAM}">
      <g id="wmButter">{paths("wm_butter", keep_fill=False)}</g>
      <g id="wmSticks">{paths("wm_sticks", keep_fill=False)}</g>
      <g id="wmGolf">{paths("wm_golf", keep_fill=False, cls="golfLetter")}</g>
    </g>
  </g>

  <!-- 70s film: living grain, warm vignette, frame edge — fixed overlay,
       drawn above both acts so it never scales with the plunge -->
  <defs>
    <filter id="filmGrain" x="0" y="0" width="100%" height="100%">
      <feTurbulence id="grainNoise" type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>
      <feColorMatrix type="matrix"
        values="0 0 0 0 0.30  0 0 0 0 0.22  0 0 0 0 0.12  0.75 0.75 0.75 0 0"/>
    </filter>
    <radialGradient id="vig" cx="0.5" cy="0.47" r="0.75">
      <stop offset="0.6" stop-color="{HOLE_DARK}" stop-opacity="0"/>
      <stop offset="1" stop-color="{HOLE_DARK}" stop-opacity="0.24"/>
    </radialGradient>
  </defs>
  <g id="film" pointer-events="none">
    <rect width="1600" height="900" filter="url(#filmGrain)" opacity="0.14"/>
    <rect width="1600" height="900" fill="url(#vig)"/>
    <rect x="10" y="10" width="1580" height="880" rx="24" fill="none"
          stroke="{HOLE_DARK}" stroke-opacity="0.45" stroke-width="12"/>
  </g>
</svg>
</div>

<audio id="auAmb" src="audio/amb.mp3" preload="auto" loop></audio>
<audio id="auPutt" src="audio/putt.mp3" preload="auto"></audio>
<audio id="auRoll" src="audio/roll.mp3" preload="auto"></audio>
<audio id="auCup" src="audio/cup.mp3" preload="auto"></audio>

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
gsap.set("#ballSpin", {{ rotation: 0, transformOrigin: "12px 12px" }});
gsap.set("#putter", {{ rotation: 0, svgOrigin: "472 128", x: 0 }});
gsap.set("#flag", {{ svgOrigin: "1152 336", scaleX: 0 }});
gsap.set(["#cupMouth"], {{ autoAlpha: 0 }});
gsap.set("#scene", {{ svgOrigin: "1152 560" }});
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

// ---- address waggle, then the putt (1.3 - 2.2s)
tl.addLabel("waggle", 1.25)
  .to("#putter", {{ rotation: 2.6, duration: 0.16, ease: "sine.inOut" }}, "waggle")
  .to("#putter", {{ rotation: -2.2, duration: 0.2, ease: "sine.inOut" }}, "waggle+=0.16")
  .to("#putter", {{ rotation: 0, duration: 0.16, ease: "sine.out" }}, "waggle+=0.36");

tl.addLabel("putt", 1.8)
  .to("#putter", {{ rotation: 8, y: -14, x: -20, duration: 0.45, ease: "power1.inOut" }}, "putt")
  .to("#putter", {{ rotation: -4, y: 0, x: 0, duration: 0.14, ease: "power3.in" }}, "putt+=0.55")
  .to("#tick", {{ opacity: 1, duration: 0.05 }}, "putt+=0.66")
  .to("#tick", {{ opacity: 0, duration: 0.25 }}, "putt+=0.78")
  .to("#putter", {{ rotation: -2, y: -4, x: 6, duration: 0.4, ease: "sine.out" }}, "putt+=0.69");

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
  .to(["#cupRing", "#pole", "#flag", "#putter"], {{ autoAlpha: 0, duration: 0.3,
      ease: "sine.in" }}, "plunge+=0.3")
  .to("#bg", {{ attr: {{ fill: "{HOLE_DARK}" }}, duration: 0.3, ease: "none" }}, "plunge+=0.75")
  .to("body", {{ backgroundColor: "{INSIDE}", duration: 0.3, ease: "none" }}, "plunge+=0.75")
  .set("#scene", {{ visibility: "hidden" }}, "plunge+=1.0")
  .set("#inside", {{ visibility: "visible" }}, "plunge+=1.0");

// ---- at the bottom of the cup (5.5 - 7s)
tl.addLabel("rest", 5.55)
  .to("#bigBall", {{ y: 0, duration: 0.75, ease: "bounce.out" }}, "rest")
  .fromTo("#ballShadow", {{ scaleX: 0.35, opacity: 0, transformOrigin: "50% 50%" }},
      {{ scaleX: 1, opacity: 0.55, duration: 0.5, ease: "power2.out", immediateRender: false }}, "rest+=0.3")
  .from("#light", {{ autoAlpha: 0, duration: 0.9, ease: "sine.out" }}, "rest+=0.1");

// ---- the name surfaces (7.0 - 8.8s)
tl.addLabel("type", 7.0)
  .to("#wmButter", {{ autoAlpha: 1, y: 0, duration: 1.3, ease: "sine.out" }}, "type")
  .to("#wmSticks", {{ autoAlpha: 1, y: 0, duration: 1.3, ease: "sine.out" }}, "type+=0.14")
  .to(".golfLetter", {{ autoAlpha: 1, y: 0, duration: 1.0, ease: "sine.out", stagger: 0.09 }}, "type+=0.4");

// quiet hold
tl.to({{}}, {{ duration: 0.1 }}, 9.6);

// ---- sound: ambient bed + cues (autoplay-safe; unlocks on first gesture)
const AU = {{
  amb: document.getElementById("auAmb"),
  putt: document.getElementById("auPutt"),
  roll: document.getElementById("auRoll"),
  cup: document.getElementById("auCup"),
}};
AU.amb.volume = 0.22; AU.putt.volume = 0.9;
AU.roll.volume = 0.45; AU.cup.volume = 0.8;
const tryPlay = (a) => {{ const p = a.play(); if (p) p.catch(() => {{}}); }};
let audioUnlocked = false;
const unlockAudio = () => {{
  if (audioUnlocked) return;
  audioUnlocked = true;
  if (tl.progress() > 0 && tl.progress() < 1 && !tl.paused()) tryPlay(AU.amb);
}};
addEventListener("pointerdown", unlockAudio, {{ once: true }});
addEventListener("keydown", unlockAudio, {{ once: true }});
tl.call(() => tryPlay(AU.amb), null, "draw")
  .call(() => tryPlay(AU.putt), null, "putt+=0.62")
  .call(() => {{ AU.roll.volume = 0.45; tryPlay(AU.roll); }}, null, "roll")
  .to(AU.roll, {{ volume: 0.02, duration: 1.7, ease: "power1.in" }}, "roll+=0.2")
  .call(() => tryPlay(AU.cup), null, "roll+=1.84")
  .to(AU.amb, {{ volume: 0.07, duration: 0.8, ease: "sine.in" }}, "plunge")
  .call(() => {{ AU.cup.currentTime = 0; AU.cup.volume = 0.4;
      AU.cup.playbackRate = 0.85; tryPlay(AU.cup); }}, null, "rest+=0.3");

// ---- living 16mm: grain reseed + gentle gate weave
const isSeeking = new URLSearchParams(location.search).get("seek") !== null;
const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (!isSeeking && !prefersReduced) {{
  const gn = document.getElementById("grainNoise");
  setInterval(() => gn.setAttribute("seed", (Math.random() * 999) | 0), 100);
  (function weave() {{
    gsap.to(["#scene", "#inside"], {{
      x: () => gsap.utils.random(-1.1, 1.1),
      y: () => gsap.utils.random(-0.7, 0.7),
      duration: 0.12, ease: "none", overwrite: false, onComplete: weave }});
  }})();
}}

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

# artifact: inline the audio files so the page is fully self-contained
art = html
for _n in ("amb", "putt", "roll", "cup"):
    _b64 = base64.b64encode(
        (ROOT / "gsap" / "audio" / f"{_n}.mp3").read_bytes()).decode()
    art = art.replace(f'src="audio/{_n}.mp3"',
                      f'src="data:audio/mpeg;base64,{_b64}"')

m_title = re.search(r"<title>.*?</title>", art, re.S)
m_style = re.search(r"<style>.*?</style>", art, re.S)
m_body = re.search(r"<body>(.*)</body>", art, re.S)
(ROOT / "gsap" / "intro_putt_artifact.html").write_text(
    m_title.group(0) + "\n" + m_style.group(0) + m_body.group(1), encoding="utf-8")

print(f"WROTE {out}  ({out.stat().st_size / 1024:.0f} KB incl. inlined GSAP)")

"""Assemble gsap/intro.html — the Butter Sticks intro as a GSAP/SVG animation.

Reads gsap/groups.json (extracted brand vector paths) and gsap/gsap.min.js,
emits one self-contained HTML file. Supports ?seek=<sec> for headless
frame-grabs and respects prefers-reduced-motion (jumps to final lockup).
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


def paths(group, keep_fill=True, cls=""):
    out = []
    for it in G[group]:
        fill = f' fill="{it["fill"]}"' if keep_fill else ""
        c = f' class="{cls}"' if cls else ""
        out.append(f'<path d="{it["d"]}"{fill}{c}/>')
    return "\n".join(out)


def wave(width=3600, x0=-1000, amp=30, wl=400, depth=1100):
    """Repeating sine-ish wave with a filled body below it."""
    n = int(width / wl)
    seg = ""
    for _ in range(n):
        seg += f"q{wl / 4:.0f} {-amp} {wl / 2:.0f} 0 q{wl / 4:.0f} {amp} {wl / 2:.0f} 0 "
    return f"M{x0} 0 {seg} v{depth} h{-width} Z"


# Badge native frame: x 1530.9-1944.1, y 743.6-1394.7 (from extraction)
# Scene 1600x900. Badge scale .4 -> h 260. Wordmark scale .39 -> h 200.
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
    <filter id="goo">
      <feGaussianBlur in="SourceGraphic" stdDeviation="7" result="blur"/>
      <feColorMatrix in="blur" mode="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -8" result="goo"/>
    </filter>
    <clipPath id="drainClip">
      <rect id="drainRect" x="1520" y="745" width="430" height="656"/>
    </clipPath>
  </defs>

  <rect id="bg" width="1600" height="900" fill="{CREAM}"/>

  <!-- falling butter drops: gooey, behind the ponds -->
  <g id="dripLayer" filter="url(#goo)" fill="{GOLDEN}">
    <ellipse class="dripSrc" cx="762" cy="436" rx="16" ry="10"/>
    <ellipse class="dripSrc" cx="801" cy="440" rx="20" ry="11"/>
    <ellipse class="dripSrc" cx="843" cy="437" rx="15" ry="9"/>
    <ellipse class="drop" cx="756" cy="436" rx="11" ry="14"/>
    <ellipse class="drop" cx="789" cy="438" rx="13" ry="16"/>
    <ellipse class="drop" cx="816" cy="436" rx="10" ry="13"/>
    <ellipse class="drop" cx="848" cy="438" rx="12" ry="15"/>
    <ellipse class="drop" cx="871" cy="435" rx="9" ry="12"/>
  </g>

  <!-- liquids -->
  <g id="pondBack"><path d="{wave(amp=34)}" fill="{DEEP}"/></g>
  <g id="pondFront"><path d="{wave(amp=26)}" fill="{GOLDEN}"/></g>
  <g id="tide"><path d="{wave(amp=38)}" fill="{BROWN}"/></g>

  <!-- the badge: silhouette static, cream mold behind draining gold -->
  <g id="badgeMove">
    <g transform="translate(105,22.3) scale(0.4)">
      {paths("sil")}
      <g fill="{CREAM}" opacity="0.0" id="mold">{paths("gold", keep_fill=False)}</g>
      {paths("ball")}
      {paths("dimples_cream")}
      {paths("dimples_green")}
      <g clip-path="url(#drainClip)">{paths("gold")}</g>
      {paths("tee")}
      <g id="bsg">{paths("bsg")}</g>
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
const $ = (s) => document.querySelector(s);
const $$ = (s) => gsap.utils.toArray(s);

gsap.set("#badgeMove", {{ autoAlpha: 0, scale: 0.92, transformOrigin: "50% 50%" }});
gsap.set(["#wmButter", "#wmSticks"], {{ autoAlpha: 0, y: 150 }});
gsap.set(".golfLetter", {{ autoAlpha: 0, y: 70 }});
gsap.set([".drop", ".dripSrc"], {{ autoAlpha: 0 }});
gsap.set(["#pondBack", "#pondFront", "#tide"], {{ y: 920 }});
gsap.set("svg", {{ scale: 1.07, transformOrigin: "50% 50%" }});

// endless sideways drift on every liquid surface (wavelength = 400)
gsap.to("#pondBack path",  {{ x: -400, duration: 1.7, ease: "none", repeat: -1 }});
gsap.to("#pondFront path", {{ x: -400, duration: 2.3, ease: "none", repeat: -1 }});
gsap.to("#tide path",      {{ x: -400, duration: 2.0, ease: "none", repeat: -1 }});

const tl = gsap.timeline({{ defaults: {{ ease: "power2.out" }} }});

// ---- beat 1: arrival on cream (0 - 1.4s)
tl.addLabel("in", 0.15)
  .to("#badgeMove", {{ autoAlpha: 1, duration: 0.55, ease: "sine.out" }}, "in")
  .to("#badgeMove", {{ scale: 1.04, duration: 0.75, ease: "back.out(1.4)" }}, "in")
  .to("#badgeMove", {{ scale: 1.0, duration: 0.4 }}, "in+=0.78")
  // anticipation: butter softens
  .to("#badgeMove", {{ scaleY: 0.965, scaleX: 1.03, duration: 0.22, ease: "sine.inOut" }}, 1.28)
  .to("#badgeMove", {{ scaleY: 1, scaleX: 1, duration: 0.28, ease: "sine.out" }}, 1.52);

// ---- beat 2: the melt (1.5 - 3.5s) — gold drains out of its own outline
tl.addLabel("melt", 1.5)
  .to("#mold", {{ opacity: 1, duration: 0.15 }}, "melt")
  .to("#drainRect", {{ attr: {{ y: 1012, height: 389 }}, duration: 1.9, ease: "power1.inOut" }}, "melt")
  .to("#bsg", {{ y: 105, duration: 1.9, ease: "power1.inOut" }}, "melt")
  .to("#bsg", {{ autoAlpha: 0, duration: 0.45 }}, "melt+=1.45")
  .to("#speed", {{ autoAlpha: 0, duration: 0.4 }}, "melt+=0.25")
  .to(".dripSrc", {{ autoAlpha: 1, duration: 0.3, stagger: 0.12 }}, "melt+=0.2")
  .to(".dripSrc", {{ autoAlpha: 0, duration: 0.3, stagger: 0.1 }}, "melt+=1.7");

// falling gooey drops, two staggered waves
$$(".drop").forEach((d, i) => {{
  [0, 1].forEach((w) => {{
    const t0 = 1.75 + i * 0.17 + w * 0.85 + (i % 3) * 0.06;
    tl.fromTo(d, {{ autoAlpha: 1, y: 0, scaleY: 1, transformOrigin: "50% 0%" }},
      {{ y: 205, scaleY: 2.6, duration: 0.62, ease: "power2.in", immediateRender: false }}, t0)
      .to(d, {{ autoAlpha: 0, duration: 0.12 }}, t0 + 0.52);
  }});
}});

// ---- beat 3: pond fills like a glass (2.2 - 3.5s)
tl.addLabel("pond", 2.2)
  .to("#pondBack", {{ y: 585, duration: 1.25, ease: "power1.inOut" }}, "pond")
  .to("#pondFront", {{ y: 606, duration: 1.25, ease: "power1.inOut" }}, "pond+=0.1");

// ---- beat 4: the brown tide inversion (3.6 - 4.45s)
tl.addLabel("tideUp", 3.6)
  .to("#tide", {{ y: -85, duration: 0.85, ease: "power2.inOut" }}, "tideUp");

// ---- beat 5: jelly settle + rise to lockup (4.35 - 5.1s)
tl.addLabel("settle", 4.35)
  .to("#badgeMove", {{ scaleY: 0.85, scaleX: 1.09, duration: 0.16, ease: "sine.in" }}, "settle")
  .to("#badgeMove", {{ scaleY: 1.06, scaleX: 0.96, duration: 0.18, ease: "sine.inOut" }}, "settle+=0.16")
  .to("#badgeMove", {{ scaleY: 1, scaleX: 1, duration: 0.24, ease: "sine.out" }}, "settle+=0.34")
  .to("#badgeMove", {{ y: -117.2, duration: 0.7, ease: "power2.inOut" }}, "settle+=0.15");

// ---- beat 6: wordmark reveal (4.8 - 6.2s)
tl.addLabel("type", 4.8)
  .to("#wmButter", {{ autoAlpha: 1, y: 0, duration: 0.6, ease: "power3.out" }}, "type")
  .to("#wmSticks", {{ autoAlpha: 1, y: 0, duration: 0.6, ease: "power3.out" }}, "type+=0.22")
  .to(".golfLetter", {{ autoAlpha: 1, y: 0, duration: 0.45, ease: "power2.out", stagger: 0.11 }}, "type+=0.55");

// ---- beat 7: breathing hold (6.4 - 7.1s)
tl.to("#badgeMove", {{ scale: 1.012, duration: 0.35, ease: "sine.inOut" }}, 6.4)
  .to("#badgeMove", {{ scale: 1.0, duration: 0.35, ease: "sine.inOut" }}, 6.75);

// slow camera push, whole film
tl.to("svg", {{ scale: 1.0, duration: 7.1, ease: "sine.out" }}, 0);

// reduced motion: land on the finished lockup immediately
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {{
  tl.progress(1).pause();
  gsap.set("#tide", {{ y: -85 }});
}}

// headless frame-grab support: ?seek=<seconds>
const seek = new URLSearchParams(location.search).get("seek");
if (seek !== null) {{
  gsap.ticker.sleep?.();
  tl.pause(parseFloat(seek));
  gsap.globalTimeline.pause();   // freezes the drift loops too
}}
window.introTimeline = tl;
</script>
</body>
</html>
"""

out = ROOT / "gsap" / "intro.html"
out.write_text(html, encoding="utf-8")
print(f"WROTE {out}  ({out.stat().st_size / 1024:.0f} KB incl. inlined GSAP)")

"""Assemble gsap/intro.html — the Butter Sticks intro as a GSAP/SVG animation.

v3 "total meltdown":
- No shape-pop: the REAL gold vector renders through the gooey filter from
  frame one and is itself the thing that slumps (no stand-in rect).
- The melt consumes everything: butter cascades over the ball, the ball
  goes with it, and the whole golden mass slumps off the tee into the pond.
- After the brown tide, the script wordmark rises alone, centered.
~9.4s. ?seek=<sec> frame-grabs, prefers-reduced-motion, click to replay.
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

# True sphere: crown sits at the vertical middle of the 'S' in BSG (y 855.9),
# radius from the ball's widest span -> center y = 855.9 + 185.8
BALL_CX, BALL_CY, BALL_R = 1742.1, 1041.7, 185.8


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
    """The liquid: the REAL pat artwork + ball-coat + runnels, gooey-merged.
    Same markup for the gold body and the green rim underneath."""
    runnels = ""
    for i, (x0, drift) in enumerate([(1604, -50), (1676, -20), (1744, 0),
                                     (1814, 22), (1882, 52)]):
        runnels += (f'<ellipse class="{cls}Run" cx="{x0}" cy="962" '
                    f'rx="{28 + (i % 3) * 5}" ry="34" data-drift="{drift}"/>\n')
    return f"""
    <g class="{cls}PatArt">{paths("gold", keep_fill=False)}</g>
    <ellipse class="{cls}TeeCup" cx="1741" cy="1190" rx="62" ry="24"/>
    <rect class="{cls}TeeStem" x="1717" y="1195" width="49" height="202" rx="22"/>
    <g clip-path="url(#coatClip)">
      <ellipse class="{cls}Coat" cx="{BALL_CX}" cy="{BALL_CY}" rx="{BALL_R + 4}" ry="{BALL_R + 4}"/>
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
<svg viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid meet" aria-label="Butter Sticks Golf intro animation">
  <defs>
    <filter id="goo" filterUnits="userSpaceOnUse" x="1390" y="590" width="680" height="1100" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="b"/>
      <feColorMatrix in="b" mode="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -8"/>
    </filter>
    <filter id="gooRim" filterUnits="userSpaceOnUse" x="1390" y="590" width="680" height="1100" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="b"/>
      <feColorMatrix in="b" mode="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -8" result="thresh"/>
      <feMorphology id="rimDilate" in="thresh" operator="dilate" radius="9" result="fat"/>
      <feFlood flood-color="{GREEN}"/>
      <feComposite operator="in" in2="fat"/>
    </filter>
    <filter id="lettersMelt" filterUnits="userSpaceOnUse" x="1560" y="730" width="390" height="540" color-interpolation-filters="sRGB">
      <feTurbulence type="turbulence" baseFrequency="0.012 0.03" numOctaves="2" result="n"/>
      <feDisplacementMap id="dispMap" in="SourceGraphic" in2="n" scale="0"
        xChannelSelector="R" yChannelSelector="G" result="disp"/>
      <feGaussianBlur id="bsgBlur" in="disp" stdDeviation="0 0"/>
    </filter>
    <clipPath id="coatClip">
      <path id="coatWave" d="M1520 400 H1968 V1128 Q1932 1146 1896 1136 L1834 1106 Q1788 1088 1744 1078 Q1700 1088 1654 1106 L1592 1136 Q1556 1146 1520 1128 Z"/>
    </clipPath>
    <mask id="eraserMask">
      <rect id="eraserRect" x="1520" y="740" width="440" height="0" fill="white"/>
      <circle cx="{BALL_CX}" cy="{BALL_CY}" r="202" fill="black"/>
    </mask>
    <mask id="ballGuard">
      <rect x="1500" y="700" width="480" height="380" fill="white"/>
      <circle cx="{BALL_CX}" cy="{BALL_CY}" r="202" fill="black"/>
    </mask>
    <clipPath id="sceneClip"><rect x="0" y="0" width="1600" height="900"/></clipPath>
  </defs>
  <g clip-path="url(#sceneClip)">

  <rect id="bg" width="1600" height="900" fill="{CREAM}"/>

  <!-- gentle drops falling from the cascading mass into the pond -->
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
      <g id="staticA">
        {paths("sil")}
        <g mask="url(#eraserMask)"><g id="eraser" fill="{CREAM}" stroke="{CREAM}" stroke-width="9">{paths("sil", keep_fill=False)}</g></g>
        {paths("ball")}
        {paths("dimples_cream")}
        {paths("dimples_green")}
        {paths("tee")}
        <g id="hornCover" fill="{CREAM}" opacity="0" mask="url(#ballGuard)">
          <rect x="1872" y="876" width="92" height="104" rx="14"/>
          <rect x="1522" y="886" width="84" height="90" rx="14"/>
        </g>
      </g>
      <!-- the molten butter: real art in the goo from frame one -->
      <g id="moltenRim" filter="url(#gooRim)">{molten_members("r")}</g>
      <g id="moltenGold" filter="url(#goo)" fill="{GOLDEN}">{molten_members("g")}</g>
      <g id="bsg" filter="url(#lettersMelt)">{paths("bsg", cls="bsgL")}</g>
      <g id="speed">{paths("speed")}</g>
    </g>
  </g>

  <!-- wordmark: the sole hero of the final act, centered -->
  <g id="wmMove" transform="translate(538.0,291.8) scale(0.41)" fill="{CREAM}">
    <g id="wmButter">{paths("wm_butter", keep_fill=False)}</g>
    <g id="wmSticks">{paths("wm_sticks", keep_fill=False)}</g>
    <g id="wmGolf">{paths("wm_golf", keep_fill=False, cls="golfLetter")}</g>
  </g>
  </g>
</svg>
</div>

<script>{GSAP}</script>
<script>
const $$ = (s) => gsap.utils.toArray(s);

gsap.set("#badgeMove", {{ autoAlpha: 0, scale: 0.92, transformOrigin: "50% 50%" }});
gsap.set(["#wmButter", "#wmSticks"], {{ autoAlpha: 0, y: 40 }});
gsap.set(".golfLetter", {{ autoAlpha: 0, y: 24 }});
gsap.set(".drop", {{ autoAlpha: 0 }});
gsap.set("#coatWave", {{ y: -282 }});
gsap.set(["#pondBack", "#pondFront", "#tide"], {{ y: 920 }});
gsap.set("svg", {{ scale: 1.07, transformOrigin: "50% 50%" }});
gsap.set(".rRun, .gRun", {{ autoAlpha: 0 }});
gsap.set(".rTeeCup, .gTeeCup, .rTeeStem, .gTeeStem", {{ autoAlpha: 0 }});
gsap.set(".rTeeStem, .gTeeStem", {{ scaleY: 0.12, transformOrigin: "50% 0%" }});

// endless sideways drift on every liquid surface (wavelength = 400)
gsap.to("#pondBack path",  {{ x: -400, duration: 2.1, ease: "none", repeat: -1 }});
gsap.to("#pondFront path", {{ x: -400, duration: 2.8, ease: "none", repeat: -1 }});
gsap.to("#tide path",      {{ x: -400, duration: 2.4, ease: "none", repeat: -1 }});

const tl = gsap.timeline({{ defaults: {{ ease: "power2.out" }} }});

// ---- beat 1: arrival on cream (0 - 1.4s)
tl.addLabel("in", 0.15)
  .to("#badgeMove", {{ autoAlpha: 1, duration: 0.7, ease: "sine.out" }}, "in")
  .to("#badgeMove", {{ scale: 1.0, duration: 1.2, ease: "sine.out" }}, "in");

// ---- beat 2: the pat melts in place (1.6 - 3.4s)
tl.addLabel("melt", 1.6)
  .to("#speed", {{ autoAlpha: 0, duration: 0.4 }}, "melt")
  // the outline melts into the mass: rim thins as everything liquefies
  .to("#rimDilate", {{ attr: {{ radius: 3 }}, duration: 2.6, ease: "sine.inOut" }}, "melt+=0.3")
  // the real pat art slumps downward into the flow
  .to(".rPatArt, .gPatArt", {{ scaleY: 0.24, transformOrigin: "50% 100%",
      duration: 1.8, ease: "power1.inOut" }}, "melt+=0.2")
  .to(".rPatArt", {{ opacity: 0, duration: 1.6, ease: "sine.in" }}, "melt+=0.5")
  .to("#eraserRect", {{ attr: {{ height: 300 }}, duration: 1.6, ease: "power1.out" }}, "melt+=0.05")
  // butter coats the ball's crown, hugging the surface
  .to("#coatWave", {{ y: 165, duration: 2.5, ease: "power1.inOut" }}, "melt+=0.4")
  .to(".rRun, .gRun", {{ autoAlpha: 1, duration: 0.4, stagger: 0.15 }}, "melt+=0.3")
  .to("#hornCover", {{ opacity: 1, duration: 0.5, ease: "sine.inOut" }}, "melt+=0.9")
  // BSG rides the slumping butter down, liquefying as it goes
  .to(".bsgL", {{ y: 215, scaleY: 1.55, transformOrigin: "50% 0%", duration: 1.8,
      ease: "power1.inOut", stagger: 0.08 }}, "melt+=0.2")
  .to(".bsgL", {{ fill: "{GOLDEN}", duration: 0.9, ease: "sine.in", stagger: 0.08 }}, "melt+=0.55")
  .to(".bsgL", {{ autoAlpha: 0, duration: 0.7, ease: "sine.inOut", stagger: 0.08 }}, "melt+=1.25")
  .to("#dispMap", {{ attr: {{ scale: 26 }}, duration: 1.3, ease: "sine.in" }}, "melt+=0.5")
  .to("#bsgBlur", {{ attr: {{ stdDeviation: "0 19" }}, duration: 1.2, ease: "sine.in" }}, "melt+=0.7");

// runnels slide down the ball as the coat spreads
$$(".rRun, .gRun").forEach((r) => {{
  const drift = parseFloat(r.dataset.drift);
  const t0 = 0.65 + (55 - Math.abs(drift)) / 75;
  tl.to(r, {{ attr: {{ cy: 1235, cx: "+=" + drift }}, scaleY: 1.6,
      transformOrigin: "50% 0%", duration: 2.2 + Math.abs(drift) / 55,
      ease: "sine.in" }}, "melt+=" + t0);
}});

// ---- beat 3: the ball goes with it (3.3 - 5.2s)
tl.addLabel("consume", 3.3)

  // pond arrives to receive the cascade
  .to("#pondBack", {{ y: 585, duration: 1.3, ease: "power1.inOut" }}, "consume+=0.1")
  .to("#pondFront", {{ y: 606, duration: 1.3, ease: "power1.inOut" }}, "consume+=0.22")
  // everything solid fades beneath the gold (invisible handoff)
  .to("#staticA", {{ autoAlpha: 0, duration: 0.38, ease: "sine.inOut" }}, "consume+=0.78")
  .to(".rPatArt, .gPatArt", {{ autoAlpha: 0, duration: 0.4 }}, "consume+=0.7")
  // ...and the whole molten mass slumps off the tee into the river
  .to("#coatWave", {{ y: 620, duration: 0.8, ease: "power1.in" }}, "consume+=0.6")
  .to(".rTeeCup, .gTeeCup", {{ autoAlpha: 1, duration: 0.25, ease: "sine.out" }}, "consume+=0.45")
  .to(".rTeeStem, .gTeeStem", {{ autoAlpha: 1, duration: 0.18 }}, "consume+=0.5")
  .to(".rTeeStem, .gTeeStem", {{ scaleY: 1, duration: 0.55, ease: "power1.in" }}, "consume+=0.52")
  .to(".rCoat, .gCoat", {{ attr: {{ cy: "+=300", ry: 96, rx: 238 }},
      duration: 1.35, ease: "power1.in" }}, "consume+=0.75")
  .to(".rRun, .gRun", {{ attr: {{ cy: "+=260" }}, autoAlpha: 0,
      duration: 0.9, ease: "power1.in", stagger: (i) => (i % 5) * 0.06 }}, "consume+=0.8")
  .to(["#moltenRim", "#moltenGold"], {{ autoAlpha: 0, duration: 0.45, ease: "sine.in" }}, "consume+=1.8");

// drops accompany the cascade
$$(".drop").forEach((d, i) => {{
  [0, 1].forEach((w) => {{
    const t0 = 3.7 + i * 0.35 + w * 0.8;
    tl.fromTo(d, {{ autoAlpha: 1, y: 0, scaleY: 1, transformOrigin: "50% 0%" }},
      {{ y: 385, scaleY: 2.0, duration: 1.05, ease: "power1.in", immediateRender: false }}, t0)
      .to(d, {{ autoAlpha: 0, duration: 0.2 }}, t0 + 0.85);
  }});
}});

// ---- beat 4: the brown tide inversion (5.3 - 6.2s)
tl.addLabel("tideUp", 5.3)
  .to("#tide", {{ y: -85, duration: 0.9, ease: "power2.inOut" }}, "tideUp")
  .to("body", {{ backgroundColor: "{BROWN}", duration: 0.7, ease: "sine.inOut" }}, "tideUp+=0.25");

// ---- beat 5: wordmark rises alone, centered (6.5 - 8.3s)
tl.addLabel("type", 6.7)
  .to("#wmButter", {{ autoAlpha: 1, y: 0, duration: 1.6, ease: "sine.out" }}, "type")
  .to("#wmSticks", {{ autoAlpha: 1, y: 0, duration: 1.6, ease: "sine.out" }}, "type+=0.15")
  .to(".golfLetter", {{ autoAlpha: 1, y: 0, duration: 1.2, ease: "sine.out", stagger: 0.1 }}, "type+=0.45");

// ---- beat 6: breathing hold (8.5 - 9.4s)
tl.to({{}}, {{ duration: 0.1 }}, 9.7);  // quiet hold to the end

// slow camera push, whole film
tl.to("svg", {{ scale: 1.0, duration: 5.5, ease: "sine.out" }}, 0);

// reduced motion: land on the finished lockup immediately
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {{
  tl.progress(1).pause();
  gsap.set("#tide", {{ y: -85 }});
  gsap.set("body", {{ backgroundColor: "{BROWN}" }});
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

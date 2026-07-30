"""Assemble gsap/intro.html — the Butter Sticks intro as a GSAP/SVG animation.

v5 "Seedance-matched glaze":
Motion copied from reference/melt1.mp4 (Seedance 2.0, 8s): the pat melts
into a cap conforming to the ball's crown (BSG riding it, warping, alive
deep into the melt); butter runs down the ball in discrete STREAMS with
dimples visible between them (clipped to the ball's silhouette so they
hug the sphere); streams continue down the tee; droplets detach
throughout. The glazed ball stays whole, then the entire glazed object
sinks into the pond. ~13s.
?seek=<sec> frame-grabs, prefers-reduced-motion, click to replay.
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


def _drip_tips():
    """Find the painted drips' tips on the gold vector's bottom edge —
    the frozen melt the animation resumes."""
    import collections
    from svgpathtools import parse_path
    path = parse_path(G["gold"][0]["d"])
    bottom = collections.defaultdict(float)
    for i in range(4000):
        pt = path.point(i / 3999)
        b = int(pt.real // 10) * 10
        if pt.imag > bottom[b]:
            bottom[b] = pt.imag
    runs, cur = [], []
    for b in sorted(bottom):
        if 1540 <= b <= 1935 and bottom[b] > 975:
            cur.append((b, bottom[b]))
        else:
            if len(cur) >= 2:
                runs.append(cur)
            cur = []
    if len(cur) >= 2:
        runs.append(cur)
    tips = []
    for r in runs:
        xs = [q[0] for q in r]
        tx, ty = max(r, key=lambda q: q[1])
        tips.append((tx + 5, ty, max(xs) + 10 - min(xs)))
    tips.sort(key=lambda t: -t[1])          # longest painted drip resumes first
    return tips[:6]


DRIP_TIPS = _drip_tips()
print("painted drip tips:", [(round(t[0]), round(t[1]), t[2]) for t in DRIP_TIPS])

# Ball streams measured from the Seedance reference mid-melt frames:
# (center offset, width, final length, start order)
STREAMS = [(-110, 30, 330, 3), (-50, 42, 400, 0), (8, 34, 360, 1),
           (62, 38, 395, 2), (118, 26, 300, 4)]


def molten_members(cls):
    """The liquid, Seedance-matched: pat art + conforming crown cap +
    ball streams (clipped to the sphere) + tee streams + resumed drips.
    Same markup for the gold body and the green rim underneath."""
    runnels = ""
    for i, (tx, ty, w) in enumerate(DRIP_TIPS):
        drift = max(-40, min(40, (tx - 1742) * 0.35))
        runnels += (f'<ellipse class="{cls}Run" cx="{tx:.0f}" cy="{ty - 26:.0f}" '
                    f'rx="{w / 2 - 2:.0f}" ry="16" data-drift="{drift:.0f}" data-i="{i}"/>\n')
    streams = ""
    for j, (dx, w, ln, order) in enumerate(STREAMS):
        streams += (f'<rect class="{cls}Stream" x="{BALL_CX + dx - w / 2:.0f}" y="892" '
                    f'width="{w}" height="{ln}" rx="{w / 2}" data-order="{order}"/>\n')
    return f"""
    <g class="{cls}PatArt">{paths("gold", keep_fill=False)}</g>
    <g clip-path="url(#ballClip)">
      <ellipse class="{cls}Cap" cx="{BALL_CX}" cy="938" rx="168" ry="96"/>
      {streams}
    </g>
    <ellipse class="{cls}TeeCup" cx="1741" cy="1192" rx="54" ry="20"/>
    <rect class="{cls}TeeStreamA" x="1714" y="1206" width="16" height="176" rx="8"/>
    <rect class="{cls}TeeStreamB" x="1744" y="1206" width="13" height="150" rx="6"/>
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
    <clipPath id="ballClip">
      <circle cx="{BALL_CX}" cy="{BALL_CY}" r="{BALL_R + 2}"/>
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

  <!-- droplets detaching from the glaze into the pond -->
  <g id="dripLayer" filter="url(#goo)" fill="{GOLDEN}" transform="translate(105,22.3) scale(0.4)">
    <ellipse class="drop" cx="1688" cy="1150" rx="22" ry="30"/>
    <ellipse class="drop" cx="1748" cy="1240" rx="26" ry="34"/>
    <ellipse class="drop" cx="1802" cy="1170" rx="20" ry="28"/>
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
gsap.set(["#pondBack", "#pondFront", "#tide"], {{ y: 920 }});
gsap.set("svg", {{ scale: 1.07, transformOrigin: "50% 50%" }});
gsap.set(".rRun, .gRun", {{ autoAlpha: 0 }});
gsap.set(".rCap, .gCap", {{ autoAlpha: 0, scale: 0.55, transformOrigin: "50% 20%" }});
gsap.set(".rStream, .gStream", {{ autoAlpha: 0, scaleY: 0.05, transformOrigin: "50% 0%" }});
gsap.set(".rTeeCup, .gTeeCup, .rTeeStreamA, .gTeeStreamA, .rTeeStreamB, .gTeeStreamB", {{ autoAlpha: 0 }});
gsap.set(".rTeeStreamA, .gTeeStreamA, .rTeeStreamB, .gTeeStreamB", {{ scaleY: 0.08, transformOrigin: "50% 0%" }});

// endless sideways drift on every liquid surface (wavelength = 400)
gsap.to("#pondBack path",  {{ x: -400, duration: 2.1, ease: "none", repeat: -1 }});
gsap.to("#pondFront path", {{ x: -400, duration: 2.8, ease: "none", repeat: -1 }});
gsap.to("#tide path",      {{ x: -400, duration: 2.4, ease: "none", repeat: -1 }});

const tl = gsap.timeline({{ defaults: {{ ease: "power2.out" }} }});

// ---- beat 1: arrival on cream (0 - 1.5s)
tl.addLabel("in", 0.15)
  .to("#badgeMove", {{ autoAlpha: 1, duration: 0.7, ease: "sine.out" }}, "in")
  .to("#badgeMove", {{ scale: 1.0, duration: 1.2, ease: "sine.out" }}, "in");

// ---- beat 2: the frozen melt resumes (1.6 - 3.4s)  [ref: 0.0 - 1.8s]
tl.addLabel("melt", 1.6)
  .to("#speed", {{ autoAlpha: 0, duration: 0.4 }}, "melt")
  .to("#rimDilate", {{ attr: {{ radius: 4 }}, duration: 2.6, ease: "sine.inOut" }}, "melt+=0.4")
  .to(".gRun", {{ autoAlpha: 1, duration: 0.2, stagger: 0.1 }}, "melt+=0.05");

$$(".rRun, .gRun").forEach((r) => {{
  const drift = parseFloat(r.dataset.drift);
  const t0 = 0.12 + parseInt(r.dataset.i, 10) * 0.22;   // longest painted drip resumes first
  if (r.classList.contains("rRun")) {{
    tl.to(r, {{ autoAlpha: 1, duration: 0.45, ease: "sine.in" }}, "melt+=" + (t0 + 0.2));
  }}
  tl.to(r, {{ attr: {{ ry: 44, cy: "+=40" }}, scaleX: 0.78, transformOrigin: "50% 50%", duration: 0.8, ease: "power1.in" }}, "melt+=" + t0)
    .to(r, {{ attr: {{ cy: 1235, cx: "+=" + drift }}, scaleY: 1.3, scaleX: 0.68,
      transformOrigin: "50% 0%", duration: 1.9 + Math.abs(drift) / 55,
      ease: "sine.in" }}, "melt+=" + (t0 + 0.8));
}});

// ---- beat 3: the pat becomes a cap conforming to the crown (2.3 - 4.4s)  [ref: 1.5 - 3.0s]
tl.to(".rPatArt, .gPatArt", {{ scaleY: 0.34, scaleX: 0.60, transformOrigin: "50% 100%",
      duration: 2.0, ease: "power1.inOut" }}, "melt+=0.7")
  .to(".rPatArt", {{ opacity: 0, duration: 1.7, ease: "sine.in" }}, "melt+=1.0")
  .to("#eraserRect", {{ attr: {{ height: 300 }}, duration: 1.9, ease: "power1.out" }}, "melt+=0.6")
  .to(".rCap, .gCap", {{ autoAlpha: 1, duration: 0.5, ease: "sine.inOut" }}, "melt+=0.9")
  .to(".rCap, .gCap", {{ scale: 1.0, duration: 1.9, ease: "power1.inOut" }}, "melt+=0.9")
  .to(".rCap, .gCap", {{ attr: {{ cy: "+=26", ry: 108 }}, duration: 2.6, ease: "sine.inOut" }}, "melt+=3.0")
  .to("#hornCover", {{ opacity: 1, duration: 0.5, ease: "sine.inOut" }}, "melt+=1.2")
  // BSG rides the cap, warps with its curve, stays alive deep into the melt
  .to(".bsgL", {{ y: 132, scaleY: 1.18, transformOrigin: "50% 0%", duration: 2.0,
      ease: "power1.inOut", stagger: 0.08 }}, "melt+=0.7")
  .to(".bsgL", {{ rotation: (i) => [-6, 0, 6, 2][i % 4], duration: 2.0, ease: "sine.inOut", stagger: 0.08 }}, "melt+=0.9")
  .to(".bsgL", {{ fill: "{GOLDEN}", duration: 1.2, ease: "sine.in", stagger: 0.1 }}, "melt+=2.6")
  .to(".bsgL", {{ autoAlpha: 0, duration: 0.9, ease: "sine.inOut", stagger: 0.1 }}, "melt+=3.8")
  .to("#dispMap", {{ attr: {{ scale: 24 }}, duration: 1.6, ease: "sine.in" }}, "melt+=2.2")
  .to("#bsgBlur", {{ attr: {{ stdDeviation: "0 16" }}, duration: 1.4, ease: "sine.in" }}, "melt+=2.6");

// ---- beat 4: streams glaze the ball, dimples peeking through (3.2 - 7.0s)  [ref: 2.0 - 6.5s]
tl.addLabel("glaze", 3.2);
$$(".rStream, .gStream").forEach((st) => {{
  const order = parseInt(st.dataset.order, 10);
  const t0 = order * 0.45;
  tl.to(st, {{ autoAlpha: 1, duration: 0.3, ease: "sine.in" }}, "glaze+=" + t0)
    .to(st, {{ scaleY: 1.0, duration: 2.0 + order * 0.15, ease: "power1.inOut" }}, "glaze+=" + (t0 + 0.1));
}});

// streams keep swelling gently — coverage grows but never seals the dimples
tl.to(".rStream, .gStream", {{ scaleX: 1.28, transformOrigin: "50% 50%", duration: 1.9,
      ease: "sine.inOut" }}, "glaze+=2.7")
  // butter reaches the tee and runs down it
  .to(".rTeeCup, .gTeeCup", {{ autoAlpha: 1, duration: 0.35, ease: "sine.out" }}, "glaze+=2.4")
  .to(".rTeeStreamA, .gTeeStreamA", {{ autoAlpha: 1, duration: 0.2 }}, "glaze+=2.7")
  .to(".rTeeStreamA, .gTeeStreamA", {{ scaleY: 1, duration: 1.3, ease: "power1.in" }}, "glaze+=2.75")
  .to(".rTeeStreamB, .gTeeStreamB", {{ autoAlpha: 1, duration: 0.2 }}, "glaze+=3.15")
  .to(".rTeeStreamB, .gTeeStreamB", {{ scaleY: 1, duration: 1.2, ease: "power1.in" }}, "glaze+=3.2")
  // pond rises to receive the drips
  .to("#pondBack", {{ y: 585, duration: 1.45, ease: "power1.inOut" }}, "glaze+=3.4")
  .to("#pondFront", {{ y: 606, duration: 1.45, ease: "power1.inOut" }}, "glaze+=3.52");

// droplets detach from the glaze throughout  [ref: continuous]
$$(".drop").forEach((d, i) => {{
  [0, 1, 2].forEach((w) => {{
    const t0 = 4.0 + i * 0.45 + w * 1.25;
    tl.fromTo(d, {{ autoAlpha: 1, y: 0, scaleY: 1, transformOrigin: "50% 0%" }},
      {{ y: 385, scaleY: 1.9, duration: 1.15, ease: "power1.in", immediateRender: false }}, t0)
      .to(d, {{ autoAlpha: 0, duration: 0.12 }}, t0 + 1.0);
  }});
}});

// ---- beat 5: the whole glazed object sinks into the river (8.0 - 9.4s)
tl.addLabel("sink", 8.0)
  .to("#badgeMove", {{ y: 660, duration: 1.35, ease: "power1.in" }}, "sink")
  .to("#badgeMove", {{ autoAlpha: 0, duration: 0.32, ease: "sine.in" }}, "sink+=1.0");

// ---- beat 6: the brown tide inversion (9.6 - 10.5s)
tl.addLabel("tideUp", 9.6)
  .to("#tide", {{ y: -85, duration: 0.9, ease: "power2.inOut" }}, "tideUp")
  .to("body", {{ backgroundColor: "{BROWN}", duration: 0.7, ease: "sine.inOut" }}, "tideUp+=0.25");

// ---- beat 7: wordmark rises alone, centered (10.9 - 12.6s)
tl.addLabel("type", 10.9)
  .to("#wmButter", {{ autoAlpha: 1, y: 0, duration: 1.6, ease: "sine.out" }}, "type")
  .to("#wmSticks", {{ autoAlpha: 1, y: 0, duration: 1.6, ease: "sine.out" }}, "type+=0.15")
  .to(".golfLetter", {{ autoAlpha: 1, y: 0, duration: 1.2, ease: "sine.out", stagger: 0.1 }}, "type+=0.45");

// quiet hold to the end
tl.to({{}}, {{ duration: 0.1 }}, 13.0);

// slow camera push through the melt
tl.to("svg", {{ scale: 1.0, duration: 7.5, ease: "sine.out" }}, 0);

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

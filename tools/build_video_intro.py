"""Assemble gsap/intro_video.html — the hybrid intro:

The Seedance 2.0 melt VIDEO plays the melt (black background chroma-keyed
to transparent so it lives on our cream page), while GSAP/SVG overlays do
what video can't: the golden river rises to catch the drips, the brown
tide inverts the palette, and the crisp vector wordmark lands centered.

Builds two variants:
  gsap/intro_video.html          — site build, references melt.mp4
  gsap/intro_video_artifact.html — self-contained, video inlined base64
"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = json.loads((ROOT / "gsap" / "groups.json").read_text(encoding="utf-8"))
GSAP = (ROOT / "gsap" / "gsap.min.js").read_text(encoding="utf-8")

CREAM = "#EADDC1"
BROWN = "#8C5E2E"
GOLDEN = "#D9B64E"
DEEP = "#BD9A42"

import subprocess

SRC = ROOT / "reference" / "melt2.mp4"
if not SRC.exists():
    SRC = ROOT / "reference" / "melt1.mp4"
VIDEO_DUR = float(subprocess.run(
    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
     "format=duration", "-of", "csv=p=0", str(SRC)],
    capture_output=True, text=True).stdout.strip())
VIDEO_START = 0.35          # timeline second when the video starts playing
V_END = VIDEO_START + VIDEO_DUR
print(f"video: {SRC.name}  duration {VIDEO_DUR:.2f}s")


def paths(group, cls=""):
    out = []
    for it in G[group]:
        c = f' class="{cls}"' if cls else ""
        out.append(f'<path d="{it["d"]}" fill-rule="evenodd"{c}/>')
    return "\n".join(out)


def wave(width=3600, x0=-1000, amp=30, wl=400, depth=1100):
    n = int(width / wl)
    seg = ""
    for _ in range(n):
        seg += f"q{wl / 4:.0f} {-amp} {wl / 2:.0f} 0 q{wl / 4:.0f} {amp} {wl / 2:.0f} 0 "
    return f"M{x0} 0 {seg} v{depth} h{-width} Z"


def build(video_src):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Butter Sticks Golf — Intro</title>
<style>
  html, body {{ margin: 0; height: 100%; background: {CREAM}; overflow: hidden; }}
  #melt {{
    position: fixed; left: 50%; top: 47%;
    height: 66vh; transform: translate(-50%, -50%);
    filter: url(#unblack);
    opacity: 0;
  }}
  .overlay {{ position: fixed; inset: 0; width: 100vw; height: 100vh;
              pointer-events: none; }}
</style>
</head>
<body>

<svg width="0" height="0" style="position:absolute">
  <defs>
    <filter id="unblack" color-interpolation-filters="sRGB">
      <feColorMatrix in="SourceGraphic" type="matrix"
        values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0.35 0.55 0.2 0 0" result="lum"/>
      <feComponentTransfer in="lum" result="mask">
        <feFuncA type="linear" slope="10" intercept="-0.45"/>
      </feComponentTransfer>
      <feComposite in="SourceGraphic" in2="mask" operator="in"/>
    </filter>
  </defs>
</svg>

<video id="melt" src="{video_src}" muted playsinline preload="auto"></video>

<!-- liquids: full-bleed cover -->
<svg class="overlay" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <g clip-path="url(#lc)"><clipPath id="lc"><rect width="1600" height="900"/></clipPath>
    <g id="pondBack"><path d="{wave(amp=34)}" fill="{DEEP}"/></g>
    <g id="pondFront"><path d="{wave(amp=26)}" fill="{GOLDEN}"/></g>
    <g id="tide"><path d="{wave(amp=38)}" fill="{BROWN}"/></g>
  </g>
</svg>

<!-- wordmark: fit, never cropped -->
<svg class="overlay" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid meet"
     aria-label="Butter Sticks Golf">
  <g id="wmMove" transform="translate(538.0,291.8) scale(0.41)" fill="{CREAM}">
    <g id="wmButter">{paths("wm_butter")}</g>
    <g id="wmSticks">{paths("wm_sticks")}</g>
    <g id="wmGolf">{paths("wm_golf", cls="golfLetter")}</g>
  </g>
</svg>

<script>{GSAP}</script>
<script>
const video = document.getElementById("melt");
const VIDEO_START = {VIDEO_START};
const VIDEO_DUR = {VIDEO_DUR};

gsap.set(["#wmButter", "#wmSticks"], {{ autoAlpha: 0, y: 40 }});
gsap.set(".golfLetter", {{ autoAlpha: 0, y: 24 }});
gsap.set(["#pondBack", "#pondFront", "#tide"], {{ y: 920 }});

// endless sideways drift on every liquid surface
gsap.to("#pondBack path",  {{ x: -400, duration: 2.1, ease: "none", repeat: -1 }});
gsap.to("#pondFront path", {{ x: -400, duration: 2.8, ease: "none", repeat: -1 }});
gsap.to("#tide path",      {{ x: -400, duration: 2.4, ease: "none", repeat: -1 }});

const tl = gsap.timeline({{ defaults: {{ ease: "power2.out" }} }});

// ---- the badge fades in and the Seedance melt plays (0 - 8.4s)
tl.to("#melt", {{ opacity: 1, duration: 0.8, ease: "sine.out" }}, 0.15)
  .call(() => {{ if (!seeking) video.play(); }}, null, VIDEO_START);

// ---- the golden river rises to catch the drips (5.9 - 7.4s)
tl.to("#pondBack", {{ y: 585, duration: 1.5, ease: "power1.inOut" }}, {V_END - 2.5:.2f})
  .to("#pondFront", {{ y: 606, duration: 1.5, ease: "power1.inOut" }}, {V_END - 2.35:.2f});

// ---- the tide inverts everything as the melt completes (8.45 - 9.4s)
tl.addLabel("tideUp", {V_END + 0.05:.2f})
  .to("#tide", {{ y: -85, duration: 0.95, ease: "power2.inOut" }}, "tideUp")
  .to("body", {{ backgroundColor: "{BROWN}", duration: 0.7, ease: "sine.inOut" }}, "tideUp+=0.25")
  .to("#melt", {{ opacity: 0, duration: 0.45, ease: "sine.in" }}, "tideUp+=0.35");

// ---- the wordmark surfaces, centered (9.7 - 11.4s)
tl.addLabel("type", {V_END + 1.3:.2f})
  .to("#wmButter", {{ autoAlpha: 1, y: 0, duration: 1.6, ease: "sine.out" }}, "type")
  .to("#wmSticks", {{ autoAlpha: 1, y: 0, duration: 1.6, ease: "sine.out" }}, "type+=0.15")
  .to(".golfLetter", {{ autoAlpha: 1, y: 0, duration: 1.2, ease: "sine.out", stagger: 0.1 }}, "type+=0.45");

// quiet hold to the end
tl.to({{}}, {{ duration: 0.1 }}, {V_END + 3.8:.2f});

// reduced motion: land on the finished lockup immediately
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {{
  tl.progress(1).pause();
  video.style.display = "none";
  gsap.set("#tide", {{ y: -85 }});
  gsap.set("body", {{ backgroundColor: "{BROWN}" }});
}}

// headless frame-grab support: ?seek=<seconds>
const params = new URLSearchParams(location.search);
const seekParam = params.get("seek");
const seeking = seekParam !== null;
if (seeking) {{
  const t = parseFloat(seekParam);
  tl.pause(t);
  gsap.globalTimeline.pause();
  video.currentTime = Math.max(0, Math.min(VIDEO_DUR - 0.05, t - VIDEO_START));
  video.pause();
}}

document.body.addEventListener("click", () => {{
  video.pause(); video.currentTime = 0; tl.restart();
}});
window.introTimeline = tl;
</script>
</body>
</html>
"""


import shutil
shutil.copy(SRC, ROOT / "gsap" / "melt.mp4")
subprocess.run(["ffmpeg", "-y", "-i", str(SRC), "-vf", "scale=576:-2",
                "-c:v", "libx264", "-crf", "28", "-preset", "slow",
                "-movflags", "+faststart", "-an",
                str(ROOT / "gsap" / "melt_small.mp4")],
               capture_output=True)

site = build("melt.mp4")
(ROOT / "gsap" / "intro_video.html").write_text(site, encoding="utf-8")

b64 = base64.b64encode((ROOT / "gsap" / "melt_small.mp4").read_bytes()).decode()
artifact = build(f"data:video/mp4;base64,{b64}")
import re
m_title = re.search(r"<title>.*?</title>", artifact, re.S)
m_style = re.search(r"<style>.*?</style>", artifact, re.S)
m_body = re.search(r"<body>(.*)</body>", artifact, re.S)
(ROOT / "gsap" / "intro_video_artifact.html").write_text(
    m_title.group(0) + "\n" + m_style.group(0) + m_body.group(1), encoding="utf-8")

print(f"site:     {(ROOT / 'gsap' / 'intro_video.html').stat().st_size / 1024:.0f} KB (+ melt.mp4)")
print(f"artifact: {(ROOT / 'gsap' / 'intro_video_artifact.html').stat().st_size / 1024:.0f} KB self-contained")

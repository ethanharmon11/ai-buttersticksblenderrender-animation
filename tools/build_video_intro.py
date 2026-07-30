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

<!-- the bloom born from the droplet's impact -->
<div id="bloom" style="position:fixed; width:300px; height:300px; border-radius:50%;
  margin:-150px 0 0 -150px; z-index:3; visibility:hidden;
  background: radial-gradient(circle, {BROWN} 0%, {BROWN} 58%, rgba(140,94,46,0) 74%);
  pointer-events:none;"></div>
<div id="brownField" class="overlay" style="opacity:0; background: {BROWN}; z-index:4;"></div>



<!-- wordmark: fit, never cropped -->
<svg class="overlay" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid meet"
     style="z-index:5" aria-label="Butter Sticks Golf">
  <g id="wmMove" transform="translate(538.0,291.8) scale(0.41)" fill="{CREAM}">
    <g id="wmButter">{paths("wm_butter")}</g>
    <g id="wmSticks">{paths("wm_sticks")}</g>
    <g id="wmGolf">{paths("wm_golf", cls="golfLetter")}</g>
  </g>
</svg>

<script>{GSAP}</script>
<script>
gsap.ticker.lagSmoothing(0);
const $$ = (s) => gsap.utils.toArray(s);
const video = document.getElementById("melt");
const VIDEO_START = {VIDEO_START};
const VIDEO_DUR = {VIDEO_DUR};

gsap.set(["#wmButter", "#wmSticks"], {{ autoAlpha: 0, y: 40 }});
gsap.set(".golfLetter", {{ autoAlpha: 0, y: 24 }});

// melt2's own last droplet exits the frame bottom at video-time 7.90s,
// x = 72.6% across (measured by pixel-tracking the gold drops)
const vh = innerHeight, vw = innerWidth;
const vidH = vh * 0.66, vidW = vidH * 1144 / 1808;
const vidL = vw / 2 - vidW / 2, vidT = vh * 0.47 - vidH / 2;
const exitPt = {{ x: vidL + vidW * 0.726, y: vidT + vidH + vh * 0.012 }};
gsap.set("#bloom", {{ left: exitPt.x, top: exitPt.y, scale: 0,
  transformOrigin: "50% 50%", autoAlpha: 1 }});
const bloomScale = Math.hypot(vw, vh) / 135;

const tl = gsap.timeline({{ defaults: {{ ease: "power2.out" }} }});

// ---- the badge fades in and the Seedance melt plays (0 - 8.4s)
tl.to("#melt", {{ opacity: 1, duration: 0.8, ease: "sine.out" }}, 0.15)
  .call(() => {{ if (!seeking) video.play(); }}, null, VIDEO_START);

// ---- the video's own last drop exits, and the brand blooms where it lands
tl.addLabel("drop", {VIDEO_START + 7.90:.2f})
  .fromTo("#bloom", {{ scale: 0 }}, {{ scale: bloomScale, duration: 1.5,
      ease: "power1.inOut", immediateRender: false }}, "drop+=0.06")
  .to("body", {{ backgroundColor: "{BROWN}", duration: 0.6, ease: "sine.inOut" }}, "drop+=1.0")
  .to("#brownField", {{ opacity: 1, duration: 0.4 }}, "drop+=1.35")
  .to("#melt", {{ opacity: 0, duration: 0.2 }}, "drop+=1.45");

// ---- the wordmark surfaces, centered
tl.addLabel("type", {VIDEO_START + 7.90 + 1.9:.2f})
  .to("#wmButter", {{ autoAlpha: 1, y: 0, duration: 1.6, ease: "sine.out" }}, "type")
  .to("#wmSticks", {{ autoAlpha: 1, y: 0, duration: 1.6, ease: "sine.out" }}, "type+=0.15")
  .to(".golfLetter", {{ autoAlpha: 1, y: 0, duration: 1.2, ease: "sine.out", stagger: 0.1 }}, "type+=0.45");

// quiet hold to the end
tl.to({{}}, {{ duration: 0.1 }}, {VIDEO_START + 7.90 + 4.6:.2f});

// reduced motion: land on the finished lockup immediately
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {{
  tl.progress(1).pause();
  video.style.display = "none";
  gsap.set("#brownField", {{ opacity: 1 }});
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

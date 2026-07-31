"""Assemble gsap/intro_fade.html — the quiet intro.

"Butter Sticks Golf" fades in on brand brown, breathes, and fades away.
No gimmicks: opacity, a 2% settle, a soft focus resolve. ~4.5s.

Builds intro_fade.html, intro_fade_artifact.html, intro_fade_embed.html
(click = skip, postMessage "bsg-intro-done", self-dismisses).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = json.loads((ROOT / "gsap" / "groups.json").read_text(encoding="utf-8"))
GSAP = (ROOT / "gsap" / "gsap.min.js").read_text(encoding="utf-8")

CREAM = "#EADDC1"
BROWN = "#8C5E2E"


def paths(group, cls=""):
    out = []
    for it in G[group]:
        c = f' class="{cls}"' if cls else ""
        out.append(f'<path d="{it["d"]}" fill-rule="evenodd"{c}/>')
    return "\n".join(out)


html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Butter Sticks Golf</title>
<style>
  html, body {{ margin: 0; height: 100%; background: {BROWN}; overflow: hidden; }}
  .stage {{ position: fixed; inset: 0; }}
  svg {{ width: 100vw; height: 100vh; }}
</style>
</head>
<body>
<div class="stage">
<svg viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid meet" aria-label="Butter Sticks Golf">
  <defs>
    <filter id="focus" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur id="focusBlur" stdDeviation="0"/>
    </filter>
  </defs>
  <!-- wordmark centered: native bbox spans ~1244x420 at scale 0.41 -->
  <g id="wordmark" transform="translate(538.0,291.8) scale(0.41)" fill="{CREAM}"
     filter="url(#focus)">
    <g id="wmButter">{paths("wm_butter")}</g>
    <g id="wmSticks">{paths("wm_sticks")}</g>
    <g id="wmGolf">{paths("wm_golf", cls="golfLetter")}</g>
  </g>
</svg>
</div>

<script>{GSAP}</script>
<script>
gsap.ticker.lagSmoothing(0);

const focusBlur = document.getElementById("focusBlur");
const blur = {{ v: 6 }};

gsap.set("#wordmark", {{ autoAlpha: 0, scale: 1.025, svgOrigin: "800 450" }});

const tl = gsap.timeline({{ defaults: {{ ease: "sine.inOut" }} }});

// in: opacity + focus resolve + 2% settle, script first, GOLF follows
tl.addLabel("in", 0.35)
  .to("#wordmark", {{ autoAlpha: 1, duration: 1.6 }}, "in")
  .to("#wordmark", {{ scale: 1.0, duration: 2.2, ease: "power2.out" }}, "in")
  .to(blur, {{ v: 0, duration: 1.3, ease: "power2.out",
      onUpdate: () => focusBlur.setAttribute("stdDeviation", blur.v.toFixed(2)) }}, "in")
  .from(".golfLetter", {{ autoAlpha: 0, duration: 0.9, stagger: 0.06,
      ease: "sine.out" }}, "in+=0.55");

// hold — let it sit
tl.addLabel("hold", 2.4).to({{}}, {{ duration: 1.4 }}, "hold");

// out: one clean exhale
tl.addLabel("out", 3.8)
  .to("#wordmark", {{ autoAlpha: 0, scale: 1.012, duration: 0.9,
      ease: "sine.in" }}, "out");

tl.to({{}}, {{ duration: 0.05 }}, 4.75);

if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {{
  gsap.set("#wordmark", {{ scale: 1 }});
  focusBlur.setAttribute("stdDeviation", 0);
  tl.timeScale(1.6);
}}

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

out = ROOT / "gsap" / "intro_fade.html"
out.write_text(html, encoding="utf-8")

# embed: click skips, completion notifies the parent page and self-dismisses
embed = html.replace(
    """document.body.addEventListener("click", () => tl.restart());""",
    """document.body.addEventListener("click", () => tl.progress(1));  // click = skip
tl.eventCallback("onComplete", () => {
  try { parent.postMessage("bsg-intro-done", "*"); } catch (e) {}
  gsap.to(document.body, { opacity: 0, duration: 0.5,
    onComplete: () => { document.body.style.display = "none"; } });
});""")
(ROOT / "gsap" / "intro_fade_embed.html").write_text(embed, encoding="utf-8")

m_title = re.search(r"<title>.*?</title>", html, re.S)
m_style = re.search(r"<style>.*?</style>", html, re.S)
m_body = re.search(r"<body>(.*)</body>", html, re.S)
(ROOT / "gsap" / "intro_fade_artifact.html").write_text(
    m_title.group(0) + "\n" + m_style.group(0) + m_body.group(1), encoding="utf-8")

print(f"WROTE {out} ({out.stat().st_size / 1024:.0f} KB)")

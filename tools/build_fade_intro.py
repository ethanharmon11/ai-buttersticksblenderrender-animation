"""Assemble the quiet lining intros.

Like the inside of the Butter Sticks box: a washed half-drop repeat of the
butter-ball badge on cream, with "Butter Sticks Golf" in copper (#8C5E2E)
fading in on top. The wordmark breathes in with a focus resolve + 2%
settle, holds, exhales. ~5s.

Two variants:
  gsap/intro_fade.html        tone-on-tone — badge in copper/cream only
  gsap/intro_fade_color.html  the badge in its own brand colors, washed back

Each builds a _embed (click = skip, postMessage "bsg-intro-done",
self-dismisses) and an _artifact (shareable; adds a replay hint).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = json.loads((ROOT / "gsap" / "groups.json").read_text(encoding="utf-8"))
GSAP = (ROOT / "gsap" / "gsap.min.js").read_text(encoding="utf-8")

CREAM = "#EADDC1"
BROWN = "#8C5E2E"

# badge silhouette bbox (probed via getBBox)
MX, MY, MW, MH = 1530.9, 743.6, 413.2, 651.1

# half-drop repeat: motif ~76 units wide on the 1600-unit stage
S = 0.184
TW, TH = 250, 296
M = f"scale({S}) translate({-MX:.1f},{-MY:.1f})"


def paths(group, fill=None, opacity=None, cls=""):
    out = []
    for it in G[group]:
        f = f' fill="{fill}"' if fill else f' fill="{it["fill"]}"'
        o = f' opacity="{opacity}"' if opacity else ""
        c = f' class="{cls}"' if cls else ""
        out.append(f'<path d="{it["d"]}" fill-rule="evenodd"{f}{o}{c}/>')
    return "\n".join(out)


def motif(colored):
    """The badge as lining art.

    Tone-on-tone: copper silhouette, cream interiors — texture, not image.
    Colored: the badge's own palette (green outline, golden butter, rust
    tee and script) with the ball left cream so the paper shows through.
    """
    if not colored:
        return (
            paths("sil", fill=BROWN)
            + paths("gold", fill=CREAM)
            + paths("ball", fill=CREAM)
            + paths("tee", fill=CREAM)
            + paths("dimples_green", fill=BROWN, opacity=0.5)
            + paths("bsg", fill=BROWN)
        )
    return (
        paths("sil")            # #21522a green silhouette
        + paths("gold")         # #e9af34 butter pat
        + paths("ball", fill=CREAM)
        + paths("tee")          # rust tee
        + paths("dimples_green")
        + paths("speed")
        + paths("bsg")          # rust script
    )


def build(colored, lining_opacity):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Butter Sticks Golf</title>
<style>
  html, body {{ margin: 0; height: 100%; background: {CREAM}; overflow: hidden; }}
  .stage {{ position: fixed; inset: 0; }}
  svg {{ width: 100vw; height: 100vh; }}
</style>
</head>
<body>
<div class="stage">
<svg viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" aria-label="Butter Sticks Golf">
  <defs>
    <pattern id="lining" x="0" y="0" width="{TW}" height="{TH}" patternUnits="userSpaceOnUse">
      <g transform="translate(18,14) {M}">{motif(colored)}</g>
      <g transform="translate({18 + TW // 2},{14 + TH // 2}) {M}">{motif(colored)}</g>
    </pattern>
    <filter id="focus" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur id="focusBlur" stdDeviation="0"/>
    </filter>
  </defs>

  <rect width="1600" height="900" fill="{CREAM}"/>
  <!-- the lining: oversized so it can drift, washed back -->
  <g id="liningDrift">
    <rect x="-300" y="-320" width="2300" height="1600" fill="url(#lining)"
          opacity="{lining_opacity}"/>
  </g>

  <!-- wordmark centered on top, copper brown -->
  <g id="wordmark" transform="translate(538.0,291.8) scale(0.41)" fill="{BROWN}"
     filter="url(#focus)">
    <g id="wmButter">{paths("wm_butter", fill=BROWN)}</g>
    <g id="wmSticks">{paths("wm_sticks", fill=BROWN)}</g>
    <g id="wmGolf">{paths("wm_golf", fill=BROWN, cls="golfLetter")}</g>
  </g>
</svg>
</div>

<script>{GSAP}</script>
<script>
gsap.ticker.lagSmoothing(0);

const focusBlur = document.getElementById("focusBlur");
const blur = {{ v: 6 }};

gsap.set("#wordmark", {{ autoAlpha: 0, scale: 1.025, svgOrigin: "800 450" }});
gsap.set("#liningDrift", {{ autoAlpha: 0 }});

const tl = gsap.timeline({{ defaults: {{ ease: "sine.inOut" }} }});

// the lining surfaces first, like opening the box
tl.to("#liningDrift", {{ autoAlpha: 1, duration: 1.4, ease: "sine.out" }}, 0.15)
  .to("#liningDrift", {{ x: 34, y: 24, duration: 9, ease: "none" }}, 0);

// the wordmark breathes in: opacity + focus resolve + 2% settle
tl.addLabel("in", 0.55)
  .to("#wordmark", {{ autoAlpha: 1, duration: 1.6 }}, "in")
  .to("#wordmark", {{ scale: 1.0, duration: 2.2, ease: "power2.out" }}, "in")
  .to(blur, {{ v: 0, duration: 1.3, ease: "power2.out",
      onUpdate: () => focusBlur.setAttribute("stdDeviation", blur.v.toFixed(2)) }}, "in")
  .from(".golfLetter", {{ autoAlpha: 0, duration: 0.9, stagger: 0.06,
      ease: "sine.out" }}, "in+=0.55");

// hold — let it sit
tl.addLabel("hold", 2.6).to({{}}, {{ duration: 1.4 }}, "hold");

// out: one clean exhale, lining lingers a breath longer
tl.addLabel("out", 4.0)
  .to("#wordmark", {{ autoAlpha: 0, scale: 1.012, duration: 0.9,
      ease: "sine.in" }}, "out")
  .to("#liningDrift", {{ autoAlpha: 0, duration: 0.7, ease: "sine.in" }}, "out+=0.25");

tl.to({{}}, {{ duration: 0.05 }}, 5.0);

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


def emit(stem, html):
    (ROOT / "gsap" / f"{stem}.html").write_text(html, encoding="utf-8")

    # production embed: click skips, completion notifies the parent page
    embed = html.replace(
        """document.body.addEventListener("click", () => tl.restart());""",
        """document.body.addEventListener("click", () => tl.progress(1));  // click = skip
tl.eventCallback("onComplete", () => {
  try { parent.postMessage("bsg-intro-done", "*"); } catch (e) {}
  gsap.to(document.body, { opacity: 0, duration: 0.5,
    onComplete: () => { document.body.style.display = "none"; } });
});""")
    (ROOT / "gsap" / f"{stem}_embed.html").write_text(embed, encoding="utf-8")

    # shareable copy: same intro plus a quiet replay hint once the mark
    # exhales (a shared link otherwise plays once and leaves an empty screen)
    art = html.replace("</style>", f"""  #replayHint {{
    position: fixed; left: 0; right: 0; bottom: 7vh; text-align: center;
    font: 500 11px/1 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    letter-spacing: 0.24em; text-transform: uppercase; color: {BROWN};
    opacity: 0; pointer-events: none;
  }}
</style>""").replace(
        """window.introTimeline = tl;""",
        """const hint = document.createElement("div");
hint.id = "replayHint";
hint.textContent = "click to replay";
document.body.appendChild(hint);
tl.eventCallback("onComplete", () => gsap.to(hint, { opacity: 0.5, duration: 0.9 }));
document.body.addEventListener("click", () => gsap.set(hint, { opacity: 0 }));
window.introTimeline = tl;""")

    m_title = re.search(r"<title>.*?</title>", art, re.S)
    m_style = re.search(r"<style>.*?</style>", art, re.S)
    m_body = re.search(r"<body>(.*)</body>", art, re.S)
    (ROOT / "gsap" / f"{stem}_artifact.html").write_text(
        m_title.group(0) + "\n" + m_style.group(0) + m_body.group(1), encoding="utf-8")
    size = (ROOT / "gsap" / f"{stem}.html").stat().st_size / 1024
    print(f"WROTE gsap/{stem}.html ({size:.0f} KB) + _embed + _artifact")


emit("intro_fade", build(colored=False, lining_opacity=0.15))
emit("intro_fade_color", build(colored=True, lining_opacity=0.30))

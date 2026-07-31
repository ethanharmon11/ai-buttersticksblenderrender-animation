"""Composite the crisp BSG script onto the blank-ball flight clip.

- Renders the brand's bsg vector group once to a transparent sprite (Chrome).
- Rides it along reference/ball_track.json (smoothed; pre-strike pinned to
  the known start position; gaps = ball in hole = no lettering).
- Lettering stays upright (cartoon license) and always crisp.

Output: reference/flight_bsg.mp4
"""
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
RUST = "#B15023"
FPS = 30

# ---- 1. render the BSG sprite (transparent background) -------------------
G = json.loads((ROOT / "gsap" / "groups.json").read_text(encoding="utf-8"))
X0, Y0, X1, Y1 = 1611.4, 796.7, 1877.1, 960.9        # bsg bbox in badge coords
PAD = 8
W, H = X1 - X0 + 2 * PAD, Y1 - Y0 + 2 * PAD
paths = "\n".join(f'<path d="{p["d"]}" fill-rule="evenodd"/>' for p in G["bsg"])
sprite_html = ROOT / "gsap" / "bsg_sprite.html"
sprite_html.write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;background:transparent}}</style></head><body>
<svg width="1600" height="{1600 * H / W:.0f}" viewBox="{X0 - PAD} {Y0 - PAD} {W} {H}"
 xmlns="http://www.w3.org/2000/svg"><g fill="{RUST}">{paths}</g></svg>
</body></html>""", encoding="utf-8")
sprite_png = ROOT / "reference" / "bsg_sprite.png"
subprocess.run([CHROME, "--headless=new", f"--screenshot={sprite_png}",
                f"--window-size=1600,{int(1600 * H / W)}", "--hide-scrollbars",
                "--default-background-color=00000000",
                sprite_html.resolve().as_uri()], check=True, capture_output=True)
sprite = Image.open(sprite_png).convert("RGBA")
# soften edges a hair so it sits in the painted world
sprite = sprite.filter(ImageFilter.GaussianBlur(0.6))
SPR_AR = sprite.height / sprite.width
print(f"sprite {sprite.size}")

# ---- 2. load + condition the track ---------------------------------------
track = json.load(open(ROOT / "reference" / "ball_track.json"))
n = len(track)
xs = np.array([o["x"] if o["ok"] else np.nan for o in track], dtype=float)
ys = np.array([o["y"] if o["ok"] else np.nan for o in track], dtype=float)
rs = np.array([o["r"] if o["ok"] else np.nan for o in track], dtype=float)

# pre-strike: pin to the design position; strike window: hide the lettering
START = (640 * 1280 / 1920, 690 * 720 / 1080, 215 * 1280 / 1920)  # x, y, r
# airborne: ball clearly up in the sky as a small tracked circle
launch = n
for i in range(n):
    if not np.isnan(ys[i]) and ys[i] < START[1] - 150 and rs[i] < 90:
        launch = i
        break
# the club whip occupies the ~16 frames before liftoff
strike = max(0, launch - 16)
xs[:strike], ys[:strike], rs[:strike] = START
# alpha envelope: 1 at rest, 0 through the strike whip, ramp back in airborne
alpha = np.ones(n)
alpha[strike:launch] = 0.0
ramp = min(4, n - launch)
if ramp > 0:
    alpha[launch:launch + ramp] = np.linspace(0.35, 1.0, ramp)

# interpolate interior gaps; leave trailing gap (ball in hole) as NaN
def interp(a):
    idx = np.arange(n)
    good = ~np.isnan(a)
    last = int(np.nonzero(good)[0][-1])
    a[:last + 1] = np.interp(idx[:last + 1], idx[good], a[good])
    return a
xs, ys, rs = interp(xs), interp(ys), interp(rs)

# smooth (movavg 5) and widen detected radius to the ink outline
k = np.ones(5) / 5
def smooth(a):
    good = ~np.isnan(a)
    b = a.copy()
    b[good] = np.convolve(np.pad(a[good], 2, mode="edge"), k, mode="valid")
    return b
xs, ys = smooth(xs), smooth(ys)
rs = smooth(rs)
rs[launch:] *= 1.18

# ---- 3. composite ---------------------------------------------------------
tmp = Path(tempfile.mkdtemp())
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i",
                str(ROOT / "reference" / "flight_blank.mp4"),
                "-vf", f"fps={FPS}", str(tmp / "f%04d.png")], check=True)
frames = sorted(tmp.glob("f*.png"))
out_dir = Path(tempfile.mkdtemp())
rng = np.random.default_rng(7)
for i, f in enumerate(frames):
    im = Image.open(f).convert("RGBA")
    if i < len(xs) and not np.isnan(xs[i]) and rs[i] > 12 and alpha[i] > 0.01:
        w = max(int(2 * rs[i] * 0.78), 10)
        spr = sprite.resize((w, max(int(w * SPR_AR), 4)), Image.LANCZOS)
        # grain the lettering slightly so it lives on the film
        a = np.asarray(spr, dtype=np.float32)
        noise = rng.normal(0, 9, a.shape[:2])[..., None]
        a[..., :3] = np.clip(a[..., :3] + noise, 0, 255)
        a[..., 3] *= 0.94 * alpha[i]
        spr = Image.fromarray(a.astype(np.uint8))
        im.alpha_composite(spr, (int(xs[i] - spr.width / 2),
                                 int(ys[i] - spr.height / 2)))
    im.convert("RGB").save(out_dir / f.name)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                "-i", str(out_dir / "f%04d.png"),
                "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(ROOT / "reference" / "flight_bsg.mp4")], check=True)
print(f"strike f{strike} ({strike / FPS:.2f}s), launch f{launch} ({launch / FPS:.2f}s)")
print("wrote reference/flight_bsg.mp4")

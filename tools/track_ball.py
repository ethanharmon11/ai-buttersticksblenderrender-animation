"""Track the cream golf ball through an AI-generated flight clip.

Finds the ball per frame as the roundest bright-cream blob, writes
reference/ball_track.json: [{f, t, x, y, r, ok}, ...] in source pixels.
The composite step rides the vector BSG ball along this path.

Usage: python tools/track_ball.py reference/flight_blank.mp4
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "reference" / "flight_blank.mp4"
FPS = 30

def frames(src):
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
                    "-vf", f"fps={FPS}", str(tmp / "f%04d.png")], check=True)
    return sorted(tmp.glob("f*.png"))

def find_ball(img):
    """All round bright-cream blobs as candidates [(score, x, y, r), ...]."""
    cands = []
    a = np.asarray(img.convert("RGB"), dtype=np.int16)
    r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
    # cream/white: bright, low saturation, warm
    bright = (r_ > 175) & (g_ > 165) & (b_ > 140)
    lowsat = (abs(r_ - g_) < 45) & (r_ - b_ < 90) & (r_ - b_ > -20)
    mask = bright & lowsat
    # connected components via simple flood label (scipy-free)
    from collections import deque
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    ys, xs = np.nonzero(mask)
    order = np.argsort(-(ys))  # any order
    for i in order[:: max(1, len(order) // 4000)]:
        y0, x0 = int(ys[i]), int(xs[i])
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        px = []
        while q:
            y, x = q.popleft()
            px.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if len(px) < 40:
            continue
        arr = np.array(px)
        cy, cx = arr[:, 0].mean(), arr[:, 1].mean()
        rr = np.sqrt(len(px) / np.pi)
        # roundness: fraction of pixels within fitted radius
        d = np.sqrt(((arr[:, 0] - cy) ** 2 + (arr[:, 1] - cx) ** 2))
        roundness = float((d < rr * 1.25).mean())
        spans = (np.ptp(arr[:, 0]) + 1, np.ptp(arr[:, 1]) + 1)
        span = max(spans)
        aspect = min(spans) / span
        score = roundness * aspect * min(len(px), 20000)
        if roundness > 0.72 and aspect > 0.55:
            cands.append((score, cx, cy, rr))
    return cands

def main():
    fr = frames(SRC)
    out = []
    # seed: ball position in the start frame (1920x1080 design -> source px)
    w0, h0 = Image.open(fr[0]).size
    pred = (640 * w0 / 1920, 690 * h0 / 1080)
    vel = (0.0, 0.0)
    prev = None
    for i, f in enumerate(fr):
        cands = find_ball(Image.open(f))
        x = y = r = None
        ok = False
        if cands:
            # nearest candidate to predicted position, distance-penalized score
            def keyf(c):
                d = ((c[1] - pred[0]) ** 2 + (c[2] - pred[1]) ** 2) ** 0.5
                return d - min(c[0] / 400.0, 120)
            best = min(cands, key=keyf)
            d = ((best[1] - pred[0]) ** 2 + (best[2] - pred[1]) ** 2) ** 0.5
            if d < 0.22 * w0:
                x, y, r = best[1], best[2], best[3]
                ok = True
                if prev is not None:
                    vel = (0.6 * (x - prev[0]) + 0.4 * vel[0],
                           0.6 * (y - prev[1]) + 0.4 * vel[1])
                prev = (x, y)
        pred = (prev[0] + vel[0], prev[1] + vel[1]) if prev else pred
        out.append({"f": i, "t": round(i / FPS, 3), "x": x, "y": y, "r": r, "ok": ok})
    (ROOT / "reference" / "ball_track.json").write_text(json.dumps(out), encoding="utf-8")
    good = sum(1 for o in out if o["ok"])
    print(f"tracked {good}/{len(out)} frames -> reference/ball_track.json")

if __name__ == "__main__":
    main()

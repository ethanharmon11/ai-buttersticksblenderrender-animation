"""Split the brand-sheet SVG into animatable groups for the GSAP build.

Classifies the 61 paths by quadrant (wordmark TL, badge BR) and by fill,
then writes gsap/groups.json: {group: [{d, fill, bbox}]} in page coords
(y already un-flipped to standard SVG y-down space).
"""
import json
import re
from pathlib import Path

from svgpathtools import parse_path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "vectors" / "bsg_badge.svg").read_text(encoding="utf-8")
OUT = ROOT / "gsap"
OUT.mkdir(exist_ok=True)

H = 1530.7088
W = 2551.1812

paths = re.findall(r'<path transform="matrix\(1,0,0,-1,0,[0-9.]+\)" d="([^"]+)"[^/]*?fill="(#[0-9a-f]{6})"', SRC)
print(f"paths found: {len(paths)}")


def flip(d):
    """Apply the y-flip into the path data itself so groups need no transform."""
    p = parse_path(d)
    q = p.scaled(1, -1).translated(complex(0, H))
    return q.d()


items = []
for d, fill in paths:
    p = parse_path(d)
    x0, x1, y0, y1 = p.bbox()
    # flipped page coords (y-down)
    fy0, fy1 = H - y1, H - y0
    items.append({
        "d": flip(d), "fill": fill,
        "bbox": [round(x0, 1), round(fy0, 1), round(x1, 1), round(fy1, 1)],
    })

badge = [it for it in items if it["bbox"][0] > W / 2 and it["bbox"][1] > H * 0.35]
wordmark = [it for it in items if it["bbox"][2] < W / 2 and it["bbox"][3] < H * 0.55]
print(f"badge: {len(badge)}  wordmark: {len(wordmark)}")

groups = {"sil": [], "gold": [], "drips": [], "ball": [], "dimples_cream": [],
          "dimples_green": [], "tee": [], "bsg": [], "speed": []}
for it in badge:
    f = it["fill"]
    if f == "#21522a":
        groups["sil"].append(it)
    elif f == "#e9af34":
        groups["gold"].append(it)
    elif f == "#a66c1c":
        groups["drips"].append(it)
    elif f == "#f3e4c3":
        groups["ball"].append(it)
    elif f == "#f6e2c8":
        groups["dimples_cream"].append(it)
    elif f == "#244e29":
        groups["dimples_green"].append(it)
    elif f in ("#b9511f", "#b65125"):
        groups["tee"].append(it)
    elif f == "#b15023":
        groups["bsg"].append(it)
    elif f == "#1d5021":
        groups["speed"].append(it)
    else:
        print("UNCLASSIFIED badge fill:", f, it["bbox"])

# Wordmark: sort into Butter / Sticks / G,O,L,F by bbox
wm = sorted(wordmark, key=lambda i: (i["bbox"][1], i["bbox"][0]))
big = [i for i in wm if (i["bbox"][2] - i["bbox"][0]) > 200]
small = sorted([i for i in wm if (i["bbox"][2] - i["bbox"][0]) <= 200],
               key=lambda i: i["bbox"][0])
mid_y = (min(i["bbox"][1] for i in big) + max(i["bbox"][3] for i in big)) / 2
groups["wm_butter"] = [i for i in big if i["bbox"][3] < mid_y + 80]
groups["wm_sticks"] = [i for i in big if i["bbox"][3] >= mid_y + 80]
groups["wm_golf"] = small

for k, v in groups.items():
    print(k, len(v), "bbox:" if v else "", [
        min(i["bbox"][0] for i in v),
        min(i["bbox"][1] for i in v),
        max(i["bbox"][2] for i in v),
        max(i["bbox"][3] for i in v),
    ] if v else "")

(OUT / "groups.json").write_text(json.dumps(groups), encoding="utf-8")
print("WROTE", OUT / "groups.json")

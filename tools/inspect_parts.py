"""Dump per-object geometry + color data from the saved scene as JSON,
so the animation script can target badge sub-parts (pat, drips, ball, tee...).

Run:  blender --background butter_sticks_intro.blend --python tools/inspect_parts.py
"""
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
out = {}

for coll_name in ("badge", "wordmark"):
    coll = bpy.data.collections.get(coll_name)
    items = []
    for o in coll.objects:
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        mat = o.material_slots[0].material if o.material_slots else None
        color = None
        if mat and mat.node_tree:
            for n in mat.node_tree.nodes:
                if n.type == "EMISSION":
                    c = n.inputs["Color"].default_value
                    color = [round(v, 4) for v in (c[0], c[1], c[2])]
        items.append({
            "name": o.name,
            "x0": round(min(xs), 5), "x1": round(max(xs), 5),
            "y0": round(min(ys), 5), "y1": round(max(ys), 5),
            "z": round(o.location.z, 5),
            "splines": len(o.data.splines),
            "color": color,
            "mat": mat.name if mat else None,
        })
    items.sort(key=lambda d: d["z"])
    out[coll_name] = items

print("PARTS_JSON_BEGIN")
print(json.dumps(out, indent=1))
print("PARTS_JSON_END")

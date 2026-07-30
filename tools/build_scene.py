"""Build the Butter Sticks intro scene in Blender (headless).

Imports the brand-sheet SVG, splits logos into collections by page position,
applies flat emission materials, sets up an ortho camera, and renders a
style frame of the final lockup (script + BSG badge on medium brown).

Run:  blender --background --python tools/build_scene.py
"""
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "vectors" / "bsg_badge.svg"  # full brand sheet (all 3 PDFs identical)
RENDERS = ROOT / "renders"
RENDERS.mkdir(exist_ok=True)

# Brand palette (sRGB hex)
CREAM = "EADDC1"
DARK_BROWN = "4B311A"
MEDIUM_BROWN = "8C5E2E"
GOLDEN = "D9B64E"


def srgb_hex_to_linear(hex_str):
    def conv(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r = conv(int(hex_str[0:2], 16))
    g = conv(int(hex_str[2:4], 16))
    b = conv(int(hex_str[4:6], 16))
    return (r, g, b, 1.0)


def flat_material(name, rgba):
    """Shadeless flat-color material via emission."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba
    em.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


# ---------------------------------------------------------------- fresh scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ------------------------------------------------------------------ import svg
before = set(bpy.data.objects)
bpy.ops.import_curve.svg(filepath=str(SVG))
imported = [o for o in bpy.data.objects if o not in before and o.type == "CURVE"]
print(f"Imported {len(imported)} curve objects")

# The SVG importer parents everything into one collection scaled tiny.
# Compute overall bounds to classify by quadrant.
def obj_center(o):
    xs, ys = [], []
    for corner in o.bound_box:
        world = o.matrix_world @ bpy.mathutils_vector(corner) if False else None
    # bound_box is local; combine with matrix_world manually
    from mathutils import Vector
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(xs), min(ys), max(xs), max(ys))


all_bounds = [obj_center(o) for o in imported]
min_x = min(b[2][0] for b in all_bounds)
max_x = max(b[2][2] for b in all_bounds)
min_y = min(b[2][1] for b in all_bounds)
max_y = max(b[2][3] for b in all_bounds)
mid_x = (min_x + max_x) / 2
mid_y = (min_y + max_y) / 2
print(f"Sheet bounds: x[{min_x:.4f},{max_x:.4f}] y[{min_y:.4f},{max_y:.4f}]")

groups = {"wordmark": [], "ap1": [], "forged": [], "badge": []}
for o, (cx, cy, _) in zip(imported, all_bounds):
    if cx < mid_x and cy > mid_y:
        groups["wordmark"].append(o)
    elif cx >= mid_x and cy > mid_y:
        groups["ap1"].append(o)
    elif cx < mid_x and cy <= mid_y:
        groups["forged"].append(o)
    else:
        groups["badge"].append(o)
for k, v in groups.items():
    print(f"group {k}: {len(v)} objects")

# Drop AP1 / FORGED — not needed for the intro
for o in groups["ap1"] + groups["forged"]:
    bpy.data.objects.remove(o, do_unlink=True)

# ------------------------------------------------- collections + z stacking
for name in ("wordmark", "badge"):
    coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)
    for i, o in enumerate(groups[name]):
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
        o.location.z = i * 0.0005  # painter's order, avoid z-fighting

# ------------------------------------------------------------- recolor marks
# Wordmark becomes cream (it sits on the brown flood at the end).
cream_mat = flat_material("wordmark_cream", srgb_hex_to_linear(CREAM))
for o in groups["wordmark"]:
    o.data.materials.clear()
    o.data.materials.append(cream_mat)

# Badge: convert each imported SVG material to an equivalent flat emission.
seen = {}
for o in groups["badge"]:
    for slot in o.material_slots:
        src = slot.material
        if src is None:
            continue
        if src.name not in seen:
            # SVG importer stores fill in diffuse_color (sRGB-ish already linear in Blender)
            col = tuple(src.diffuse_color)
            seen[src.name] = flat_material(f"flat_{src.name}", col)
        slot.material = seen[src.name]

# --------------------------------------------------------- layout the lockup
from mathutils import Vector


def group_bbox(objs):
    bpy.context.view_layer.update()  # flush pending location edits into matrix_world
    xs, ys = [], []
    for o in objs:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            xs.append(p.x)
            ys.append(p.y)
    return min(xs), min(ys), max(xs), max(ys)


def move_group(objs, dx, dy):
    for o in objs:
        o.location.x += dx
        o.location.y += dy


def scale_group(objs, pivot, s):
    for o in objs:
        o.location.x = pivot[0] + (o.location.x - pivot[0]) * s
        o.location.y = pivot[1] + (o.location.y - pivot[1]) * s
        o.scale *= s


# Normalize: badge centered above, wordmark below, combined centered at origin.
bx0, by0, bx1, by1 = group_bbox(groups["badge"])
wx0, wy0, wx1, wy1 = group_bbox(groups["wordmark"])
badge_w, badge_h = bx1 - bx0, by1 - by0
word_w, word_h = wx1 - wx0, wy1 - wy0

# Badge slightly taller than the wordmark block for visual balance
target_badge_h = word_h * 1.3
s = target_badge_h / badge_h
scale_group(groups["badge"], ((bx0 + bx1) / 2, (by0 + by1) / 2), s)
bx0, by0, bx1, by1 = group_bbox(groups["badge"])
badge_w, badge_h = bx1 - bx0, by1 - by0

gap = word_h * 0.18
# badge center → (0, (gap+badge_h)/2 + word_h/2 ... simpler: stack
move_group(groups["badge"], -(bx0 + bx1) / 2, -by0 + gap / 2)
move_group(groups["wordmark"], -(wx0 + wx1) / 2, -wy1 - gap / 2)

# Recenter combined vertically
ax0, ay0, ax1, ay1 = group_bbox(groups["badge"] + groups["wordmark"])
move_group(groups["badge"] + groups["wordmark"], 0, -(ay0 + ay1) / 2)
ax0, ay0, ax1, ay1 = group_bbox(groups["badge"] + groups["wordmark"])
total_h = ay1 - ay0
total_w = ax1 - ax0
print(f"Lockup size: {total_w:.4f} x {total_h:.4f}")

# ------------------------------------------------------------------ backdrop
brown_mat = flat_material("bg_brown", srgb_hex_to_linear(MEDIUM_BROWN))
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.01))
bg = bpy.context.active_object
bg.name = "backdrop"
bg.scale = (total_w * 6, total_w * 6, 1)
bg.data.materials.append(brown_mat)

# -------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = (total_h / 0.55) * (1920 / 1080)  # lockup ≈55% of frame height
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
cam.location = (0, 0, 5)
scene.camera = cam

# -------------------------------------------------------------------- render
scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "RenderSettings") and any(
    e.identifier == "BLENDER_EEVEE_NEXT" for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
) else "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"  # exact hex colors, no filmic
scene.render.filepath = str(RENDERS / "style_frame.png")
bpy.ops.render.render(write_still=True)
print("RENDER DONE:", scene.render.filepath)

# Save the .blend for iteration
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "butter_sticks_intro.blend"))
print("SAVED BLEND")

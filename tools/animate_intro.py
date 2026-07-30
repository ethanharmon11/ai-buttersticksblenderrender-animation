"""Animate the Butter Sticks intro (7s @ 30fps) on top of the built scene.

v4 "filling the glass":
- THIN syrupy streams pour off the butter pat (not fat lobes)
- A two-layer golden pond (front + darker phase-shifted back) fills the
  bottom of frame like a glass, surface lapping via scrolling noise
- The brown inversion arrives as a RISING WAVE that floods the frame
- Anticipation squash before the melt; jelly settle after the flood
- GOLF letters stay hidden until their own entrance (no ghosting)

Run:  blender --background butter_sticks_intro.blend --python tools/animate_intro.py
Saves butter_sticks_intro_anim.blend and renders probe frames.
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
RENDERS = ROOT / "renders" / "probes"
RENDERS.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
FPS = 30
END = 210
scene.render.fps = FPS
scene.frame_start = 1
scene.frame_end = END


def lin_hex(h):
    def conv(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (conv(int(h[0:2], 16)), conv(int(h[2:4], 16)), conv(int(h[4:6], 16)), 1.0)


CREAM = lin_hex("EADDC1")
MEDIUM_BROWN = lin_hex("8C5E2E")
GOLDEN = lin_hex("D9B64E")
DEEP_GOLDEN = tuple(0.65 * GOLDEN[i] + 0.35 * MEDIUM_BROWN[i] for i in range(3)) + (1.0,)

badge = list(bpy.data.collections["badge"].objects)
word = list(bpy.data.collections["wordmark"].objects)

# Opening beats play on cream; the liquids provide the color story later.
backdrop = bpy.data.objects["backdrop"]
for n in backdrop.material_slots[0].material.node_tree.nodes:
    if n.type == "EMISSION":
        n.inputs["Color"].default_value = CREAM


def flat_material(name, rgba):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def emission_node(mat):
    for n in mat.node_tree.nodes:
        if n.type == "EMISSION":
            return n
    return None


def key_color(mat, frame, rgba):
    em = emission_node(mat)
    em.inputs["Color"].default_value = rgba
    em.inputs["Color"].keyframe_insert("default_value", frame=frame)


def key_loc(o, frame, x=None, y=None, z=None):
    if x is not None:
        o.location.x = x
    if y is not None:
        o.location.y = y
    if z is not None:
        o.location.z = z
    o.keyframe_insert("location", frame=frame)


def key_delta(o, frame, x=0.0, y=0.0):
    o.delta_location.x = x
    o.delta_location.y = y
    o.keyframe_insert("delta_location", frame=frame)


def key_scale(o, frame, sx, sy=None, sz=1.0):
    sy = sx if sy is None else sy
    o.scale = (sx, sy, sz)
    o.keyframe_insert("scale", frame=frame)


def key_hide(o, frame_show):
    o.hide_render = True
    o.keyframe_insert("hide_render", frame=1)
    o.hide_render = False
    o.keyframe_insert("hide_render", frame=int(frame_show))


def iter_fcurves(action):
    if hasattr(action, "fcurves"):  # legacy API (<=4.x)
        yield from action.fcurves
        return
    for layer in action.layers:      # slotted actions (5.0+)
        for strip in layer.strips:
            for bag in strip.channelbags:
                yield from bag.fcurves


def set_ease(o_or_mat, style="AUTO_CLAMPED"):
    ad = o_or_mat.animation_data
    if not ad or not ad.action:
        return
    for fc in iter_fcurves(ad.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = style
            kp.handle_right_type = style


# ===================== MELT THE ACTUAL VECTOR (v5) =========================
# The butter pat itself sags via a lattice shape key: gold pat + silhouette
# border + BSG script + speed lines convert to meshes and deform; the ball,
# dimples and tee stay rigid. All coords below are lockup-layout world coords.
by = {o.name: o for o in badge}
GOLD = by["Curve.022"]
SIL = by["Curve.021"]
LETTERS = [by[f"Curve.{n:03d}"] for n in (55, 56, 57, 58)]
SPEED = [by["Curve.059"], by["Curve.060"]]
BALL = by["Curve.023"]


def to_mesh(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target="MESH")


for o in [GOLD] + LETTERS + SPEED:
    to_mesh(o)

bpy.context.view_layer.objects.active = GOLD   # dense geometry -> smooth pour
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.subdivide(number_cuts=2)
bpy.ops.object.mode_set(mode="OBJECT")

# Re-stack painter z so molten gold flows OVER the ball art (it imported
# below the ball fill and would vanish behind it mid-melt otherwise).
ztab = {"Curve.021": 0.0, "Curve.023": 0.0004, "Curve.022": 0.008,
        "Curve.053": 0.0084, "Curve.054": 0.0086,
        "Curve.059": 0.0096, "Curve.060": 0.0098}
for i, n in enumerate(range(24, 32)):
    ztab[f"Curve.{n:03d}"] = 0.0008 + i * 0.0002
for i, n in enumerate(range(32, 53)):
    ztab[f"Curve.{n:03d}"] = 0.0026 + i * 0.0002
for i, n in enumerate(range(55, 59)):
    ztab[f"Curve.{n:03d}"] = 0.0088 + i * 0.0002
for n, z in ztab.items():
    if n in by:
        by[n].location.z = z

# Cream patch behind the ball's drip cutouts, so the gold sliding away
# reveals clean ball instead of the dark silhouette base.
bx0, by0_, bx1, by1_ = BALL.bound_box[0], None, None, None
b_lo = [min((BALL.matrix_world @ Vector(c))[i] for c in BALL.bound_box) for i in range(2)]
b_hi = [max((BALL.matrix_world @ Vector(c))[i] for c in BALL.bound_box) for i in range(2)]
cx, r = (b_lo[0] + b_hi[0]) / 2, (b_hi[0] - b_lo[0]) / 2
cy = b_hi[1] - r
clip_y = cy + 0.18 * r   # only the upper cap, where the drip cutouts live
pverts, steps = [], 40
t0, t1 = math.asin(max(-1, (clip_y - cy) / r)), math.pi - math.asin(max(-1, (clip_y - cy) / r))
for i in range(steps + 1):
    t = t0 + (t1 - t0) * i / steps
    pverts.append((cx + r * 0.94 * math.cos(t), cy + r * 0.94 * math.sin(t), 0))
patch_mesh = bpy.data.meshes.new("ball_patch")
patch_mesh.from_pydata(pverts, [], [list(range(len(pverts)))])
patch_mesh.update()
patch = bpy.data.objects.new("ball_patch", patch_mesh)
scene.collection.objects.link(patch)
patch.location = (0, 0, 0.0002)
patch.data.materials.append(BALL.material_slots[0].material)
badge.append(patch)

# Cream fill in the pat's exact shape: as the gold drains away it reveals
# an "emptied" butter mold inside the static green outline.
pat_patch = GOLD.copy()                    # full object copy: keeps scale/loc
pat_patch.data = GOLD.data.copy()
pat_patch.name = "pat_patch"
scene.collection.objects.link(pat_patch)
pat_patch.location.z = 0.0003
pat_patch.data.materials.clear()
pat_patch.data.materials.append(BALL.material_slots[0].material)
badge.append(pat_patch)

# The melt lattice: 8 columns x 6 rows over the pat region.
lat_data = bpy.data.lattices.new("melt_lat")
lat_data.points_u, lat_data.points_v, lat_data.points_w = 8, 6, 1
lat = bpy.data.objects.new("melt_lat", lat_data)
scene.collection.objects.link(lat)
lat.location = (cx, 0.115, 0.02)
lat.scale = (0.17, 0.14, 1.0)
lat.shape_key_add(name="Basis")
melt_key = lat.shape_key_add(name="Melted", from_mix=False)
colf = [1.0, 1.0, 0.55, 0.95, 0.5, 0.9, 0.9, 0.9]   # per-column drippiness
rowf = [1.0, 0.92, 0.8, 0.68, 0.56, 0.45]           # DRAIN: even the top edge pours down
for v in range(6):
    for u in range(8):
        idx = v * 8 + u
        base = melt_key.data[idx].co.copy()
        down_world = (0.035 + 0.085 * colf[u]) * rowf[v]
        melt_key.data[idx].co = (base.x, base.y - down_world / 0.14, base.z)

melt_key.value = 0.0
melt_key.keyframe_insert("value", frame=46)
melt_key.value = 1.0
melt_key.keyframe_insert("value", frame=104)


# The silhouette stays completely static (the empty mold). Gold, letters and
# speed lines pour: full lattice influence, no vertex groups needed.
for o in [GOLD] + LETTERS + SPEED:
    mod = o.modifiers.new("melt", "LATTICE")
    mod.object = lat

# ---------------------------------------------------------------- badge root
bb_min = Vector((min(min(v.x for v in (o.matrix_world @ Vector(c) for c in o.bound_box)) for o in badge),
                 min(min(v.y for v in (o.matrix_world @ Vector(c) for c in o.bound_box)) for o in badge), 0))
bb_max = Vector((max(max(v.x for v in (o.matrix_world @ Vector(c) for c in o.bound_box)) for o in badge),
                 max(max(v.y for v in (o.matrix_world @ Vector(c) for c in o.bound_box)) for o in badge), 0))
badge_center = (bb_min + bb_max) / 2
print(f"badge center: {badge_center.x:.4f},{badge_center.y:.4f}")

root = bpy.data.objects.new("badge_root", None)
scene.collection.objects.link(root)
root.location = badge_center
bpy.context.view_layer.update()
inv = root.matrix_world.inverted()
for o in badge + [lat]:   # lattice rides the badge so the melt tracks it
    o.parent = root
    o.matrix_parent_inverse = inv

# Root motion: badge starts screen-center, rises to lockup after the flood.
key_loc(root, 1, x=0.0, y=0.0, z=0.0)
key_loc(root, 130, x=0.0, y=0.0, z=0.0)
key_loc(root, 150, x=badge_center.x, y=badge_center.y, z=0.0)

# Scale beats: intro pop, anticipation soften, jelly squash, breathing idle.
key_scale(root, 1, 0.90)
key_scale(root, 20, 0.90)
key_scale(root, 32, 1.05)
key_scale(root, 44, 1.00)
key_scale(root, 45, 1.00)
key_scale(root, 51, 1.035, 0.95)   # butter softens as the melt starts
key_scale(root, 58, 1.00, 1.00)
key_scale(root, 128, 1.00)
key_scale(root, 134, 1.09, 0.84)
key_scale(root, 141, 0.95, 1.07)
key_scale(root, 148, 1.00, 1.00)
key_scale(root, 196, 1.00, 1.00)
key_scale(root, 203, 1.012, 1.012)
key_scale(root, 210, 1.00, 1.00)
set_ease(root)

# ------------------------------------------------------- badge color fade-in
muted = lambda c: tuple(0.30 * c[i] + 0.70 * CREAM[i] for i in range(3)) + (1.0,)
badge_mats = {s.material for o in badge for s in o.material_slots if s.material}
for mat in badge_mats:
    em = emission_node(mat)
    true_col = tuple(em.inputs["Color"].default_value)
    key_color(mat, 1, CREAM)          # invisible on cream bg
    key_color(mat, 22, muted(true_col))
    key_color(mat, 44, true_col)
    set_ease(mat.node_tree)

# --------------------------------------------------- liquid infrastructure
# One scrolling empty drives every Displace: noise flows DOWN and drifts
# sideways -> streams wiggle, pond laps, brown wave rolls.
flow = bpy.data.objects.new("flow_empty", None)
scene.collection.objects.link(flow)
flow.location = (0, 0, 0)
flow.keyframe_insert("location", frame=40)
flow.location = (-0.28, -1.8, 0)
flow.keyframe_insert("location", frame=170)
for fc in iter_fcurves(flow.animation_data.action):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"

tex = bpy.data.textures.new("flow_noise", "CLOUDS")
tex.noise_scale = 0.11
tex.noise_depth = 1


def add_ripple(o, strength, direction):
    disp = o.modifiers.new("ripple", "DISPLACE")
    disp.texture = tex
    disp.texture_coords = "OBJECT"
    disp.texture_coords_object = flow
    disp.mid_level = 0.5
    disp.direction = direction
    disp.strength = strength


def grid_plane(name, width, height, cols, origin_y, z, mat, x_shift=0.0):
    """Horizontal grid strip anchored at origin (bottom edge), rising in +Y."""
    verts = [(-width / 2 + width * i / cols + x_shift, y, 0)
             for y in (0.0, height) for i in range(cols + 1)]
    faces = [(i, i + 1, cols + 2 + i, cols + 1 + i) for i in range(cols)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(o)
    o.location = (0, origin_y, z)
    o.data.materials.append(mat)
    return o


# ------------------------------------------- thin syrup streams off the pat
def make_stream(name, width, length, x, top_y, z):
    """Thin gridded stream, origin top-center, rounded tip, hangs in -Y."""
    r = width / 2
    cap, body = 5, 40
    rows = []
    for i in range(cap):                          # rounded top
        t = math.pi / 2 * (1 - i / cap)
        rows.append((-r + r * math.sin(t), max(r * math.cos(t), 0.15 * r)))
    for i in range(body + 1):                     # long thin body
        rows.append((-r - (length - 2 * r) * i / body, r))
    for i in range(1, cap + 1):                   # rounded falling tip
        t = math.pi / 2 * i / cap
        rows.append((-(length - r) - r * math.sin(t), max(r * math.cos(t), 0.15 * r)))
    verts = [(s * hw, y, 0) for (y, hw) in rows for s in (-1, 1)]
    faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(rows) - 1)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(o)
    o.location = (x, top_y, z)
    return o


golden_mat = flat_material("butter_gold", GOLDEN)

# No separate streams in v5: the melted vector's own drip tips sag low and
# the rising pond climbs up to swallow them — the connection is the story.

# --------------------------------------- the pond: two-layer lapping waves
pond_back = grid_plane("pond_back", 1.6, 0.75, 48, -0.36, -0.0045,
                       flat_material("butter_deep", DEEP_GOLDEN), x_shift=0.055)
pond_front = grid_plane("pond_front", 1.6, 0.75, 48, -0.36, -0.003, golden_mat)
# Displace runs before object scale, so compensate for the ~0.45 Y-squash
add_ripple(pond_back, 0.065, "Y")
add_ripple(pond_front, 0.052, "Y")

# Fill like a glass: back layer peeks slightly above the front (depth cue).
key_scale(pond_back, 58, 1.0, 0.0001)
key_scale(pond_back, 100, 1.0, 0.467)    # level ~ -0.01
key_scale(pond_front, 62, 1.0, 0.0001)
key_scale(pond_front, 102, 1.0, 0.440)   # level ~ -0.03
set_ease(pond_back)
set_ease(pond_front)

# --------------------------------- the brown wave: inversion as liquid rise
brown_wave = grid_plane("brown_wave", 1.6, 0.75, 48, -0.36, -0.002,
                        flat_material("brown_liquid", MEDIUM_BROWN))
add_ripple(brown_wave, 0.050, "Y")
key_scale(brown_wave, 112, 1.0, 0.0001)
key_scale(brown_wave, 130, 1.0, 1.06)    # crests past frame top -> full brown
set_ease(brown_wave)

# ------------------------------------------------------------- wordmark anim
by_name = {o.name: o for o in word}
butter = [by_name["Curve.003"], by_name["Curve.005"]]
sticks = [by_name["Curve.004"], by_name["Curve.006"]]
golf = [by_name["Curve.007"], by_name["Curve.008"], by_name["Curve.010"], by_name["Curve.009"]]  # G O L F by x

golf_mat = flat_material("golf_cream", CREAM)
for o in golf:
    o.data.materials.clear()
    o.data.materials.append(golf_mat)

word_mat = by_name["Curve.003"].material_slots[0].material

for o in butter + sticks:
    key_hide(o, 150)
for o in golf:
    key_hide(o, 172)   # hidden until its own entrance (occlusion-ghost fix)

RISE = 0.055
for i, piece_group in enumerate((butter, sticks)):
    f0 = 150 + i * 8
    for o in piece_group:
        key_delta(o, f0, 0, -RISE)
        key_delta(o, f0 + 15, 0, 0)
        set_ease(o)

for i, o in enumerate(golf):
    f0 = 174 + i * 4
    cx = (o.bound_box[0][0] + o.bound_box[6][0]) / 2 + o.location.x
    key_delta(o, f0, -cx * 0.5, -0.02)
    key_delta(o, f0 + 10, 0, 0)
    set_ease(o)

key_color(word_mat, 148, MEDIUM_BROWN)
key_color(word_mat, 168, CREAM)
set_ease(word_mat.node_tree)
key_color(golf_mat, 172, MEDIUM_BROWN)
key_color(golf_mat, 192, CREAM)
set_ease(golf_mat.node_tree)

# ------------------------------------------------------------- camera push
cam = scene.camera
base = cam.data.ortho_scale
cam.data.ortho_scale = base * 1.10
cam.data.keyframe_insert("ortho_scale", frame=1)
cam.data.ortho_scale = base
cam.data.keyframe_insert("ortho_scale", frame=END)

# ---------------------------------------------------------------- save+probe
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "butter_sticks_intro_anim.blend"))
print("SAVED ANIM BLEND")

for f in (44, 60, 72, 84, 96, 104, 120, 134, 200):
    scene.frame_set(f)
    scene.render.filepath = str(RENDERS / f"probe_{f:03d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"PROBE {f} DONE")

"""Round 3: make the butter river flow. Run inside Blender (live or headless).

- Subdivide + displace every drip strip with a scrolling Clouds texture so
  the edges undulate and the ripple pattern flows DOWNWARD like liquid.
- Same treatment on the pool's rising surface (Y direction).
- Anticipation: badge does a tiny 'butter softening' squash as the melt begins.
Idempotent: safe to re-run (clears its own modifiers/keys first).
"""
import bpy

scene = bpy.context.scene


def get_fcurves_compat(action):
    if hasattr(action, 'fcurves'):
        return list(action.fcurves)
    fcurves = []
    for layer in action.layers:
        for strip in layer.strips:
            if hasattr(strip, 'channelbags'):
                for cb in strip.channelbags:
                    fcurves.extend(cb.fcurves)
    return fcurves


# ---------------------------------------------------- scrolling flow empty
flow = bpy.data.objects.get('flow_empty')
if flow is None:
    flow = bpy.data.objects.new('flow_empty', None)
    scene.collection.objects.link(flow)
flow.animation_data_clear()
flow.location = (0, 0, 0)
flow.keyframe_insert('location', frame=40)
flow.location = (0, -1.8, 0)          # noise scrolls down through the melt+flood
flow.keyframe_insert('location', frame=150)
for fc in get_fcurves_compat(flow.animation_data.action):
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR'   # constant flow speed (mechanical scroll)

tex = bpy.data.textures.get('flow_noise')
if tex is None:
    tex = bpy.data.textures.new('flow_noise', 'CLOUDS')
tex.noise_scale = 0.11                # ripple wavelength
tex.noise_depth = 1

# ------------------------------------------- undulating edges on the river
drips = [o for o in scene.objects if o.name.startswith('drip_')]
pool = bpy.data.objects['butter_pool']

for o in drips + [pool]:
    for m in list(o.modifiers):
        o.modifiers.remove(m)
    # meshes are pre-gridded by animate_intro.py — displace directly, no subsurf
    disp = o.modifiers.new('ripple', 'DISPLACE')
    disp.texture = tex
    disp.texture_coords = 'OBJECT'
    disp.texture_coords_object = flow
    disp.mid_level = 0.5
    if o is pool:
        disp.direction = 'Y'          # pool surface sloshes vertically
        disp.strength = 0.022
    else:
        disp.direction = 'X'          # drip edges wobble sideways
        disp.strength = 0.020

# ------------------------------- anticipation: butter softens before melt
root = bpy.data.objects['badge_root']
# nudge keys between the saturate-pop (f44) and the jelly squash (f118)
root.scale = (1.0, 1.0, 1.0)
root.keyframe_insert('scale', frame=45)
root.scale = (1.035, 0.95, 1.0)       # soften/settle as the melt starts
root.keyframe_insert('scale', frame=51)
root.scale = (1.0, 1.0, 1.0)
root.keyframe_insert('scale', frame=58)

if bpy.app.background:
    bpy.ops.wm.save_mainfile()
print(f"RIVER ORGANICS OK  drips={len(drips)}  pool=1  anticipation=on")

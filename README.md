# Butter Sticks Golf — Website Intro Animation

A 7-second flat-2D logo animation for the Butter Sticks Golf website opening,
built entirely in **Blender 5.0** and driven by reproducible Python scripts.
The BSG badge's butter pat genuinely melts — the gold vector pours out of its
own outline, over the golf ball, into a rising two-layer butter pond, followed
by a brown "browned butter" tide inversion and a staggered wordmark reveal.

Inspired by a Saint Lukas Art School logo animation (TikTok @mid.night182).

## Deliverables

- `renders/butter_sticks_intro.webm` — the site-embed file (~165 KB)
- `renders/butter_sticks_intro.mp4` — review copy
- `butter_sticks_intro_anim.blend` — the fully animated scene

## Pipeline (all reproducible)

| Script | Purpose |
|---|---|
| `tools/extract_svg.py` | Brand-sheet PDF → SVG via PyMuPDF (`uv run --with pymupdf`) |
| `tools/build_scene.py` | Import SVG curves, split logos, flat emission materials, ortho camera, style frame |
| `tools/animate_intro.py` | The whole 210-frame choreography: lattice/shape-key vector melt, drip columns, two-layer pond with scrolling-noise waves, brown tide, jelly squash, type reveal |
| `tools/blender_client.py` | Direct socket client for the blender-mcp addon (drive a live Blender GUI on localhost:9876) |
| `tools/pdf_preview.py` | Render source PDFs to PNG for inspection |

Rebuild + render from scratch:

```powershell
blender --background butter_sticks_intro.blend --python tools/animate_intro.py
blender --background butter_sticks_intro_anim.blend -o "//renders/frames/f_####" -F PNG -x 1 -a
ffmpeg -framerate 30 -i renders/frames/f_%04d.png -c:v libvpx-vp9 -b:v 0 -crf 32 -pix_fmt yuv420p renders/butter_sticks_intro.webm
```

## Key techniques

- **Vector melt**: badge curves converted to meshes, caged in an 8×6 lattice
  with a "Melted" shape key — per-column drippiness, top edge drains, static
  silhouette left behind as an emptied butter mold (cream fill revealed).
- **Liquid surfaces**: gridded planes displaced by a Clouds texture whose
  coordinate object scrolls down-frame — waves that visibly *flow*.
- **Flat-2D look**: emission-only materials at exact brand hexes
  (cream `#EADDC1`, medium brown `#8C5E2E`, golden `#D9B64E`), Standard view
  transform, orthographic camera with a slow 10% push.
- Blender 5.x note: layered-action API (`action.layers[].strips[].channelbags[]`)
  — see `iter_fcurves` in `tools/animate_intro.py`.

`.claude/skills/` contains 11 community Blender skills (kevinbadi/blender-skills,
RobLe3/cc-blender-skill, ra100/blender-claude-plugin), security-vetted before
install. `blender_mcp_addon.py` is the vetted blender-mcp addon (ahujasid).

Brand assets are **not** in this repo — they live in the Butter Sticks OneDrive
(`Merchandise Designs/Logo Assets`); `vectors/` holds the extracted SVGs.

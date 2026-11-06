# Woodland environment art pass

This pass keeps the authored trees, cottage, landmark positions and clue entity names. It replaces the rectangular road tiles with continuous gravel ribbons, adds a shallow woodland ground mesh, and scatters low bracken and stones outside the walking line. Ground relief feathers to zero around paths and landmarks so existing steps, paw prints and tree roots remain at their authored grade.

The bunkers retain the original first-person interior envelope and 1.8 m doorway. Their new mesh adds softened concrete edges, formwork texture, damp stains, retaining wings, ventilation louvers, door jambs and hardware. The existing open steel doors, notice planes and interior clues stay separate. The ground and bunker shells carry physics; gravel and bracken are decorative. The new mound keeps the original open-front pivot; its broader, flatter crown covers the rear roof corners.

The hound has a continuous body mesh, posed limbs, closed eyes, folded ears, tail and leather collar. The loose collars have leather straps, stitching, buckles, brass tags and a break matching the story's “chewed through” description. The named `Document: collar` entity keeps its original pointer collider and pickup behavior; the dog keeps `Forest: dead dog` for its disappearance beat.

## Rebuilding the assets

The source scripts write to `/tmp/mothman-art` before packaging into the scene. They require Python with Pillow/numpy and Blender 5.1 (Blender includes numpy). Run from the project root, with preview stopped while packaging asset files:

```sh
python3 scripts/build-environment-textures.py
MOTHMAN_ROOT="$PWD" /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python scripts/build-environment-art.py
python3 scripts/package-environment-art.py
```

Packaging extracts shared images from the Blender GLBs, deduplicates them, rewrites the GLBs to reference `assets/Images/woodland-v2/`, and adds a shared roughness/metalness atlas for leather versus metal. No geometry compression or runtime procedural shaders are used. Fine detail is merged by material to avoid separate renderers for every stitch or bolt.

Use a new asset version when revising models in a running preview, then update sources through Creator Hub MCP; cached GLBs may otherwise remain stale. Source scripts do not write the composite. The original `gen-forest.py` refuses to regenerate once `Environment:` entities exist, because rebuilding its greybox would orphan the detailed replacements and reset editor changes.

## Placement audit

The scene is 192 × 192 m (144 parcels). Ground and track meshes use unit scale at (96, 0, 96). Bunker shells use unit scale at their existing bunker roots; the shared mound retains scale (7, 4.6, 14) at local (0, 0, -4.5). Collars use unit scale at their original positions. The dog uses scale 0.85 at its original position and yaw.

Detailed measured bounds and validation results are recorded in `environment-art-audit.json`. Blender studies are modeling previews, not evidence of the final scene lighting.

## Second refinement pass

The v3 pass replaces the overlapping path ribbons with a single sampled road network. Vertex alpha feathers only the outside perimeter; continuous world-space UVs and junction-aware rut shading remove the dark transverse borders at forks. The exported `COLOR_1` is explicitly promoted to `COLOR_0` during packaging so the intended fade reaches glTF consumers.

The hound now has joined limb anatomy, a tucked flank, slender muzzle, soft folded ears, individual toes and claws, nostrils, closed eyelids, a leather collar and brass tag. Its two-material mesh uses textured fur and a normal map. The existing named clue and disappearance behavior are preserved. The experimental v3 bark and trunk-normal changes were reverted at the owner’s request. All trees use their original catalog GLBs, including the original pale bark, leaf materials and trunk shading. Tree transforms and colliders remain unchanged.

The four cottage panes now use spatially varying grime opacity (roughly 60–90%), a new normal map, and roughness 0.64. This masks detail and catches the flashlight; it does not implement screen-space refraction or blur. The bunker receives damp concrete normal detail, and its earth crown now closes around the front retaining wall instead of leaving a gap above the coping.

Furniture is downloaded catalog content, not newly modeled:

| Item | Source | Placement calibration |
|---|---|---|
| Worn wooden table | OpenDCL `oldtable`, `bafybeignuppqx6zr27xcxnanl6uz4aipqkxfadzmdjyldhmymzz3uwa5iq` | Native bounds approximately 4.525 × 1.350 × 2.686 m; scale (0.376, 0.578, 0.391), top at 0.98 m for the existing radio and statement |
| Iron single bed | Creator Hub `ee8d07e1-c954-458c-b00f-3e3a84712710` | Native bounds 1.294 × 1.005 × 2.677 m; scale 0.78, offset for its corner pivot |
| Four window cabinets | Creator Hub Night Stand `aac5d038-f510-4594-acb6-10709cd827be` | Native bounds 1.521 × 1.666 × 1.063 m; individually fitted beneath existing windows |
| Existing barrel file restored | Creator Hub `76280eb2-09bc-4ed4-abba-b1f847dcdf3c` | Existing scene placement retained |

The table and catalog furniture use built-in colliders. The original invisible window-sill stops remain to prevent the flashlight origin passing through a pane when the player stands against it. The box cot visuals were removed. Existing furniture imports and their catalog metadata remain in `assets/asset-packs`.

Rebuild the v3 assets from the project root, with preview stopped:

```sh
python3 scripts/refine-art-textures.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/refine-environment-models.py
python3 scripts/package-refined-art.py
```

This uses headless Blender. Blender MCP is an optional route for future live, collaborative modeling; setup is described in `.claude/skills/add-3d-models/references/blender-authoring.md`. Creator Hub MCP was used for all scene entity/component mutations and autosave was checked throughout.

### Validation of the second pass

- `npm run build`: bundling and TypeScript checking passed.
- `git diff --check`: passed.
- 581 MCP mutations completed and were autosaved; catalog placement used MCP as well.
- Final bounds/hierarchy audit: 690 revised model placements within the 192 × 192 m scene; 1,084 tree and trunk-collider entities preserve their transforms and collision components. Referenced image files exist; new GLBs have no animation clips or required geometry compression.
- Loaded GLB instances total 708,855 triangles (primitive geometry is additional), against the scene's 1,440,000 triangle allowance. This is an asset audit, not a runtime performance measurement.
- Blender studies checked the hound, continuous road fork, tree bark, bunker earth-cover closure and cottage furniture fit.
- In-world validation remains pending: Creator Hub launched Explorer, but its MCP listener never started and UI inspection timed out. The test instance was closed. The exact flashlight response of the new glass and road alpha must still be assessed in a healthy Explorer session; no gameplay or lighting defaults were changed for this art pass.

### Tree art direction — owner correction

Preserve the original white/pale trunks: they are easier to see in the low-light scene and looked better than the v3 replacement. The brown trunk pass is rejected. Any future realism pass must start from the original pale bark and retain its brightness and color identity; do not substitute brown bark or reinterpret the palette. The requested immediate change is an exact restoration, not another texture redesign.

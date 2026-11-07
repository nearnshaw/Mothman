# Dog and pale bark refinement

The existing hound skin now has a narrower cheek, a tapered nasal bridge, a flatter jaw and a lower brow; its pendant ears lie closer to the head. The pose, collar, limbs, fur maps and scene placement are retained. This is a deformation of the existing continuous mesh, not additional overlapping primitives.

All three existing tree assets now use the approved pale pine bark artwork and retain their PBR material settings (roughness 0.9, metallic 0). Their bark color and normal maps now include fine fibres, pores and shallow irregular fissures. Average bark brightness changes by less than 1%; foliage and geometry are unchanged. The maps are 1024 × 1024.

Verified with headless Blender renders of the dog and the actual pine trunk under nearby lighting. Explorer is not connected, so the in-world appearance and flashlight response remain unverified. Reload the preview if cached assets remain visible. Live collaborative editing is also available through Blender MCP when connected.

Dog asset audit:
- Native DCL bounds: (-1.1018, 0.0116, -0.1938) to (1.1630, 0.3784, 0.6650) m.
- Native dimensions: 2.2648 × 0.3667 × 0.8588 m; existing bottom-relative pivot retained.
- Existing scale: 0.85; position: (67.3760, 0.0200, 48.6532); rotation unchanged.
- World bounds: (66.6316, 0.0299, 47.5277) to (68.4014, 0.3416, 49.4886), inside the scene's 192 × 192 m envelope.
- 21,916 triangles and 2 materials, unchanged. No animation, camera or light exported. Texture references resolve; existing shared maps retained externally. Packaged GLB: 516,012 bytes.

Authoring sources: `scripts/refine-hound-shape.py` creates a review GLB and still in `/tmp/mothman-detail`; `scripts/detail-pale-bark.py` updates only the six bark maps from tracked originals, avoiding cumulative passes. The dog review GLB embeds textures; externalize its maps before replacing the production GLB, as in the project's existing packaging workflow.

The initial external-texture coverage check did not establish the live result: the owner's screenshot still showed the old birch bar markings. Updating PNGs underneath unchanged GLB references was insufficient for the running renderer.

The follow-up exports two new models, `green_birch_tree-pale-bark-v4.glb` and `autumn_birch_tree-pale-bark-v4.glb`, embedding the approved color and normal maps. All 244 green and 96 autumn tree references are changed through Creator Hub MCP, with on-disk autosave verification. The 202 pine trees retain their already-approved asset. `gen-forest.py` uses the new references too.

Both new models were re-imported into Blender and compared to their sources: 728 triangles each, identical native geometry bounds and pivots, unchanged material roughness, foliage alpha masks and double-sided settings. Native Blender bounds are approximately (-2.995, -3.043, 0) to (2.995, 3.043, 13.388) m; the DCL dimensions are 5.990 × 13.388 × 6.086 m. Each entity retains its individually authored position, rotation and scale because the native geometry is identical. Embedded bark color/normal pixels match the approved PNGs exactly. Files are approximately 2.89 and 2.88 MB. Authoring recipe: `scripts/package-pale-trees.py`.

Live visual verification remains unavailable: Creator Hub's current renderer does not support the editor screenshot tool, and native-window capture timed out. The previous conclusion based solely on texture-file hashes was too strong.

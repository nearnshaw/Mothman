# Mothman concept alternatives

- 01-the-watcher.png — Gaunt forest stalker with long tapered wings.
- 02-the-duskmoth.png — Heavy animalistic moth with rounded patterned wings.
- 03-the-shrouded.png — Upright figure with draped wings and recessed face.
- 04-the-ironwing.png — Angular insect creature with broad faceted wings.

## GLB production guidance

Suggested targets for one creature, not platform limits or measured performance: 4,000–8,000 triangles, one opaque body/wing material, a shared 1024px texture atlas and an emissive eye mask. Actual performance needs verification in the complete scene.

Bake most illustrated fur clumps, antenna barbs, wing veins and plates into textures. Keep only a few large silhouette clumps as geometry. Use slightly thick opaque wings with visible backs, simple wing hinges, and a modest skeleton supporting idle, flap and glide. Avoid layered transparent fur and cloth simulation.

Feed one selected image to an image-to-3D generator. These are single-view concepts, not exact orthographic turnarounds: hidden backs and wing attachments need reconstruction. Check that arms overlapping wings in projection do not become fused geometry. Clean up topology, UVs and skin weights before animation. Keep the origin at the feet and use consistent real-world scale.

Before replacing the existing model, inspect triangle/material counts, textures, dimensions, animations and collision settings, then test it in Decentraland. No GLB has been generated or runtime-tested during this concept-art task.

Art/ is excluded from deployment in .dclignore. Exact prompts are saved in prompts.md; generation used the built-in image generation tool.

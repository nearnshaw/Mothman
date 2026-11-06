/**
 * Preview-only tuning knobs (src/debug.tsx draws the panel). Plain state with no imports so that environment.ts and
 * flashlight.ts can read it without a cycle. The defaults are the shipped values; `dirty` asks the owners to re-apply.
 */
export const tune = {
  sky: 1.4, // multiplier on the three sky colours: the visible sky and the ambient light together (the engine ties them)
  sun: 2.0, // the sun/moon directional light, in the Sun component's units (0 = none)
  fog: 0.4, // EnvironmentFog density
  beamAngle: 56, // flashlight outer cone, degrees (the inner cone keeps its 28/48 ratio)
  beam: 2.0, // multiplier on the flashlight intensity
  stars: 6, // Skybox stars brightness (engine default 4.62; the brighter sky needs more to show them)
  dirty: true
}

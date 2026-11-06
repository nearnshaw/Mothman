import { engine, Skybox, Sun, EnvironmentFog, SkyboxTime, CameraModeArea, CameraType, Transform, ColorGradient } from '@dcl/sdk/ecs'
import { Color4, Vector3 } from '@dcl/sdk/math'
import { tune } from './tune'

const constant = (color: Color4): ColorGradient => ({ keys: [{ time: 0, color }] })
const scaled = (c: Color4, k: number) => Color4.create(Math.min(1, c.r * k), Math.min(1, c.g * k), Math.min(1, c.b * k), 1)

// These are also the ambient light (sky-sun-fog.md): zenith -> sky, horizon -> equator, nadir -> ground. A trace of
// blue-grey: enough to guess that something moved against the trees with the lamp off, not enough to walk by.
const SKY = {
  zenith: Color4.create(0.1, 0.11, 0.2, 1),
  horizon: Color4.create(0.11, 0.115, 0.17, 1),
  nadir: Color4.create(0.06, 0.06, 0.07, 1)
}
// A faintly grey fog colour reads as night mist; pure black fog is invisible in a black scene.
const FOG = Color4.create(0.05, 0.055, 0.07, 1)

/**
 * Night in the TNT area. The sky, sun and fog overrides are desktop-only (mobile and Bevy keep their sky);
 * the fixed 1:30 am skybox time works everywhere and is the fallback darkness.
 */
export function setupNight() {
  SkyboxTime.createOrReplace(engine.RootEntity, { fixedTime: 5400 })
  applyEnvironment()
}

/** Writes the sky, sun and fog from the base night and the preview tuning knobs (src/tune.ts). */
export function applyEnvironment() {
  Skybox.createOrReplace(engine.RootEntity, {
    skyColors: {
      zenith: constant(scaled(SKY.zenith, tune.sky)),
      horizon: constant(scaled(SKY.horizon, tune.sky)),
      nadir: constant(scaled(SKY.nadir, tune.sky))
    },
    clouds: { opacity: 0 },
    stars: { brightness: tune.stars }
  })
  Sun.createOrReplace(engine.RootEntity, { intensity: tune.sun, visible: false })
  EnvironmentFog.createOrReplace(engine.RootEntity, { color: constant(FOG), density: tune.fog })
}

let fpArea: ReturnType<typeof engine.addEntity> | null = null

/** First person everywhere in the play space (resized once the real bounds are known). */
export function forceFirstPerson(w: number, d: number) {
  if (fpArea === null) {
    fpArea = engine.addEntity()
    Transform.create(fpArea, { position: Vector3.create(w / 2, 5, d / 2) })
    CameraModeArea.create(fpArea, { area: Vector3.create(w + 6, 16, d + 6), mode: CameraType.CT_FIRST_PERSON })
    return
  }
  Transform.getMutable(fpArea).position = Vector3.create(w / 2, 5, d / 2)
  CameraModeArea.getMutable(fpArea).area = Vector3.create(w + 6, 16, d + 6)
}

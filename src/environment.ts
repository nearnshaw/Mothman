import { engine, Skybox, Sun, EnvironmentFog, SkyboxTime, CameraModeArea, CameraType, Transform, ColorGradient } from '@dcl/sdk/ecs'
import { Color4, Vector3 } from '@dcl/sdk/math'

const constant = (color: Color4): ColorGradient => ({ keys: [{ time: 0, color }] })

/**
 * Night in the TNT area. The sky, sun and fog overrides are desktop-only (mobile and Bevy keep their sky);
 * the fixed 1:30 am skybox time works everywhere and is the fallback darkness.
 */
export function setupNight() {
  SkyboxTime.createOrReplace(engine.RootEntity, { fixedTime: 5400 })
  Skybox.createOrReplace(engine.RootEntity, {
    skyColors: {
      // These are also the ambient light (sky-sun-fog.md). A trace of blue-grey: enough to guess that something
      // moved against the trees with the lamp off, not enough to walk by.
      zenith: constant(Color4.create(0.1, 0.11, 0.2, 1)),
      horizon: constant(Color4.create(0.11, 0.115, 0.17, 1)),
      nadir: constant(Color4.create(0.06, 0.06, 0.07, 1))
    },
    clouds: { opacity: 0 },
    stars: { brightness: 0.5 }
  })
  Sun.createOrReplace(engine.RootEntity, { intensity: 0, visible: false })
  // A faintly grey fog colour reads as night mist; pure black fog is invisible in a black scene.
  EnvironmentFog.createOrReplace(engine.RootEntity, { color: constant(Color4.create(0.05, 0.055, 0.07, 1)), density: 0.06 })
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

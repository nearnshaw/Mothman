import { engine, Entity, Transform, LightSource, inputSystem, InputAction, PointerEventType, AudioSource, ParticleSystem, PBParticleSystem_BlendMode } from '@dcl/sdk/ecs'
import { Vector3, Color3, Color4, Quaternion } from '@dcl/sdk/math'
import { setLoop } from './audio'
import { showCaption, showHint } from './telepathy'
import { CAPTIONS, HINTS } from './script'

/**
 * The one tool the player has. Toggle with F. It has no battery: it only fails when he is close (the beam
 * stutters and the 1966 TV whine rises) or when he puts it out after the reveal. Both are made audible and captioned
 * so a failure never reads as a glitch.
 */
export const flashlight = {
  on: false,
  wantOn: false,
  litFor: 0, // seconds the beam has been on continuously
  litTotal: 0, // seconds on, over the whole session
  offFor: 0,
  flicker: 0, // seconds of flicker left (the Mothman is near)
  dying: 0, // seconds of whine-and-stutter before he puts it out
  dead: 0, // seconds the flashlight stays dead (punishment)
  toggles: 0,
  failures: 0, // times it was put out
  entity: 0 as Entity
}

const BASE_INTENSITY = 150000
const OUTER_ANGLE = 48
let clickEntity: Entity
let whine: Entity
let lastIntensity = -1
let lastActive: boolean | null = null
let clock = 0
let flickerExplained = false
let pendingDead = 0
let wasDead = false
let sparks: Entity
let sparkFor = 0

export function setupFlashlight() {
  const e = engine.addEntity()
  Transform.create(e, { parent: engine.CameraEntity, position: Vector3.create(0.15, -0.1, 0.55), rotation: Quaternion.Identity() })
  LightSource.create(e, {
    type: LightSource.Type.Spot({ innerAngle: 28, outerAngle: OUTER_ANGLE }),
    color: Color3.create(1, 0.95, 0.85),
    intensity: BASE_INTENSITY,
    range: 40,
    shadow: false, // the avatar's own head shadows the cone when the lamp sits at the camera
    active: false
  })
  flashlight.entity = e
  // Sparks out of the lamp head when he puts it out: a continuous emitter switched on for a third of a second.
  sparks = engine.addEntity()
  Transform.create(sparks, { parent: e, position: Vector3.create(0, 0, 0.08) })
  ParticleSystem.create(sparks, {
    active: false,
    rate: 260,
    lifetime: 0.55,
    maxParticles: 160,
    texture: { src: 'assets/images/spark.png' }, // a glowing point with a four-point flare, not a plain quad
    initialSize: { start: 0.025, end: 0.07 },
    sizeOverTime: { start: 1, end: 0.15 },
    initialColor: { start: Color4.create(1, 0.98, 0.8, 1), end: Color4.create(1, 0.7, 0.3, 1) },
    colorOverTime: { start: Color4.create(1, 0.95, 0.7, 1), end: Color4.create(1, 0.25, 0.03, 0) },
    initialVelocitySpeed: { start: 1.5, end: 5 },
    gravity: 0.6, // they arc and fall like real sparks
    limitVelocity: { speed: 3.5, dampen: 0.8 },
    blendMode: PBParticleSystem_BlendMode.PSB_ADD,
    shape: ParticleSystem.Shape.Cone({ angle: 40, radius: 0.03 })
  })

  clickEntity = engine.addEntity()
  Transform.create(clickEntity, { parent: engine.CameraEntity })
  AudioSource.create(clickEntity, { audioClipUrl: 'assets/audio/click.ogg', playing: false, volume: 0.5 })
  whine = engine.addEntity()
  Transform.create(whine, { parent: engine.CameraEntity })
  AudioSource.create(whine, { audioClipUrl: 'assets/audio/whine.ogg', playing: false, loop: true, volume: 0.45 })

  engine.addSystem(flashlightSystem)
}

/** He puts the light out: a second and a half of whine and stutter, then dead for `seconds`. */
export function failLight(seconds: number) {
  if (!flashlight.on || flashlight.dying > 0 || flashlight.dead > 0) return
  flashlight.dying = 1.5
  pendingDead = seconds
}

function flashlightSystem(dt: number) {
  clock += dt
  if (inputSystem.isTriggered(InputAction.IA_SECONDARY, PointerEventType.PET_DOWN)) {
    flashlight.wantOn = !flashlight.wantOn
    flashlight.toggles++
    AudioSource.playSound(clickEntity, 'assets/audio/click.ogg')
    if (flashlight.wantOn && flashlight.dead > 0) showCaption(CAPTIONS.deadClick, 0, 3)
  }
  if (flashlight.dying > 0) {
    flashlight.dying -= dt
    flashlight.flicker = Math.max(flashlight.flicker, 0.2)
    if (flashlight.dying <= 0) {
      flashlight.dead = pendingDead
      flashlight.failures++
      AudioSource.playSound(clickEntity, 'assets/audio/die.ogg')
      sparkFor = 0.35
      ParticleSystem.getMutable(sparks).active = true
      showCaption(flashlight.failures === 1 ? CAPTIONS.putOut : CAPTIONS.putOutAgain, 0.3, 4)
      if (flashlight.failures === 1) showHint(HINTS.comesBack, 3, 6)
    }
  }
  if (sparkFor > 0) {
    sparkFor -= dt
    if (sparkFor <= 0) ParticleSystem.getMutable(sparks).active = false
  }
  if (flashlight.dead > 0) {
    flashlight.dead -= dt
    wasDead = true
  } else if (wasDead) {
    wasDead = false
    if (flashlight.wantOn) AudioSource.playSound(clickEntity, 'assets/audio/click.ogg')
  }
  const on = flashlight.wantOn && flashlight.dead <= 0
  if (on !== flashlight.on) {
    flashlight.on = on
    if (on) flashlight.litFor = 0
    else flashlight.offFor = 0
  }
  if (on) {
    flashlight.litFor += dt
    flashlight.litTotal += dt
  } else flashlight.offFor += dt
  if (flashlight.flicker > 0) flashlight.flicker -= dt

  // Feedback for the stutter: the TV whine from the lore, and once, a line that says what it means.
  const stuttering = on && flashlight.flicker > 0
  setLoop(whine, stuttering)
  if (stuttering && !flickerExplained) {
    flickerExplained = true
    showCaption(CAPTIONS.stutter, 0.6, 5)
    showHint(HINTS.stutter, 6, 7)
  }

  // At most 3 dips per second (photosensitivity), never fully off while flickering.
  let intensity = BASE_INTENSITY
  if (stuttering) {
    const phase = Math.floor(clock * 3) % 2
    intensity = phase === 0 ? BASE_INTENSITY : BASE_INTENSITY * 0.3
  }
  if (on !== lastActive || intensity !== lastIntensity) {
    const light = LightSource.getMutable(flashlight.entity)
    light.active = on
    light.intensity = intensity
    lastActive = on
    lastIntensity = intensity
  }
}

/** Camera position and forward in scene space. */
export function cameraRay() {
  const cam = Transform.get(engine.CameraEntity)
  return { origin: cam.position, forward: Vector3.rotate(Vector3.Forward(), cam.rotation) }
}

/** Is this point inside the lit cone right now? */
export function beamHits(p: Vector3, maxDist = 22): boolean {
  if (!flashlight.on) return false
  const { origin, forward } = cameraRay()
  const to = Vector3.subtract(p, origin)
  const d = Vector3.length(to)
  if (d > maxDist || d < 0.01) return false
  const cos = Vector3.dot(forward, Vector3.scale(to, 1 / d))
  return cos > Math.cos(((OUTER_ANGLE / 2 + 4) * Math.PI) / 180)
}

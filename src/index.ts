import { engine, Transform, TextShape, Font, TextAlignMode, AudioSource, InputModifier, MeshRenderer, Material } from '@dcl/sdk/ecs'
import { Vector3, Color4, Quaternion } from '@dcl/sdk/math'
import { loadBounds, bounds, roostSpot } from './config'
import { setupNight, forceFirstPerson } from './environment'
import { setupFlashlight, beamHits, flashlight } from './flashlight'
import { setupAmbience, setLoop, frames } from './audio'
import { setupMoths } from './moths'
import { setupTelepathy, showCaption, showHint, hud } from './telepathy'
import { SIGN, OPENING, HINTS, CAPTIONS, OBJECTIVES, ENDINGS } from './script'
import { setupHud } from './hud'
import { setupDocuments } from './documents'
import { setupCabin, cabin } from './cabin'
import { objectiveClock, setObjective } from './objectives'
import { MothmanHost, story } from './npc/mothman/host'
import { layout } from './layout'

const SPAWN = Vector3.create(layout.spawn[0], 0, layout.spawn[1])

export function main() {
  loadBounds()
  setupNight()
  forceFirstPerson(bounds.w, bounds.d)
  setupFlashlight()
  setupAmbience()
  setupMoths()
  setupTelepathy()
  setupHud()
  setupDocuments()
  setupCabin()
  engine.addSystem(objectiveClock)
  // No jumping, double jump or gliding: the fence, the cabin roof and the bunker mounds stay what they look like.
  InputModifier.createOrReplace(engine.PlayerEntity, {
    mode: InputModifier.Mode.Standard({ disableJump: true, disableDoubleJump: true, disableGliding: true })
  })

  // Why you are here (GDD §11, the dog): Duke ran up the plant road at dusk. The howling from the far bunker is the lure.
  showCaption(OPENING.where, 2, 7)
  showCaption(OPENING.gate, 10, 8)
  showCaption(OPENING.howl, 19, 7)
  hud.stickyHint = HINTS.flashlight
  engine.addSystem(function hintSystem() {
    if (flashlight.toggles > 0) {
      hud.stickyHint = ''
      showHint(HINTS.use, 1, 7)
      showHint(HINTS.graphics, 9, 7)
      engine.removeSystem(hintSystem)
    }
  })

  let waited = 0
  let mothman: MothmanHost | null = null
  engine.addSystem(function startup(dt) {
    waited += dt
    if (mothman === null && (bounds.ready || waited > 2)) {
      forceFirstPerson(bounds.w, bounds.d)
      mothman = new MothmanHost()
      howlLure()
      ending()
    }
    if (mothman !== null) engine.removeSystem(startup)
  })

  deadDogBeat()
  signText()
}

/** The dog howls from bunker 7. The sound sits on the line to it, never farther than 18 m, louder as you near. */
function howlLure() {
  const r = roostSpot()
  const goal = Vector3.create(r.door.x, 1.2, r.door.z)
  const e = engine.addEntity()
  Transform.create(e, { position: goal })
  AudioSource.create(e, { audioClipUrl: 'assets/audio/howl.ogg', loop: true, playing: false, volume: 0.3 })
  let lastVol = 0.3
  engine.addSystem(function lure() {
    const p = Transform.get(engine.PlayerEntity).position
    const to = Vector3.subtract(goal, p)
    const d = Vector3.length(to)
    // The howl stops before you reach the roost, not when you find the collar: the dog has been dead a while
    // (owner pass 6). The silence is the last stretch of road.
    if (story.collar || d < 36) {
      AudioSource.getMutable(e).playing = false
      if (!story.collar) showCaption(CAPTIONS.howlStopped, 0.5, 4)
      engine.removeSystem(lure)
      return
    }
    if (frames.n >= 2) setLoop(e, true)
    const t = Transform.getMutable(e)
    t.position = d > 18 ? Vector3.add(p, Vector3.scale(to, 18 / d)) : goal
    const vol = d > 90 ? 0.22 : d > 30 ? 0.22 + ((90 - d) / 60) * 0.38 : 0.6 + ((30 - Math.max(d, 8)) / 22) * 0.4
    if (Math.abs(vol - lastVol) > 0.04) { AudioSource.getMutable(e).volume = vol; lastVol = vol }
  })
}

/**
 * Lore beat: the dead dog on the road is not yours, and it is gone when you look back for it. The line waits until you
 * step out of the cabin: the cabin comes right after the dog and takes all of your attention on the way in.
 */
function deadDogBeat() {
  let passed = false
  let seen = false
  let gone = false
  let wasInside = false
  let dog = engine.getEntityOrNullByName('Forest: dead dog')
  engine.addSystem(function dogSystem() {
    if (dog === null) dog = engine.getEntityOrNullByName('Forest: dead dog')
    if (dog === null) return
    const leaving = wasInside && !cabin.inside
    wasInside = cabin.inside
    if (!gone) {
      const p = Transform.get(engine.PlayerEntity).position
      const d = Transform.get(dog).position
      const dist = Vector3.distance(p, d)
      if (!seen && dist < 7 && beamHits(d)) { seen = true; showCaption(CAPTIONS.dogSeen, 0.5, 7) }
      if (dist < 3) passed = true
      if ((passed || seen) && ((dist > 8 && !beamHits(d)) || cabin.inside)) {
        gone = true
        engine.removeEntity(dog)
        if (!seen) engine.removeSystem(dogSystem) // never noticed it: nothing to miss
      }
    }
    if (gone && seen && leaving) {
      showCaption(CAPTIONS.dogGone, 1.5, 6)
      engine.removeSystem(dogSystem)
    }
  })
}

/**
 * The reckoning: after the voice, the way out is the road back. Reaching the gate ends the night, and the line you get
 * depends on whether the light is on when you arrive.
 */
function ending() {
  let t = -1
  engine.addSystem(function endSystem(dt) {
    if (story.ended) { hud.black = 1; hud.deathAlpha = 1; return } // nothing brings the world back
    if (story.phase !== 'revealed') return
    const p = Transform.get(engine.PlayerEntity).position
    const dHome = Math.hypot(p.x - SPAWN.x, p.z - SPAWN.z)
    if (!story.walkingOut) { if (dHome > 40) story.walkingOut = true; return }
    if (t < 0) {
      if (dHome > 7 || hud.black > 0) return
      t = 0
      hud.deathText = flashlight.on ? ENDINGS.lit : ENDINGS.dark
      setObjective(...OBJECTIVES.over)
    }
    t += dt
    // The screen goes black and stays black: the night is over, the words stay up (owner pass 9).
    hud.black = Math.min(1, t / 2.5)
    hud.deathAlpha = t > 2 ? Math.min(1, (t - 2) / 1.2) : 0
    if (t > 4) story.ended = true
  })
}

/** The post sign at the gate gets its text in code (the model is a blank board). */
function signText() {
  let tries = 0
  engine.addSystem(function findSign() {
    tries++
    const sign = engine.getEntityOrNullByName('Forest: sign')
    if (sign === null) { if (tries > 600) engine.removeSystem(findSign); return }
    // TextShape is unlit: white letters would glow in the dark. A pale painted board behind black letters is lit
    // by the flashlight like everything else.
    const board = engine.addEntity()
    Transform.create(board, { parent: sign, position: Vector3.create(0, 1.47, 0.045), rotation: Quaternion.fromEulerDegrees(0, 180, 0), scale: Vector3.create(0.6, 1.02, 1) })
    MeshRenderer.setPlane(board)
    Material.setPbrMaterial(board, { albedoColor: Color4.create(0.8, 0.76, 0.66, 1), roughness: 0.95, metallic: 0 })
    const text = engine.addEntity()
    Transform.create(text, { parent: sign, position: Vector3.create(0, 1.47, 0.06), rotation: Quaternion.fromEulerDegrees(0, 180, 0), scale: Vector3.create(0.32, 0.32, 0.32) })
    TextShape.create(text, {
      text: SIGN,
      fontSize: 1.0,
      font: Font.F_SERIF,
      textColor: Color4.create(0.06, 0.05, 0.04, 1),
      textAlign: TextAlignMode.TAM_MIDDLE_CENTER,
      width: 1.5,
      height: 3,
      textWrapping: true
    })
    engine.removeSystem(findSign)
  })
}

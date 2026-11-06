import { engine, Transform, TextShape, Font, TextAlignMode, AudioSource, InputModifier, MeshRenderer, MeshCollider, ColliderLayer, Material, GltfContainer } from '@dcl/sdk/ecs'
import { Vector3, Color4, Quaternion } from '@dcl/sdk/math'
import { loadBounds, bounds, roostSpot } from './config'
import { setupNight, forceFirstPerson } from './environment'
import { setupFlashlight, beamHits, flashlight } from './flashlight'
import { setupAmbience, setLoop, frames } from './audio'
import { setupMoths, resetMoths } from './moths'
import { onReset } from './game'
import { setupTelepathy, showCaption, showHint, hud } from './telepathy'
import { SIGN, OPENING, HINTS, CAPTIONS, OBJECTIVES, ENDINGS } from './script'
import { setupHud } from './hud'
import { setupDebug } from './debug'
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
  setupDebug()
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

  // A death resets the night. The screen is black when this runs (host.ts, !take); the fade-in takes 2.7 s more, so the
  // opening plays again once the gate is in view, and the objective comes back with it.
  onReset(() => {
    resetMoths()
    setObjective('', '')
    showCaption(OPENING.where, 4.5, 7)
    showCaption(OPENING.gate, 12.5, 8)
    showCaption(OPENING.howl, 21.5, 7)
    openingIn = 4.5
  })
  engine.addSystem((dt) => {
    if (openingIn < 0) return
    openingIn -= dt
    if (openingIn <= 0) setObjective(...OBJECTIVES.start)
  })
}

let openingIn = -1

/** The dog howls from bunker 7. The sound sits on the line to it, never farther than 18 m, louder as you near. */
function howlLure() {
  const r = roostSpot()
  const goal = Vector3.create(r.door.x, 1.2, r.door.z)
  const e = engine.addEntity()
  Transform.create(e, { position: goal })
  AudioSource.create(e, { audioClipUrl: 'assets/audio/howl.ogg', loop: true, playing: false, volume: 0.3 })
  let lastVol = 0.3
  let stopped = false
  onReset(() => { stopped = false })
  engine.addSystem(function lure() {
    if (stopped) return
    const p = Transform.get(engine.PlayerEntity).position
    const to = Vector3.subtract(goal, p)
    const d = Vector3.length(to)
    // The howl stops before you reach the roost, not when you find the collar: the dog has been dead a while
    // (owner pass 6). The silence is the last stretch of road. A reset starts it again.
    if (story.collar || d < 36) {
      setLoop(e, false)
      if (!story.collar) showCaption(CAPTIONS.howlStopped, 0.5, 4)
      stopped = true
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
  let told = false
  let wasInside = false
  let dog = engine.getEntityOrNullByName('Forest: dead dog')
  let home: Vector3 | null = null // where it lies; it is sunk 50 m under the road when taken, and comes back on a reset
  onReset(() => {
    passed = seen = gone = told = false
    if (dog !== null && home !== null) Transform.getMutable(dog).position = home
  })
  engine.addSystem(function dogSystem() {
    if (dog === null) dog = engine.getEntityOrNullByName('Forest: dead dog')
    if (dog === null) return
    if (home === null) home = Vector3.clone(Transform.get(dog).position)
    const leaving = wasInside && !cabin.inside
    wasInside = cabin.inside
    if (!gone) {
      const p = Transform.get(engine.PlayerEntity).position
      const d = home
      const dist = Vector3.distance(p, d)
      if (!seen && dist < 7 && beamHits(d)) { seen = true; showCaption(CAPTIONS.dogSeen, 0.5, 7) }
      if (dist < 3) passed = true
      if ((passed || seen) && ((dist > 8 && !beamHits(d)) || cabin.inside)) {
        gone = true
        Transform.getMutable(dog).position = Vector3.add(home, Vector3.create(0, -50, 0))
      }
    }
    if (gone && seen && leaving && !told) {
      told = true
      showCaption(CAPTIONS.dogGone, 1.5, 6)
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
    if (story.phase !== 'revealed') { t = -1; return }
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

/**
 * The post sign at the gate is built here from primitives: a post and a board, with the text on the board. The
 * composite only places an empty anchor named 'Forest: sign' (older composites still carry the asset-pack model on
 * it, whose back face shows a different sign: that model is dropped at start).
 */
function signText() {
  let tries = 0
  engine.addSystem(function findSign() {
    tries++
    const sign = engine.getEntityOrNullByName('Forest: sign')
    if (sign === null) { if (tries > 600) engine.removeSystem(findSign); return }
    if (GltfContainer.has(sign)) GltfContainer.deleteFrom(sign)
    Transform.getMutable(sign).scale = Vector3.One() // everything below is in metres
    const wood = { albedoColor: Color4.create(0.3, 0.22, 0.14, 1), roughness: 0.95, metallic: 0 }
    // TextShape is unlit: white letters would glow in the dark. A pale painted board behind black letters is lit
    // by the flashlight like everything else.
    const paint = { albedoColor: Color4.create(0.8, 0.76, 0.66, 1), roughness: 0.95, metallic: 0 }
    const post = engine.addEntity()
    Transform.create(post, { parent: sign, position: Vector3.create(0, 1.95, -0.09), scale: Vector3.create(0.16, 3.9, 0.16) })
    MeshRenderer.setBox(post)
    MeshCollider.setBox(post, ColliderLayer.CL_PHYSICS)
    Material.setPbrMaterial(post, wood)
    const board = engine.addEntity()
    Transform.create(board, { parent: sign, position: Vector3.create(0, 2.9, 0), scale: Vector3.create(1.4, 2.0, 0.08) })
    MeshRenderer.setBox(board)
    Material.setPbrMaterial(board, paint)
    const text = engine.addEntity()
    Transform.create(text, { parent: sign, position: Vector3.create(0, 2.9, 0.045), rotation: Quaternion.fromEulerDegrees(0, 180, 0), scale: Vector3.create(0.7, 0.7, 0.7) })
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

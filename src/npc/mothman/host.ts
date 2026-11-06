import { engine, Transform, AudioSource } from '@dcl/sdk/ecs'
import { Vector3, Quaternion } from '@dcl/sdk/math'
import { movePlayerTo } from '~system/RestrictedActions'
import { PlanRunner, DecompositionStatus } from '../../htn-planner/htn/planner'
import { WorldState } from '../../htn-planner/htn/world-state'
import { sym } from '../../htn-planner/htn/atom'
import { mothmanDomain } from './mothman.htn'
import { createMothmanBody, MothmanBody } from './body'
import { MOTHMAN_CLIPS, MothmanClip } from './animations'
import { flashlight, beamHits, cameraRay, failLight } from '../../flashlight'
import { bounds, bands, roostSpot } from '../../config'
import { telepathy, startTelepathy, hud, showCaption, showHint, closeDocument, docOpenFor, captionsPending } from '../../telepathy'
import { setLoop, loopSound } from '../../audio'
import { cabin } from '../../cabin'
import { layout } from '../../layout'
import { setObjective } from '../../objectives'
import { CAPTIONS, HINTS, OBJECTIVES, DEATHS } from '../../script'
import { onReset, resetGame } from '../../game'
import { insideBunker, keepOut, grace } from '../../shelter'

/**
 * Host for the Mothman's HTN domain (mothman.domain). The host owns: sensing (facts), the replan policy (fact key
 * changes or plan end), action executors, movement, animation, sound, attention cues and the story phase. The planner
 * decides what he does; the host decides how it looks.
 */
type Status = 'running' | 'done'
type Executor = { start(): void; update(dt: number): Status; cancel(): void }

export const story = {
  phase: 'ignorant' as 'ignorant' | 'revealed',
  scared: false,
  deaths: 0,
  litAfterReveal: 0,
  collar: false, // Duke's collar picked up at bunker 7: summons him
  walkingOut: false, // after the reveal, the player has left the roost; the road back is the ending
  awake: false, // he does nothing, and is not even rendered, until the player has walked 55 m up the road (owner passes 5, 9)
  // A death resets everything above (resetGame): the next night starts as the first did. Only `deaths` and `ended` keep.
  summoned: false, // latched once the collar's page is down and its lines have run: only then his final approach (owner pass 6)
  ended: false
}

const SPEEDS = { approachMid: 1.7, approachNear: 1.5, hover: 2.4, retreat: 7, lurk: 12, lunge: 14, window: 6 }
const SPAWN = Vector3.create(layout.spawn[0], 0.1, layout.spawn[1])
/** Metres from the gate before he exists. The register and the sign are within 10 m; the dead dog is at 77 m. */
const WAKE_DISTANCE = 55

export class MothmanHost {
  readonly body: MothmanBody
  private readonly world = new WorldState()
  private readonly runner: PlanRunner
  private exec: Executor | null = null
  private lastKey = ''
  private hasPlan = false
  private locked = false // an uninterruptible executor (speak, take) is running
  private drone = loopSound(null, 'assets/audio/drone.ogg', 0.7, true)
  private clock = 0
  private eyes = 0
  private humOn = false
  private lastYaw = 0
  private cueClock = 0
  private cueFlip = false
  private faceAt: Vector3 | null = null // when set, he faces this point instead of the player
  private pendingDeath = 0
  private resetLitAfterRetreat = false
  private hoverSeed = Math.random() * 10
  private airborne = false
  private idleVariant = 0
  private cabinOpen = false // !enter / !take: the one time he may be inside the cabin

  constructor() {
    const r = roostSpot()
    this.body = createMothmanBody(Vector3.create(r.x, r.top, r.z))
    this.runner = new PlanRunner(mothmanDomain, this.world, {
      defaultTopLevel: 'behave',
      onDiagnostic: (d) => console.log(`[htn] ${d.code}: ${d.message}`)
    })
    engine.addSystem((dt) => this.update(dt))
    onReset(() => this.reset())
  }

  /** Back to the roost, asleep, with the story at its first page. Called with the screen black; the running !take
   *  executor keeps the lock until the fade-in is done, then the planner sees `dormant` and starts over. */
  private reset() {
    Object.assign(story, { phase: 'ignorant', scared: false, litAfterReveal: 0, collar: false, walkingOut: false, awake: false, summoned: false })
    const r = roostSpot()
    Transform.getMutable(this.body.root).position = Vector3.create(r.x, r.top, r.z)
    this.body.setClip('idle_ground')
    this.airborne = false
    this.faceAt = null
    this.setHum(false)
    setLoop(this.drone, false)
    this.eyes = 0
    this.lastKey = ''
    this.cabinOpen = false
  }

  // ---- sensing -------------------------------------------------------------------------------------------------

  private player(): Vector3 { return Transform.get(engine.PlayerEntity).position }
  private me(): Vector3 { return Transform.get(this.body.root).position }
  private distXZ(): number {
    const p = this.player(), m = this.me()
    return Math.hypot(p.x - m.x, p.z - m.z)
  }
  private band(): 'far' | 'mid' | 'near' {
    const d = this.distXZ()
    return d <= bands.near + 0.4 ? 'near' : d <= bands.mid + 0.6 ? 'mid' : 'far'
  }
  private inView(): boolean {
    const { origin, forward } = cameraRay()
    const to = Vector3.subtract(this.body.eyePos(), origin)
    const d = Vector3.length(to)
    if (d < 0.01) return true
    return Vector3.dot(forward, Vector3.scale(to, 1 / d)) > 0.45
  }

  private sense(dt: number): string {
    const beam = flashlight.on ? 'on' : 'off'
    const lit = !flashlight.on ? 'none' : flashlight.litFor >= 45 ? 'long' : flashlight.litFor >= 18 ? 'some' : 'none'
    const dist = this.band()
    if (story.collar && !story.summoned && docOpenFor() < 0 && captionsPending() <= 0) story.summoned = true
    const summoned = story.summoned && story.phase === 'ignorant'
    const hidden = story.collar && !story.summoned // between the collar and the voice: out of sight, eyes dark
    if (!story.awake) {
      const p = this.player()
      if (Math.hypot(p.x - SPAWN.x, p.z - SPAWN.z) > WAKE_DISTANCE || summoned) {
        story.awake = true
        flashlight.litFor = 0 // the beam clock starts now: the first paper, read in the light at the gate, counts for nothing
      }
    }
    const place = cabin.inside ? 'cabin' : 'woods'
    const lamp = cabin.lampOn ? 'on' : 'off'
    const lampLit = !cabin.lampOn || !cabin.inside ? 'none' : cabin.lampOnFor >= 110 ? 'spent' : cabin.lampOnFor >= 65 ? 'long' : cabin.lampOnFor >= 30 ? 'some' : 'none'
    const sheltered = insideBunker(this.player()) // a bunker: safe. He waits outside.
    const reading = docOpenFor() >= 0 // a page is up: nothing moves on the player
    if (story.phase === 'revealed' && flashlight.on && !grace()) {
      story.litAfterReveal += dt
      if (story.litAfterReveal > 18 && flashlight.dead <= 0 && flashlight.dying <= 0) {
        failLight(7)
        story.litAfterReveal = 0
      }
    }
    this.world.set('beam', sym(beam))
    this.world.set('lit', sym(lit))
    this.world.set('dist', sym(dist))
    this.world.set('phase', sym(story.phase))
    this.world.set('place', sym(place))
    this.world.set('lamp', sym(lamp))
    this.world.set('lamp_lit', sym(lampLit))
    this.world.clear('summoned', 0)
    if (summoned) this.world.add('summoned')
    this.world.clear('scared', 0)
    if (story.scared) this.world.add('scared')
    this.world.clear('dormant', 0)
    if (!story.awake) this.world.add('dormant')
    this.world.clear('hidden', 0)
    if (hidden) this.world.add('hidden')
    this.world.clear('sheltered', 0)
    if (sheltered) this.world.add('sheltered')
    this.world.clear('reading', 0)
    if (reading) this.world.add('reading')
    // Replan key: only events outside his control (the lights, the place, the story). Distance and fear are facts he
    // plans with, but changes he causes himself must not interrupt a running plan.
    return `${beam}|${lit}|${story.phase}|${summoned ? 1 : 0}|${place}|${lamp}|${lampLit}|${story.awake ? 1 : 0}|${hidden ? 1 : 0}|${sheltered ? 1 : 0}|${reading ? 1 : 0}`
  }

  // ---- planning loop --------------------------------------------------------------------------------------------

  private update(dt: number) {
    this.clock += dt
    const key = this.sense(dt)
    if (!this.locked && (key !== this.lastKey || !this.hasPlan)) {
      if (this.exec !== null) { this.exec.cancel(); this.exec = null }
      const status: DecompositionStatus = this.runner.plan()
      this.hasPlan = status === 'succeeded'
      this.lastKey = key
      if (!this.hasPlan) console.log(`[mothman] no plan (${status}) for ${key}`)
      else {
        const m = this.me()
        console.log(`[mothman] ${key} -> ${this.runner.steps.map((s) => s.name).join(' ')} @ ${m.x.toFixed(1)},${m.y.toFixed(1)},${m.z.toFixed(1)} d=${this.distXZ().toFixed(1)}`)
      }
    }
    if (this.hasPlan) {
      if (this.exec === null) {
        const r = this.runner.resolve()
        if (r === 'ready') {
          const step = this.runner.current()!
          this.exec = this.makeExecutor(step.name, step.args.map((a) => (a.t === 'float' || a.t === 'int' ? a.v : a.t === 'sym' ? a.v : 0)))
          this.exec.start()
        } else {
          this.hasPlan = false
        }
      } else {
        const s = this.exec.update(dt)
        if (s === 'done') {
          this.exec = null
          this.runner.complete()
        }
      }
    }
    this.body.updateAnimation(dt)
    this.present(dt)
  }

  // ---- presentation: facing, eyeshine, attention cues ------------------------------------------------------------

  private present(dt: number) {
    const p = this.faceAt ?? this.player(), m = this.me()
    const yaw = (Math.atan2(p.x - m.x, p.z - m.z) * 180) / Math.PI
    if (Math.abs(yaw - this.lastYaw) > 0.5) {
      Transform.getMutable(this.body.root).rotation = Quaternion.fromEulerDegrees(0, yaw, 0)
      this.lastYaw = yaw
    }
    this.body.setVisible(story.awake)
    const lit = beamHits(this.body.eyePos())
    const summoned = story.summoned && story.phase === 'ignorant'
    const target = !story.awake || (story.collar && !story.summoned) ? 0 : lit ? 7 : summoned || this.faceAt !== null ? 2.0 : story.phase === 'revealed' ? 1.4 : this.band() === 'near' ? 0.6 : 0.15
    this.eyes += (target - this.eyes) * Math.min(1, dt * 8)
    this.body.setEyes(this.eyes)

    // Attention: when he is active but out of view, a spatial sound from where he is. In the dark, a rarer call.
    this.cueClock -= dt
    if (this.cueClock <= 0 && !this.locked) {
      const d = this.distXZ()
      if (flashlight.on && !this.inView() && d <= bands.far + 4) {
        AudioSource.playSound(this.body.cue, this.cueFlip ? 'assets/audio/wingbeat.ogg' : 'assets/audio/call.ogg')
        this.cueFlip = !this.cueFlip
        this.cueClock = 3 + Math.random() * 2.5
      } else if (!flashlight.on && d <= bands.far + 12) {
        AudioSource.playSound(this.body.cue, 'assets/audio/call.ogg')
        this.cueClock = 8 + Math.random() * 6
      } else this.cueClock = 1
    }
  }

  private setHum(on: boolean) {
    if (on !== this.humOn) { this.humOn = on; setLoop(this.body.hum, on) }
  }

  // ---- movement ----------------------------------------------------------------------------------------------------

  private clampToScene(v: Vector3): Vector3 {
    return Vector3.create(Math.max(3, Math.min(bounds.w - 3, v.x)), Math.max(0, Math.min(12, v.y)), Math.max(3, Math.min(bounds.d - 3, v.z)))
  }

  private moveToward(target: Vector3, speed: number, dt: number, arrive = 0.25): boolean {
    const t = Transform.getMutable(this.body.root)
    const to = Vector3.subtract(target, t.position)
    const d = Vector3.length(to)
    if (d <= arrive) { t.position = target; return true }
    const step = Math.min(d, speed * dt)
    const from = t.position
    let next = keepOut(this.clampToScene(Vector3.add(from, Vector3.scale(to, step / d))), this.cabinOpen)
    if (Vector3.distance(next, from) < step * 0.3) {
      // pressed against a wall or a mound: slide along it instead of standing still
      const side = Vector3.scale(Vector3.create(to.z, 0, -to.x), step / Math.max(0.01, Math.hypot(to.x, to.z)))
      const slide = keepOut(this.clampToScene(Vector3.add(from, side)), this.cabinOpen)
      if (Vector3.distance(slide, from) > Vector3.distance(next, from)) next = slide
    }
    t.position = next
    return false
  }

  private ringPoint(dist: number, height: number, awayFrom?: Vector3): Vector3 {
    const p = this.player()
    let best = p, bestD = -1
    for (let i = 0; i < 10; i++) {
      const a = awayFrom === undefined ? Math.random() * Math.PI * 2 : Math.atan2(p.x - awayFrom.x, p.z - awayFrom.z) + (Math.random() - 0.5) * 1.2 + Math.PI
      const c = keepOut(this.clampToScene(Vector3.create(p.x + Math.sin(a) * dist, height, p.z + Math.cos(a) * dist)), this.cabinOpen)
      const d = Math.hypot(c.x - p.x, c.z - p.z)
      if (d > bestD) { bestD = d; best = c }
      if (d >= dist * 0.85) break
    }
    return best
  }

  /** A point `dist` in front of the player, where they are looking (so he lands in view), offset sideways by `side`. */
  private inFront(dist: number, height: number, side = 0): Vector3 {
    const p = this.player()
    const { forward } = cameraRay()
    const f = Vector3.normalize(Vector3.create(forward.x, 0, forward.z))
    const r = Vector3.create(f.z, 0, -f.x)
    return keepOut(this.clampToScene(Vector3.create(p.x + f.x * dist + r.x * side, height, p.z + f.z * dist + r.z * side)), this.cabinOpen)
  }

  private nearestWindow(): Vector3 {
    const m = this.me()
    let best = layout.cabin.windows[0], bd = Infinity
    for (const w of layout.cabin.windows) {
      const d = Math.hypot(w.x - m.x, w.z - m.z)
      if (d < bd) { bd = d; best = w }
    }
    return Vector3.create(best.x, 0.05, best.z)
  }

  // ---- executors -----------------------------------------------------------------------------------------------------

  private idleClip(): MothmanClip {
    return this.airborne ? (this.idleVariant++ % 2 === 0 ? 'idle_fly' : 'idle_fly_watch') : 'idle_ground'
  }

  private makeExecutor(name: string, args: (number | string)[]): Executor {
    const host = this
    const timed = (seconds: number, clip: MothmanClip = host.idleClip(), onTick?: (dt: number) => void): Executor => {
      let left = seconds
      return { start() { host.body.setClip(clip) }, update(dt) { left -= dt; onTick?.(dt); return left <= 0 ? 'done' : 'running' }, cancel() {} }
    }
    switch (name) {
      case '!wait':
        return timed(Number(args[0] ?? 1))
      case '!watch': {
        // Hold still and let the eyeshine work. If he is far beyond the far ring (the roost, after a respawn), he first
        // glides in through the dark to the ring, fast and unlit, so the slow approach never starts from 100 m away.
        let left = Number(args[0] ?? 1)
        let target: Vector3 | null = null
        return {
          start() { host.body.setClip(host.idleClip()) },
          update(dt) {
            left -= dt
            if (host.distXZ() > bands.far + 6) {
              if (target === null) { target = host.ringPoint(bands.far, 3 + Math.random() * 1.5); host.airborne = true; host.body.setClip('glide_retreat') }
              host.moveToward(target, SPEEDS.lurk, dt)
            }
            return left <= 0 ? 'done' : 'running'
          },
          cancel() {}
        }
      }
      case '!lurk': {
        let target: Vector3 | null = null
        return {
          start() { target = host.ringPoint(bands.far, 3 + Math.random() * 1.5); host.airborne = true; host.body.setClip('glide_retreat') },
          update(dt) { return target !== null && host.moveToward(target, SPEEDS.lurk, dt) ? 'done' : 'running' },
          cancel() {}
        }
      }
      case '!approach': {
        const band = String(args[0])
        const stop = band === 'near' ? bands.near : bands.mid
        const height = band === 'near' ? 0.05 : 1.2
        const speed = band === 'near' ? SPEEDS.approachNear : SPEEDS.approachMid
        let flapped = false
        let landing = -1
        let spot: Vector3 | null = null // the ground point he lands on: fixed once the landing starts
        return {
          start() {
            host.airborne = true
            host.setHum(true)
            host.body.setClip(story.phase === 'revealed' || band === 'near' ? 'fly_menacing' : 'idle_fly')
            AudioSource.playSound(host.body.wings, 'assets/audio/wingbeat.ogg')
          },
          update(dt) {
            const near = host.distXZ() <= stop + 0.6 && host.inView()
            if (band === 'near' && landing < 0 && near && host.me().y < 1.25) {
              landing = 0
              spot = host.inFront(stop, height) // from here on the camera no longer moves him
              host.body.setClip('land', true)
            }
            if (landing >= 0) landing += dt
            const target = spot ?? host.inFront(stop, height)
            const arrived = host.moveToward(target, host.distXZ() > bands.far + 2 ? SPEEDS.lurk : speed, dt, 0.1)
            // Horizontal distance alone must not finish the approach while he is still above the player. Once he is
            // landing on a fixed spot the player turning away must not keep him from finishing.
            const landed = host.body.clipFinished('land') || landing >= MOTHMAN_CLIPS.land.duration + 0.25
            if (arrived && (band !== 'near' ? host.inView() : landed)) {
              host.airborne = band !== 'near'
              host.setHum(host.airborne)
              host.body.setClip(host.airborne ? 'idle_fly' : 'idle_ground')
              return 'done'
            }
            if (!flapped && host.distXZ() < stop + 6) { flapped = true; AudioSource.playSound(host.body.wings, 'assets/audio/wingbeat.ogg') }
            return 'running'
          },
          cancel() { host.setHum(false) }
        }
      }
      case '!hover': {
        // Hangs in the air in front of the player at mid range, swaying side to side, never passing behind them.
        let left = Number(args[0] ?? 5)
        let t = 0
        return {
          start() { host.airborne = true; host.setHum(true); host.body.setClip(story.phase === 'revealed' ? 'hover_menacing' : host.idleClip()) },
          update(dt) {
            left -= dt; t += dt
            const side = Math.sin(t * 0.9 + host.hoverSeed) * 2.2
            const height = 1.4 + 0.5 * Math.sin(t * 1.7 + host.hoverSeed)
            host.moveToward(host.inFront(bands.mid - 0.5, height, side), SPEEDS.hover, dt, 0.05)
            if (flashlight.on && host.distXZ() < bands.mid + 1) flashlight.flicker = Math.max(flashlight.flicker, 0.25)
            return left <= 0 ? 'done' : 'running'
          },
          cancel() { host.setHum(false) }
        }
      }
      case '!retreat': {
        let target: Vector3 | null = null
        return {
          start() { target = host.ringPoint(bands.far, 3.2, host.me()); host.setHum(false); host.airborne = true; host.body.setClip('glide_retreat'); host.faceAt = null },
          update(dt) {
            if (target !== null && host.moveToward(target, SPEEDS.retreat, dt, 0.4)) {
              if (host.resetLitAfterRetreat) { host.resetLitAfterRetreat = false; flashlight.litFor = 0 }
              return 'done'
            }
            return 'running'
          },
          cancel() { if (host.resetLitAfterRetreat) { host.resetLitAfterRetreat = false; flashlight.litFor = 0 } }
        }
      }
      case '!rise': {
        let target: Vector3 | null = null
        let elapsed = 0
        return {
          start() {
            const m = host.me()
            target = Vector3.create(m.x, Math.min(11, m.y + 5), m.z)
            host.airborne = true
            AudioSource.playSound(host.body.wings, 'assets/audio/wingbeat.ogg')
            host.body.setClip('takeoff', true)
          },
          update(dt) {
            elapsed += dt
            const arrived = target !== null && host.moveToward(target, 6.5, dt)
            if (host.body.clipFinished('takeoff') || elapsed >= MOTHMAN_CLIPS.takeoff.duration + 0.25) {
              host.body.setClip('hover_menacing')
              if (arrived) return 'done'
            }
            return 'running'
          },
          cancel() {}
        }
      }
      case '!screech':
        return {
          start() {
            AudioSource.playSound(host.body.oneShot, 'assets/audio/screech.ogg')
            if (host.band() !== 'far') flashlight.flicker = Math.max(flashlight.flicker, 1.6)
            host.body.setClip('screech', true)
          },
          update: timed(MOTHMAN_CLIPS.screech.duration).update,
          cancel() {}
        }
      case '!loom':
        return timed(Number(args[0] ?? 3), 'ground_loom', () => {
          if (host.band() === 'near') flashlight.flicker = Math.max(flashlight.flicker, 0.4)
        })
      case '!lunge': {
        // The jumpscare: straight into the face, a scream, and he is gone. Survivable; next time is not.
        let t = 0
        return {
          start() {
            t = 0
            AudioSource.playSound(host.body.oneShot, 'assets/audio/lunge.ogg')
            flashlight.flicker = 1.2
            host.body.setClip('lunge', true)
          },
          update(dt) {
            t += dt
            const { origin, forward } = cameraRay()
            const face = Vector3.create(origin.x + forward.x * 0.7, 0, origin.z + forward.z * 0.7)
            host.moveToward(face, SPEEDS.lunge, dt, 0.05)
            if (t > 0.35 && t < 0.5) AudioSource.playSound(host.body.oneShot, 'assets/audio/screech.ogg')
            if (t >= 1.3) {
              story.scared = true
              host.resetLitAfterRetreat = true
              return 'done'
            }
            return 'running'
          },
          cancel() {}
        }
      }
      case '!hide': {
        // Out of sight, behind the player and beyond the far ring, eyes dark, no hum: the roost is empty when they turn.
        let target: Vector3 | null = null
        return {
          start() { target = host.ringPoint(bands.far + 14, 6, host.me()); host.airborne = true; host.body.setClip('glide_retreat'); host.setHum(false); host.faceAt = null },
          update(dt) { return target !== null && host.moveToward(target, SPEEDS.lurk, dt, 0.5) ? 'done' : 'running' },
          cancel() {}
        }
      }
      case '!window': {
        // To the nearest cabin window; stare in at the bulb; tap the glass. The bulb flickers from the moment he shows at
        // the glass and for as long as he stays. A replan while he is already there (the lamp clock, the player stepping
        // out and back in) must not fly and land him again: he just keeps staring.
        const hold = Number(args[0] ?? 5)
        let target: Vector3 | null = null
        let there = false
        let left = hold
        let tapped = false
        let landing = -1
        let syncLeft = 0
        let onHim = 0 // seconds the beam has been held on him through the glass
        const bulb = () => Vector3.create(layout.cabin.bulb.x, 1.6, layout.cabin.bulb.z)
        /** Three seconds of the beam on his face through the window and he snuffs it: sparks, and five seconds dead. */
        const snuff = (dt: number) => {
          if (cabin.inside && flashlight.on && flashlight.dead <= 0 && beamHits(host.body.eyePos())) onHim += dt
          else onHim = Math.max(0, onHim - dt * 2)
          if (onHim >= 3) { onHim = 0; failLight(5, 0) }
        }
        /** Both lights blink while he is at the glass. Every few seconds the beam falls into step with the bulb, or out of it. */
        const blink = (dt: number) => {
          cabin.lampFlicker = Math.max(cabin.lampFlicker, 0.3)
          if (!cabin.inside || !flashlight.on) return
          flashlight.flicker = Math.max(flashlight.flicker, 0.3)
          syncLeft -= dt
          if (syncLeft <= 0) { flashlight.syncLamp = Math.random() < 0.5; syncLeft = 2 + Math.random() * 3 }
        }
        return {
          start() {
            target = host.nearestWindow()
            host.setHum(true)
            const m = host.me()
            const clip = host.body.currentClip()
            // on the spot and on the ground (a replan, or a !watch while the player read): no second landing
            if (Math.hypot(m.x - target.x, m.z - target.z) < 0.3 && (clip === 'land' || clip === 'window_stare' || clip === 'idle_ground')) {
              there = true
              tapped = true
              host.faceAt = bulb()
              if (clip === 'land' && !host.body.clipFinished('land')) landing = 0 // let the landing finish
              else { host.airborne = false; host.body.setClip('window_stare') }
              return
            }
            host.airborne = true
            host.body.setClip('fly_menacing')
          },
          update(dt) {
            if (target === null) return 'running'
            if (!there) {
              const m = host.me()
              if (Math.hypot(m.x - target.x, m.z - target.z) < 5) blink(dt)
              if (host.moveToward(target, SPEEDS.window, dt, 0.2)) {
                there = true
                landing = 0
                host.body.setClip('land', true)
                host.faceAt = bulb()
                cabin.lampFlicker = 2.0
                if (!tapped) { tapped = true; AudioSource.playSound(host.body.cue, 'assets/audio/tap.ogg') }
                if (cabin.windowCaptionVisit !== cabin.visits) {
                  // Once per visit: a repeated caption would walk over everything else on screen.
                  cabin.windowCaptionVisit = cabin.visits
                  showCaption(CAPTIONS.window, 0, 4)
                  setObjective(...OBJECTIVES.window)
                }
              }
              return 'running'
            }
            blink(dt)
            snuff(dt)
            if (landing >= 0) {
              landing += dt
              if (!host.body.clipFinished('land') && landing < MOTHMAN_CLIPS.land.duration + 0.25) return 'running'
              landing = -1
              host.airborne = false
              host.body.setClip('window_stare')
            }
            left -= dt
            if (left <= 0) { flashlight.syncLamp = false; return 'done' }
            return 'running'
          },
          cancel() { host.faceAt = null; host.setHum(false); flashlight.syncLamp = false }
        }
      }
      case '!bang': {
        let target: Vector3 | null = null
        let t = 0
        return {
          start() { target = Vector3.create(layout.cabin.door.x, 0.05, layout.cabin.door.z - 1.6); host.body.setClip('enter_glide'); host.faceAt = null },
          update(dt) {
            if (target !== null && !host.moveToward(target, SPEEDS.window, dt, 0.2)) return 'running'
            host.faceAt = Vector3.create(layout.cabin.bulb.x, 1.6, layout.cabin.bulb.z)
            if (t === 0) { host.airborne = false; host.body.setClip('door_bang', true) }
            t += dt
            if (t > 0.3 && t < 0.3 + dt * 1.5) { AudioSource.playSound(host.body.oneShot, 'assets/audio/lunge.ogg'); cabin.lampFlicker = 1.5 }
            if (t > 1.4 && t < 1.4 + dt * 1.5) { AudioSource.playSound(host.body.cue, 'assets/audio/tap.ogg') }
            return t >= MOTHMAN_CLIPS.door_bang.duration ? 'done' : 'running'
          },
          cancel() { host.faceAt = null }
        }
      }
      case '!enter': {
        // The door opens by itself and he comes in. Then !take.
        let stage = 0
        return {
          start() { cabin.forceOpen = true; host.cabinOpen = true; host.airborne = false; host.body.setClip('enter_glide'); host.faceAt = null; AudioSource.playSound(host.body.oneShot, 'assets/audio/screech.ogg') },
          update(dt) {
            const d = layout.cabin.door
            if (stage === 0) { if (host.moveToward(Vector3.create(d.x, 0.05, d.z - 1.2), 3, dt, 0.2)) stage = 1; return 'running' }
            if (stage === 1) { if (host.moveToward(Vector3.create(d.x, 0.05, d.z + 1.2), 2, dt, 0.2)) stage = 2; return 'running' }
            return 'done'
          },
          cancel() { host.cabinOpen = false }
        }
      }
      case '!take': {
        // The kill. Blackout, a line, and the player wakes up back at the gate with the light off.
        let t = 0
        return {
          start() {
            t = 0
            host.locked = true
            host.cabinOpen = true // he may already be inside, after !enter
            host.setHum(false)
            host.faceAt = null
            closeDocument() // a paper left open would still be up after the respawn
            AudioSource.playSound(host.body.oneShot, 'assets/audio/lunge.ogg')
            flashlight.flicker = 1.0
            host.body.setClip('lunge', true)
          },
          update(dt) {
            t += dt
            if (t < 1.2) {
              const { origin, forward } = cameraRay()
              host.moveToward(Vector3.create(origin.x + forward.x * 0.6, 0, origin.z + forward.z * 0.6), SPEEDS.lunge, dt, 0.05)
              if (t > 0.4 && t < 0.55) AudioSource.playSound(host.body.oneShot, 'assets/audio/screech.ogg')
            }
            if (t >= 0.9) hud.black = Math.min(1, (t - 0.9) / 1.0)
            if (t >= 0.9 && t < 7.6) flashlight.dead = 999 // only until the respawn below clears it, or the light never comes back
            if (t >= 2.4 && t < 7.5) {
              hud.deathText = cabin.inside ? DEATHS.cabin : DEATHS.road
              hud.deathAlpha = Math.min(1, (t - 2.4) / 1.0, (7.5 - t) / 0.8)
            }
            if (t >= 7.6 && t < 7.7 && story.deaths === host.pendingDeath) {
              host.pendingDeath++
              story.deaths++
              // The whole night starts over: lights, cabin, papers, the dog on the road, the objective, him at the roost.
              resetGame()
              host.locked = true // resetGame cleared nothing of this executor; keep the lock through the fade-in
              movePlayerTo({ newRelativePosition: SPAWN, cameraTarget: Vector3.create(SPAWN.x + 10, 1, SPAWN.z + 14) })
            }
            if (t >= 8.2) hud.black = Math.max(0, 1 - (t - 8.2) / 2.0)
            if (t >= 10.3) { hud.black = 0; hud.deathAlpha = 0; host.locked = false; host.cabinOpen = false; return 'done' }
            return 'running'
          },
          cancel() { host.locked = false; host.cabinOpen = false; hud.black = 0; hud.deathAlpha = 0 }
        }
      }
      case '!speak': {
        // He waits, standing there, until the player has put down whatever they are reading and the captions have
        // run out; then the voice. (Owner pass 5: the passage was starting over an open paper.)
        let started = false
        let quiet = 0
        let spot: Vector3 | null = null // where he stands: a ground point chosen once, never the camera
        let flying = false
        const settle = () => {
          host.airborne = false
          flying = false
          host.body.setClip('telepathy')
        }
        return {
          start() {
            host.locked = true
            host.setHum(false)
            // If !approach already put him down in front of the player, that is his spot. Otherwise the ground in
            // front of where they are looking, picked now and kept: turning the camera must not drag him around.
            const m = host.me()
            const close = host.distXZ() <= bands.near + 1.2 && host.inView() && m.y < 1.25
            spot = close ? Vector3.create(m.x, 0.05, m.z) : host.inFront(bands.near + 0.4, 0.05)
            settle()
          },
          update(dt) {
            if (spot !== null) {
              // Walked well away from him: he comes down again in front of the player, once, on a new fixed spot.
              if (!flying && host.distXZ() > bands.mid + 3) {
                spot = host.inFront(bands.near + 0.4, 0.05)
                flying = true
                host.airborne = true
                host.body.setClip('fly_menacing')
                AudioSource.playSound(host.body.wings, 'assets/audio/wingbeat.ogg')
              }
              if (host.moveToward(spot, flying ? SPEEDS.window : 2.5, dt, 0.05) && flying) settle()
            }
            if (!started) {
              if (docOpenFor() >= 0 || captionsPending() > 0) { quiet = 0; return 'running' }
              quiet += dt
              if (quiet < 1.5) return 'running'
              started = true
              startTelepathy()
              setLoop(host.drone, true)
              flashlight.flicker = 1.5
              setObjective(...OBJECTIVES.listen)
              return 'running'
            }
            if (telepathy.done) {
              story.phase = 'revealed'
              story.litAfterReveal = 0
              // The voice wipes the slate: the next thing the player does with the switch is the real test (GDD §10).
              story.scared = false
              flashlight.litFor = 0
              host.locked = false
              setLoop(host.drone, false)
              if (flashlight.on) flashlight.flicker = Math.max(flashlight.flicker, 2.5) // the beam stutters: he means it
              setObjective(...OBJECTIVES.gate)
              showCaption(CAPTIONS.getOut, 2.5, 6)
              showHint(HINTS.afterVoice, 9, 7)
              return 'done'
            }
            return 'running'
          },
          cancel() { host.locked = false; setLoop(host.drone, false) }
        }
      }
      default:
        console.log(`[mothman] unknown primitive ${name}`)
        return timed(0.5)
    }
  }
}

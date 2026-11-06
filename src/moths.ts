import { engine, Entity, Transform, MeshRenderer, Material, MaterialTransparencyMode, VisibilityComponent, AudioSource } from '@dcl/sdk/ecs'
import { Vector3, Color3, Color4, Quaternion } from '@dcl/sdk/math'
import { flashlight, cameraRay } from './flashlight'
import { setLoop } from './audio'

/**
 * Moths in the beam. They are the truth from minute one: they orbit the lit cone, stall, fall, and leave in a
 * straight line the moment the light goes out. After a long-held beam, one at a time drops into the circle of light.
 */
type State = 'hidden' | 'in' | 'out' | 'drop'
type Moth = {
  e: Entity
  state: State
  theta: number
  omega: number
  r: number
  depth: number
  seed: number
  t: number
  stall: number
  pos: Vector3
  vel: Vector3
  prev: Vector3
  dir: Vector3 // smoothed direction of travel: the sprite's head points this way
  flap: number // wing phase; the sprite rolls about its travel axis with it
}

export const moths = { active: 0, dropped: 0 }
/** The litter of dropped moths goes under the ground on a reset; the pool entities are reused from there. */
export function resetMoths() {
  for (const e of dead) Transform.getMutable(e).position = Vector3.create(0, -5, 0)
  deadIndex = 0
  moths.dropped = 0
  dropClock = 0
}

const POOL = 12
const DEAD_POOL = 24
const pool: Moth[] = []
const dead: Entity[] = []
let deadIndex = 0
let spawnClock = 0
let dropClock = 0
let flutter: Entity
let flutterAnchor: Entity

const mothColor = Color4.create(1, 1, 1, 1)
const MOTH_TEX = 'assets/images/moth.png'
function mothMaterial(e: Entity, emissive: number) {
  Material.setPbrMaterial(e, {
    texture: Material.Texture.Common({ src: MOTH_TEX }),
    alphaTexture: Material.Texture.Common({ src: MOTH_TEX }),
    transparencyMode: MaterialTransparencyMode.MTM_ALPHA_BLEND,
    albedoColor: mothColor,
    emissiveColor: Color3.create(0.5, 0.45, 0.35),
    emissiveTexture: Material.Texture.Common({ src: MOTH_TEX }),
    emissiveIntensity: emissive,
    roughness: 1,
    metallic: 0
  })
}

function makeMoth(i: number): Moth {
  const e = engine.addEntity()
  Transform.create(e, { position: Vector3.create(0, -5, 0), scale: Vector3.create(0.12, 0.12, 0.12) })
  MeshRenderer.setPlane(e)
  mothMaterial(e, 0.4)
  VisibilityComponent.create(e, { visible: false })
  return {
    e,
    state: 'hidden',
    theta: Math.random() * Math.PI * 2,
    omega: (Math.random() < 0.5 ? -1 : 1) * (2.6 + Math.random() * 2.4),
    r: 0.3 + Math.random() * 0.55,
    depth: 1.4 + (i / POOL) * 2.4,
    seed: Math.random() * 100,
    t: 0,
    stall: 0,
    pos: Vector3.create(0, -5, 0),
    vel: Vector3.Zero(),
    prev: Vector3.create(0, -5, 0),
    dir: Vector3.Forward(),
    flap: Math.random() * 6
  }
}

function show(m: Moth, visible: boolean) {
  const v = VisibilityComponent.getMutable(m.e)
  if (v.visible !== visible) v.visible = visible
}

/** The sprite is a moth seen from above, head up. Head along the travel direction; the body rolls with the wingbeat
 *  (a flat plane cannot flap, but a plane rolling ±60° about its own axis twelve times a second reads as one), and it
 *  banks into the orbit. A dropping moth tumbles. */
function place(m: Moth, dt: number) {
  const travel = Vector3.subtract(m.pos, m.prev)
  m.prev = Vector3.clone(m.pos)
  if (dt > 0 && Vector3.length(travel) > 0.004) m.dir = Vector3.normalize(Vector3.lerp(m.dir, Vector3.normalize(travel), Math.min(1, dt * 7)))
  m.flap += dt * (m.state === 'drop' ? 7 : 11 + 3 * Math.sin(m.seed))
  let roll = 60 * Math.sin(m.flap)
  if (m.state === 'in') roll += 28 * Math.sign(m.omega)
  if (m.state === 'drop') roll += m.t * 540
  let normal = Vector3.cross(m.dir, Vector3.cross(Vector3.Up(), m.dir)) // "up" for a level flyer
  if (Vector3.length(normal) < 0.01) normal = Vector3.Forward()
  normal = Vector3.rotate(Vector3.normalize(normal), Quaternion.fromAngleAxis(roll, m.dir))
  const t = Transform.getMutable(m.e)
  t.position = m.pos
  t.rotation = Quaternion.lookRotation(normal, m.dir) // local +z = sprite normal, local +y (the head) = travel
  // the beat itself: the wings close toward the body and open again (the sprite's width), twice per roll cycle
  const spread = m.state === 'drop' ? 0.55 : 0.3 + 0.7 * Math.abs(Math.cos(m.flap))
  t.scale = Vector3.create(0.12 * spread, 0.12, 0.12)
}

function layDead(p: Vector3) {
  let e: Entity
  if (dead.length < DEAD_POOL) {
    e = engine.addEntity()
    Transform.create(e, { position: p, scale: Vector3.create(0.16, 0.16, 0.16), rotation: Quaternion.fromEulerDegrees(90, Math.random() * 360, 0) })
    MeshRenderer.setPlane(e)
    mothMaterial(e, 0.15)
    dead.push(e)
  } else {
    e = dead[deadIndex % DEAD_POOL]
    deadIndex++
    Transform.getMutable(e).position = p
  }
  moths.dropped++
}

export function setupMoths() {
  for (let i = 0; i < POOL; i++) pool.push(makeMoth(i))
  flutterAnchor = engine.addEntity()
  Transform.create(flutterAnchor, { position: Vector3.create(8, 1.5, 8) })
  flutter = engine.addEntity()
  Transform.create(flutter, { parent: flutterAnchor })
  AudioSource.create(flutter, { audioClipUrl: 'assets/audio/flutter.ogg', loop: true, playing: false, volume: 0.35 })
  engine.addSystem(mothSystem)
}

function mothSystem(dt: number) {
  const { origin, forward } = cameraRay()
  const up = Vector3.Up()
  let u = Vector3.cross(forward, up)
  if (Vector3.length(u) < 0.01) u = Vector3.Right()
  u = Vector3.normalize(u)
  const v = Vector3.normalize(Vector3.cross(u, forward))
  const on = flashlight.on

  // spawn / release
  spawnClock += dt
  const wanted = on ? Math.min(6, Math.floor(1 + flashlight.litFor * 0.2)) : 0 // one at first, three after 10 s, six at most
  let active = 0
  for (const m of pool) if (m.state === 'in' || m.state === 'drop') active++
  if (on && active < wanted && spawnClock > 1.1) {
    const m = pool.find((x) => x.state === 'hidden')
    if (m !== undefined) {
      m.state = 'in'
      m.t = 0
      m.theta = Math.random() * Math.PI * 2
      // enter from the dark, a little outside the ring
      m.pos = Vector3.add(Vector3.add(origin, Vector3.scale(forward, m.depth)), Vector3.scale(u, 1.6 * (Math.random() < 0.5 ? -1 : 1)))
      m.prev = Vector3.clone(m.pos)
      show(m, true)
      spawnClock = 0
    }
  }
  if (!on) {
    for (const m of pool) {
      if (m.state === 'in' || m.state === 'drop') {
        // straight away, along the tangent, out of the cone
        const tangent = Vector3.add(Vector3.scale(u, -Math.sin(m.theta)), Vector3.scale(v, Math.cos(m.theta)))
        m.vel = Vector3.add(Vector3.scale(Vector3.normalize(tangent), 2.8 * Math.sign(m.omega)), Vector3.create(0, 0.6 + Math.random() * 0.6, 0))
        m.state = 'out'
        m.t = 0
      }
    }
  }
  // drops: after a long-held beam, one moth every few seconds spirals into the circle of light
  dropClock += dt
  if (on && flashlight.litFor > 15 && dropClock > 5.5) {
    const m = pool.find((x) => x.state === 'in' && x.t > 2)
    if (m !== undefined) {
      m.state = 'drop'
      m.t = 0
      dropClock = 0
    }
  }

  for (const m of pool) {
    if (m.state === 'hidden') continue
    m.t += dt
    if (m.state === 'in' || m.state === 'drop') {
      m.theta += m.omega * dt
      const center = Vector3.add(origin, Vector3.scale(forward, m.depth + 0.25 * Math.sin(m.t * 0.7 + m.seed)))
      let r = m.r + 0.08 * Math.sin(m.t * 1.3 + m.seed)
      let y = 0.06 * Math.sin(m.t * 5.1 + m.seed)
      if (m.state === 'in') {
        // occasional stall: a steep climb away from the lamp that collapses back onto it
        if (m.stall <= 0 && Math.random() < dt * 0.12) m.stall = 1.2
        if (m.stall > 0) {
          m.stall -= dt
          const s = m.stall / 1.2
          y += 0.7 * Math.sin(s * Math.PI)
        }
      } else {
        // spiral down into the circle of light
        r *= Math.max(0.15, 1 - m.t * 0.35)
        y -= m.t * m.t * 0.35
      }
      const ring = Vector3.add(Vector3.scale(u, r * Math.cos(m.theta)), Vector3.scale(v, r * Math.sin(m.theta)))
      const target = Vector3.add(Vector3.add(center, ring), Vector3.create(0, y, 0))
      // smooth follow with a little jitter: the flutter
      m.pos = Vector3.lerp(m.pos, target, Math.min(1, dt * 9))
      m.pos = Vector3.add(m.pos, Vector3.create((Math.random() - 0.5) * 0.03, (Math.random() - 0.5) * 0.03, (Math.random() - 0.5) * 0.03))
      if (m.state === 'drop' && m.pos.y <= 0.03) {
        layDead(Vector3.create(m.pos.x, 0.012, m.pos.z))
        m.state = 'hidden'
        show(m, false)
        m.pos = Vector3.create(0, -5, 0)
      }
      place(m, dt)
    } else if (m.state === 'out') {
      m.pos = Vector3.add(m.pos, Vector3.scale(m.vel, dt))
      place(m, dt)
      if (m.t > 1.4) {
        m.state = 'hidden'
        show(m, false)
        m.pos = Vector3.create(0, -5, 0)
      }
    }
  }

  moths.active = active
  if (active > 0) Transform.getMutable(flutterAnchor).position = Vector3.add(origin, Vector3.scale(forward, 1.8))
  setLoop(flutter, active > 0)
}

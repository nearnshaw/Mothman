import { engine, Entity, Transform, Material, MeshRenderer, LightSource, AudioSource, pointerEventsSystem, InputAction, Tween, EasingFunction } from '@dcl/sdk/ecs'
import { Vector3, Color3, Color4, Quaternion } from '@dcl/sdk/math'
import { layout } from './layout'
import { setLoop, frames } from './audio'
import { showCaption, docOpenFor } from './telepathy'
import { CAPTIONS } from './script'
import { onReset } from './game'

/**
 * The gatehouse cabin: the one safe-looking place. Its bulb is a light like any other. Inside with the bulb on, he
 * comes to the windows, then the door, then in. Turn the bulb off (the switch by the door) and he loses the place.
 */
export const cabin = {
  inside: false,
  lampOn: true,
  lampOnFor: 0, // seconds the bulb has been on with the player inside
  lampFlicker: 0,
  doorOpen: false,
  forceOpen: false, // he opens it
  visits: 0, // times the player has come in
  windowCaptionVisit: 0, // the visit during which 'Something is at the window.' was already shown
  warned: false
}

let hinge: Entity | null = null
let bulb: Entity | null = null
let light: Entity
let porch: Entity
let porchBulb: Entity
let glass: Entity[] = []
let buzz: Entity
let sfx: Entity
let lastIntensity = -1
let clock = 0
let settling = 0 // frames after a reset during which the player's position is not trusted (the teleport lands)
const LAMP = 11000
const PORCH = 2600 // the lamp over the door, on the same circuit: the beacon from the road (owner pass 10)

export function setupCabin() {
  const c = layout.cabin
  light = engine.addEntity()
  Transform.create(light, { position: Vector3.create(c.bulb.x, c.bulb.y - 0.1, c.bulb.z) })
  LightSource.create(light, { type: LightSource.Type.Point({}), color: Color3.create(1, 0.9, 0.7), intensity: LAMP, range: 15, shadow: false, active: true })
  // The lamp over the door (the model is Cabin: lamp outside, placed by the generator): a warm point light and a bulb
  // that glows, so the lit cabin reads from the dead dog's spot on the road, 12 m off in the dark.
  porch = engine.addEntity()
  Transform.create(porch, { position: Vector3.create(c.door.x + 1.1, 1.75, c.door.z - 0.5) })
  LightSource.create(porch, { type: LightSource.Type.Point({}), color: Color3.create(1, 0.78, 0.5), intensity: PORCH, range: 16, shadow: false, active: true })
  porchBulb = engine.addEntity()
  Transform.create(porchBulb, { position: Vector3.create(c.door.x + 1.1, 1.82, c.door.z - 0.38), scale: Vector3.create(0.09, 0.11, 0.09) })
  MeshRenderer.setSphere(porchBulb)
  Material.setPbrMaterial(porchBulb, { albedoColor: Color4.create(1, 0.9, 0.7, 1), emissiveColor: Color3.create(1, 0.8, 0.55), emissiveIntensity: 5, roughness: 0.3, metallic: 0 })
  buzz = engine.addEntity()
  Transform.create(buzz, { position: Vector3.create(c.bulb.x, c.bulb.y, c.bulb.z) })
  AudioSource.create(buzz, { audioClipUrl: 'assets/audio/buzz.ogg', loop: true, playing: true, volume: 0.35 })
  sfx = engine.addEntity()
  Transform.create(sfx, { position: Vector3.create(c.door.x, 1.2, c.door.z) })
  AudioSource.create(sfx, { audioClipUrl: 'assets/audio/door.ogg', playing: false, volume: 0.9 })

  let tries = 0
  engine.addSystem(function findCabin() {
    tries++
    if (hinge === null) {
      const h = engine.getEntityOrNullByName('Cabin: door hinge')
      const door = engine.getEntityOrNullByName('Cabin: door')
      if (h !== null && door !== null) {
        hinge = h
        pointerEventsSystem.onPointerDown({ entity: door, opts: { button: InputAction.IA_PRIMARY, hoverText: 'Door', maxDistance: 3.5 } }, () => setDoor(!cabin.doorOpen))
      }
    }
    if (glass.length === 0) {
      // the four panes glow warm while the bulb is on: lit windows are what a cabin in the dark looks like from the road
      const panes = ['F', 'B', 'L', 'R'].map((s) => engine.getEntityOrNullByName(`Cabin: glass ${s}`))
      if (panes.every((e) => e !== null)) glass = panes as Entity[]
    }
    if (bulb === null) {
      const b = engine.getEntityOrNullByName('Cabin: bulb')
      const sw = engine.getEntityOrNullByName('Cabin: switch')
      if (b !== null && sw !== null) {
        bulb = b
        pointerEventsSystem.onPointerDown({ entity: sw, opts: { button: InputAction.IA_PRIMARY, hoverText: 'Light switch', maxDistance: 3 } }, () => {
          setLamp(!cabin.lampOn)
          AudioSource.playSound(sfx, 'assets/audio/switch.ogg')
        })
      }
    }
    if ((hinge !== null && bulb !== null && glass.length === 4) || tries > 600) engine.removeSystem(findCabin)
  })
  engine.addSystem(cabinSystem)
  onReset(() => {
    setDoor(false)
    Object.assign(cabin, { inside: false, lampOn: true, lampOnFor: 0, lampFlicker: 0, forceOpen: false, visits: 0, windowCaptionVisit: 0, warned: false })
    settling = 30
  })
}

export function setDoor(open: boolean) {
  if (hinge === null || open === cabin.doorOpen) return
  cabin.doorOpen = open
  const from = Transform.get(hinge).rotation
  Tween.createOrReplace(hinge, {
    mode: Tween.Mode.Rotate({ start: from, end: Quaternion.fromEulerDegrees(0, open ? -100 : 0, 0) }),
    duration: open ? 1100 : 900,
    easingFunction: EasingFunction.EF_EASEOUTQUAD
  })
  AudioSource.playSound(sfx, 'assets/audio/door.ogg')
}

/** The dim half of the bulb's flicker cycle: the flashlight can blink in step with it. */
export function lampDim(): boolean { return Math.floor(clock * 3) % 2 === 1 }

export function setLamp(on: boolean) {
  if (on === cabin.lampOn) return
  cabin.lampOn = on
  if (!on) cabin.lampOnFor = 0
}

function cabinSystem(dt: number) {
  if (frames.n < 2) return // the bulb's buzz must not start on the first frame
  clock += dt
  const c = layout.cabin
  const p = Transform.get(engine.PlayerEntity).position
  const inside = Math.abs(p.x - c.x) < c.w / 2 - 0.1 && Math.abs(p.z - c.z) < c.d / 2 - 0.1 && p.y < c.h
  if (settling > 0) settling--
  else if (inside !== cabin.inside) {
    cabin.inside = inside
    if (inside) {
      cabin.visits++
      if (cabin.visits === 1) showCaption(CAPTIONS.cabinFirst, 1, 6)
    }
  }
  if (cabin.forceOpen) { cabin.forceOpen = false; setDoor(true) }
  if (cabin.lampOn && inside && docOpenFor() < 0) cabin.lampOnFor += dt // reading under the bulb: the clock waits
  if (cabin.lampFlicker > 0) cabin.lampFlicker -= dt
  if (cabin.lampOnFor > 26 && !cabin.warned && cabin.lampOn) {
    cabin.warned = true
    showCaption(CAPTIONS.notTheDoor, 0, 6)
  }

  let intensity = cabin.lampOn ? LAMP : 0
  if (cabin.lampOn && cabin.lampFlicker > 0) intensity = Math.floor(clock * 3) % 2 === 0 ? LAMP : LAMP * 0.25
  if (intensity !== lastIntensity) {
    lastIntensity = intensity
    const l = LightSource.getMutable(light)
    l.active = intensity > 0
    l.intensity = intensity
    if (bulb !== null) {
      const m = Material.getMutableOrNull(bulb)
      if (m !== null && m.material?.$case === 'pbr') m.material.pbr.emissiveIntensity = intensity > 0 ? (intensity === LAMP ? 4 : 1) : 0
    }
    // the porch lamp and the window panes follow the bulb, flicker included: one circuit
    const k = intensity / LAMP
    const pl = LightSource.getMutable(porch)
    pl.active = k > 0
    pl.intensity = PORCH * k
    const pm = Material.getMutable(porchBulb)
    if (pm.material?.$case === 'pbr') pm.material.pbr.emissiveIntensity = 5 * k
    for (const g of glass) {
      const gm = Material.getMutableOrNull(g)
      if (gm !== null && gm.material?.$case === 'pbr') { gm.material.pbr.emissiveColor = Color3.create(1, 0.82, 0.55); gm.material.pbr.emissiveIntensity = 1.2 * k }
    }
    setLoop(buzz, intensity > 0)
  }
}

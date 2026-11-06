import { engine, Entity, Transform, Material, LightSource, AudioSource, pointerEventsSystem, InputAction, Tween, EasingFunction } from '@dcl/sdk/ecs'
import { Vector3, Color3, Quaternion } from '@dcl/sdk/math'
import { layout } from './layout'
import { setLoop, frames } from './audio'
import { showCaption } from './telepathy'
import { CAPTIONS } from './script'

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
let buzz: Entity
let sfx: Entity
let lastIntensity = -1
let clock = 0
const LAMP = 9000

export function setupCabin() {
  const c = layout.cabin
  light = engine.addEntity()
  Transform.create(light, { position: Vector3.create(c.bulb.x, c.bulb.y - 0.1, c.bulb.z) })
  LightSource.create(light, { type: LightSource.Type.Point({}), color: Color3.create(1, 0.9, 0.7), intensity: LAMP, range: 11, shadow: false, active: true })
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
    if ((hinge !== null && bulb !== null) || tries > 600) engine.removeSystem(findCabin)
  })
  engine.addSystem(cabinSystem)
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
  if (inside !== cabin.inside) {
    cabin.inside = inside
    if (inside) {
      cabin.visits++
      if (cabin.visits === 1) showCaption(CAPTIONS.cabinFirst, 1, 6)
    }
  }
  if (cabin.forceOpen) { cabin.forceOpen = false; setDoor(true) }
  if (cabin.lampOn && inside) cabin.lampOnFor += dt
  if (cabin.lampFlicker > 0) cabin.lampFlicker -= dt
  if (cabin.lampOnFor > 42 && !cabin.warned && cabin.lampOn) {
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
    setLoop(buzz, intensity > 0)
  }
}

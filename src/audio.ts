import { engine, Entity, Transform, AudioSource } from '@dcl/sdk/ecs'
import { Vector3 } from '@dcl/sdk/math'

export function loopSound(parent: Entity | null, url: string, volume: number, global = false): Entity {
  const e = engine.addEntity()
  Transform.create(e, parent === null ? { position: Vector3.create(8, 2, 8) } : { parent })
  AudioSource.create(e, { audioClipUrl: url, loop: true, playing: false, volume, global })
  return e
}

/** Write `playing` only when it changes (LWW dedup makes repeated identical writes pointless). */
export function setLoop(e: Entity, playing: boolean) {
  const a = AudioSource.getMutableOrNull(e)
  if (a !== null && a.playing !== playing) a.playing = playing
}

/** Frames since the scene started. No loop may play before frame 2 (owner: a sound on the first frame cannot be muted in the editor). */
export const frames = { n: 0 }

/** Wind under everything, and a forest bed: crickets, gusts, an owl, a creaking trunk. */
export function setupAmbience() {
  const wind = loopSound(null, 'assets/audio/wind.ogg', 0.3, true)
  const forest = loopSound(null, 'assets/audio/forest.ogg', 0.5, true)
  engine.addSystem(() => {
    frames.n++
    if (frames.n === 2) { setLoop(wind, true); setLoop(forest, true) }
  }, 1000) // high priority: runs first, so every other system sees the frame count
}

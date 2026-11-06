import { engine, Entity, Transform, AudioSource, GltfContainer, GltfNodeModifiers, Animator, VisibilityComponent } from '@dcl/sdk/ecs'
import { Vector3, Color3, Color4 } from '@dcl/sdk/math'
import { MOTHMAN_CLIPS, MOTHMAN_EYES_PATH, MOTHMAN_MODEL_SCALE, MothmanClip } from './animations'

/** Animated Tripo rig. Native height 0.9804 m, +Z forward; 2.5× gives a 2.45 m creature.
 * Eye faces are skinned inside the GLB, so eyeshine follows the animated head. */
export type MothmanBody = {
  root: Entity
  model: Entity
  hum: Entity
  oneShot: Entity
  cue: Entity
  wings: Entity
  eyePos: () => Vector3
  setEyes: (intensity: number) => void
  setClip: (clip: MothmanClip, restart?: boolean) => void
  currentClip: () => MothmanClip
  updateAnimation: (dt: number) => void
  clipFinished: (clip: MothmanClip) => boolean
  setVisible: (visible: boolean) => void
}

export function createMothmanBody(at: Vector3): MothmanBody {
  const root = engine.addEntity()
  Transform.create(root, { position: at })
  const model = engine.addEntity()
  Transform.create(model, { parent: root, scale: Vector3.create(MOTHMAN_MODEL_SCALE, MOTHMAN_MODEL_SCALE, MOTHMAN_MODEL_SCALE) })
  GltfContainer.create(model, { src: 'assets/Models/mothman-skeleton.glb', visibleMeshesCollisionMask: 0, invisibleMeshesCollisionMask: 0 })
  Animator.create(model, {
    states: (Object.keys(MOTHMAN_CLIPS) as MothmanClip[]).map((clip) => ({
      clip, playing: clip === 'idle_ground', loop: MOTHMAN_CLIPS[clip].loop,
      speed: 1, weight: clip === 'idle_ground' ? 1 : 0, shouldReset: true
    }))
  })

  const sound = (path: string, height: number, volume: number, loop = false) => {
    const entity = engine.addEntity()
    Transform.create(entity, { parent: root, position: Vector3.create(0, height, 0) })
    AudioSource.create(entity, { audioClipUrl: path, loop, playing: false, volume })
    return entity
  }
  const hum = sound('assets/audio/hum.ogg', 1.5, 0.9, true)
  const oneShot = sound('assets/audio/screech.ogg', 2.0, 1)
  const cue = sound('assets/audio/call.ogg', 2.0, 0.9)
  const wings = sound('assets/audio/wingbeat.ogg', 1.8, 0.8)

  let lastEyes = -1
  let lastClip: MothmanClip = 'idle_ground'
  let lastVisible: boolean | null = null
  let fade: { elapsed: number; weights: number[] } | null = null
  const fadeDuration = 0.18
  VisibilityComponent.create(model, { visible: false })
  const result: MothmanBody = {
    root, model, hum, oneShot, cue, wings,
    eyePos: () => Vector3.add(Transform.get(root).position, Vector3.create(0, 2.05, 0)),
    setEyes: (intensity) => {
      const q = Math.round(intensity * 20) / 20
      if (q === lastEyes) return
      lastEyes = q
      GltfNodeModifiers.createOrReplace(model, { modifiers: [{
        path: MOTHMAN_EYES_PATH,
        material: { material: { $case: 'pbr', pbr: {
          albedoColor: Color4.create(0.3, 0.006, 0.008, 1),
          emissiveColor: Color3.create(1, 0.015, 0.008), emissiveIntensity: q,
          roughness: 0.3, metallic: 0
        } } }
      }] })
    },
    setClip: (clip, restart = false) => {
      if (clip === lastClip && !restart) return
      const states = Animator.getMutable(model).states
      const weights = states.map((state) => state.playing ? state.weight ?? 0 : 0)
      const target = states.find((state) => state.clip === clip)!
      // Stopping/restarting is explicit for one-shots, including consecutive screeches or bangs.
      if (clip === lastClip) {
        Animator.playSingleAnimation(model, clip, true)
        target.weight = 1
        fade = null
      } else {
        target.playing = true
        target.shouldReset = true
        target.weight = weights[states.indexOf(target)] ?? 0
        fade = { elapsed: 0, weights }
      }
      lastClip = clip
    },
    currentClip: () => lastClip,
    clipFinished: (clip) => lastClip === clip && Animator.get(model).states.some((state) => state.clip === clip && state.playing === false),
    updateAnimation: (dt) => {
      if (fade === null) return
      fade.elapsed += dt
      const t = Math.min(1, fade.elapsed / fadeDuration)
      const states = Animator.getMutable(model).states
      for (let i = 0; i < states.length; i++) {
        const state = states[i]
        const target = state.clip === lastClip
        state.weight = (fade.weights[i] ?? 0) * (1 - t) + (target ? t : 0)
        if (t >= 1 && !target) { state.playing = false; state.shouldReset = true }
      }
      if (t >= 1) fade = null
    },
    setVisible: (visible) => {
      if (visible === lastVisible) return
      lastVisible = visible
      VisibilityComponent.getMutable(model).visible = visible
    }
  }
  result.setEyes(0)
  return result
}

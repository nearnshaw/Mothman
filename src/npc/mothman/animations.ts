/** Exported clip contract. Durations are seconds; movement remains owned by the host. */
export const MOTHMAN_CLIPS = {
  idle_fly: { duration: 3.2, loop: true },
  idle_fly_watch: { duration: 4.8, loop: true },
  hover_menacing: { duration: 2.4, loop: true },
  fly_menacing: { duration: 1.6, loop: true },
  land: { duration: 1.4, loop: false },
  idle_ground: { duration: 4.0, loop: true },
  takeoff: { duration: 0.8, loop: false },
  glide_retreat: { duration: 2.4, loop: true },
  screech: { duration: 1.9, loop: false },
  lunge: { duration: 1.3, loop: false },
  ground_loom: { duration: 4.0, loop: true },
  telepathy: { duration: 6.0, loop: true },
  window_stare: { duration: 4.0, loop: true },
  door_bang: { duration: 2.4, loop: false },
  enter_glide: { duration: 2.4, loop: true },
} as const

export type MothmanClip = keyof typeof MOTHMAN_CLIPS

export const MOTHMAN_MODEL_SCALE = 2.5
export const MOTHMAN_EYES_PATH = 'Node_0/node_0/Armature/BoneRoot/Hip/MothmanEyes'

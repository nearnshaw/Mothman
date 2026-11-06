import { OBJECTIVES } from './script'

/** The one line in the corner that says what you are doing. Set by story events; read by hud.tsx. Words: src/script.ts. */
export const objective = { text: OBJECTIVES.start[0], sub: OBJECTIVES.start[1], changedAt: 0 }

let clock = 0
export function setObjective(text: string, sub = '') {
  if (objective.text === text && objective.sub === sub) return
  objective.text = text
  objective.sub = sub
  objective.changedAt = clock
}
export function objectiveClock(dt: number) { clock += dt }
export function objectiveAge() { return clock - objective.changedAt }

import { engine } from '@dcl/sdk/ecs'
import { VOICE } from './script'

/** What the HUD shows. Driven here, read by hud.tsx. */
export const hud = {
  line: '',
  lineAlpha: 0,
  caption: '',
  captionAlpha: 0,
  hint: '',
  hintAlpha: 0,
  stickyHint: '' as string, // shown with a slow pulse until cleared
  doc: '',
  docAlpha: 0,
  docOpen: false, // a document stays open until the player closes it (E or the button)
  docOpenedAt: 0,
  black: 0, // full-screen black overlay alpha (death, ending)
  deathText: '',
  deathAlpha: 0
}

export function showDocument(text: string) {
  hud.doc = text
  hud.docOpen = true
  hud.docOpenedAt = clock
}
export function closeDocument() {
  hud.docOpen = false
}
export function docOpenFor(): number {
  return hud.docOpen ? clock - hud.docOpenedAt : -1
}

/** The passage, in his voice, inside the player's head, while the moths circle the beam. GDD §10. Words: src/script.ts. */
const LINES = VOICE
const GAP = 0.9
const FADE_IN = 0.9
const FADE_OUT = 0.7
/** Seconds a line stays up: about three words a second, plus the fades, never under four seconds. */
const holdFor = (line: string) => Math.max(4.0, 1.6 + line.split(/\s+/).length * 0.34)
const STARTS: number[] = []
let total = 0
for (const l of LINES) { STARTS.push(total); total += holdFor(l) + GAP }

export const telepathy = { active: false, done: false, t: 0 }

export function startTelepathy() {
  telepathy.active = true
  telepathy.done = false
  telepathy.t = 0
}

type Timed = { text: string; start: number; hold: number; key: 'caption' | 'hint' }
const queue: Timed[] = []
let clock = 0

export function showCaption(text: string, delay: number, hold: number) {
  queue.push({ text, start: clock + delay, hold, key: 'caption' })
}
/** Seconds until every queued caption has finished (0 when the slot is free). */
export function captionsPending(): number {
  let end = clock
  for (const q of queue) if (q.key === 'caption') end = Math.max(end, q.start + q.hold)
  return end - clock
}
export function showHint(text: string, delay: number, hold: number) {
  queue.push({ text, start: clock + delay, hold, key: 'hint' })
}

export function setupTelepathy() {
  engine.addSystem((dt) => {
    clock += dt
    hud.captionAlpha = 0
    hud.hintAlpha = 0
    for (const q of queue) {
      const t = clock - q.start
      if (t < 0 || t > q.hold) continue
      const a = Math.min(1, t / 1.2, (q.hold - t) / 1.2)
      if (q.key === 'caption') { hud.caption = q.text; hud.captionAlpha = Math.max(hud.captionAlpha, a) }
      else { hud.hint = q.text; hud.hintAlpha = Math.max(hud.hintAlpha, a) }
    }
    if (hud.stickyHint !== '') {
      hud.hint = hud.stickyHint
      hud.hintAlpha = 0.55 + 0.45 * Math.sin(clock * 2.2)
    }
    hud.docAlpha = hud.docOpen ? Math.min(1, hud.docAlpha + dt * 2.5) : Math.max(0, hud.docAlpha - dt * 3)
    if (!telepathy.active) { hud.lineAlpha = 0; return }
    telepathy.t += dt
    if (telepathy.t >= total) {
      hud.lineAlpha = 0
      if (telepathy.t > total + 2.5) { telepathy.active = false; telepathy.done = true }
      return
    }
    let i = 0
    while (i + 1 < LINES.length && telepathy.t >= STARTS[i + 1]) i++
    const local = telepathy.t - STARTS[i]
    const hold = holdFor(LINES[i])
    hud.line = LINES[i]
    hud.lineAlpha = local > hold ? 0 : Math.min(1, local / FADE_IN, (hold - local) / FADE_OUT)
  })
}

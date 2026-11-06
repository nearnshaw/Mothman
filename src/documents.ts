import { engine, Entity, Transform, pointerEventsSystem, InputAction, AudioSource, inputSystem, PointerEventType } from '@dcl/sdk/ecs'
import { showDocument, closeDocument, docOpenFor, showCaption, captionsPending } from './telepathy'
import { story } from './npc/mothman/host'
import { setObjective } from './objectives'
import { PAGES, OBJECTIVES, Page } from './script'
import { onReset } from './game'
import { Vector3 } from '@dcl/sdk/math'

/**
 * Things left in the woods that can be read. Each is a prop placed by scripts/gen-forest.py and named
 * "Document: <key>". Reading one opens its text; it stays open until the player puts it down (E or Close).
 * The words are in src/script.ts (PAGES). This file only wires them to the props and to the story.
 *
 * The page shows only what is written or what is in front of you. What you make of it (`after`) comes as captions
 * once you put the page down, so the paper and the narrator never share a sheet (owner pass 5).
 */
type Doc = Page & { onRead?: () => void; readOnce?: boolean }
/** What reading a page does to the story, by key. */
const HOOKS: Record<string, () => void> = {
  map: () => setObjective(...OBJECTIVES.map),
  tally: () => setObjective(...OBJECTIVES.tally),
  tags: () => setObjective(...OBJECTIVES.tags),
  collar: () => {
    story.collar = true
    setObjective(...OBJECTIVES.collar)
  }
}
const TEXTS: Record<string, Doc> = {}
for (const key of Object.keys(PAGES)) TEXTS[key] = { ...PAGES[key], onRead: HOOKS[key] }

/** Lines said once the page is down, one after another, each held long enough to read. */
let pendingAfter: string[] | null = null
function sayAfter(lines: string[]) {
  let at = 0.8 + Math.max(0, captionsPending())
  for (const l of lines) {
    const hold = Math.max(3.5, 1.4 + l.split(/\s+/).length * 0.32)
    showCaption(l, at, hold)
    at += hold + 0.4
  }
}

export const documents = { read: 0, total: 0 }
let pageSound: Entity
/** Props taken when read (the collar): sunk 50 m under their spot until the next reset. */
const taken: Array<{ e: Entity; key: string; at: Vector3 }> = []

function wire(e: Entity, key: string, counted: boolean) {
  const doc = TEXTS[key]
  if (doc === undefined) return
  if (counted) documents.total++
  pointerEventsSystem.onPointerDown(
    { entity: e, opts: { button: InputAction.IA_PRIMARY, hoverText: doc.hover, maxDistance: doc.reach ?? 4 } },
    () => {
      if (docOpenFor() >= 0) return
      if (!doc.readOnce) { doc.readOnce = true; documents.read++ }
      pendingAfter = doc.after ?? null
      showDocument(doc.text, doc.style ?? 'look', doc.note ?? '', doc.ink ?? 'ballpoint')
      AudioSource.playSound(pageSound, 'assets/audio/page.ogg')
      doc.onRead?.()
      if (doc.remove) {
        pointerEventsSystem.removeOnPointerDown(e)
        const t = Transform.getMutable(e)
        taken.push({ e, key, at: Vector3.clone(t.position) })
        t.position = Vector3.add(t.position, Vector3.create(0, -50, 0))
      }
    }
  )
}

export function setupDocuments() {
  pageSound = engine.addEntity()
  Transform.create(pageSound, { parent: engine.CameraEntity })
  AudioSource.create(pageSound, { audioClipUrl: 'assets/audio/page.ogg', playing: false, volume: 0.7 })
  // A text can be spread over several props: "Document: tally", "Document: tally 2", ... all open the same page.
  const pending = new Set(Object.keys(TEXTS))
  let tries = 0
  engine.addSystem(function findDocs() {
    tries++
    for (const key of Array.from(pending)) {
      const e = engine.getEntityOrNullByName(`Document: ${key}`)
      if (e === null) continue
      wire(e, key, true)
      for (let n = 2; n < 16; n++) {
        const more = engine.getEntityOrNullByName(`Document: ${key} ${n}`)
        if (more === null) break
        wire(more, key, false)
      }
      pending.delete(key)
    }
    if (pending.size === 0 || tries > 600) engine.removeSystem(findDocs)
  })
  onReset(() => {
    pendingAfter = null
    documents.read = 0
    for (const doc of Object.values(TEXTS)) doc.readOnce = false
    for (const { e, key, at } of taken) {
      Transform.getMutable(e).position = at
      wire(e, key, false)
    }
    taken.length = 0
  })
  let wasOpen = false
  engine.addSystem(() => {
    const open = docOpenFor()
    if (open > 0.5 && inputSystem.isTriggered(InputAction.IA_PRIMARY, PointerEventType.PET_DOWN)) {
      closeDocument()
      AudioSource.playSound(pageSound, 'assets/audio/page.ogg')
    }
    const isOpen = open >= 0
    if (wasOpen && !isOpen && pendingAfter !== null) { sayAfter(pendingAfter); pendingAfter = null }
    wasOpen = isOpen
  })
}

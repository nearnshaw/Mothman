import { engine, Entity, Transform, pointerEventsSystem, InputAction, AudioSource, inputSystem, PointerEventType, MeshRenderer, Material, MaterialTransparencyMode } from '@dcl/sdk/ecs'
import { showDocument, closeDocument, docOpenFor, showCaption, captionsPending } from './telepathy'
import { story } from './npc/mothman/host'
import { setObjective } from './objectives'
import { PAGES, OBJECTIVES, Page } from './script'
import { onReset } from './game'
import { Vector3, Quaternion, Color4 } from '@dcl/sdk/math'

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

/** A monologue page said as captions: one line per sentence or two, short sentences joined to the one before. */
function monologueLines(text: string): string[] {
  const out: string[] = []
  for (const para of text.split('\n\n')) {
    // a sentence ends at . ! or ? followed by a capital: 'RT. 62' and 'No. 7' stay whole
    const parts = para.split(/([.!?]+["”]?)\s+(?=[A-Z"“])/)
    const sentences: string[] = []
    for (let i = 0; i < parts.length; i += 2) sentences.push(parts[i] + (parts[i + 1] ?? ''))
    let first = true
    for (const raw of sentences) {
      const s = raw.trim()
      if (s === '') continue
      const words = s.split(/\s+/).length
      const last = out[out.length - 1]
      if (!first && last !== undefined && (words < 5 || last.split(/\s+/).length + words <= 12)) out[out.length - 1] = `${last} ${s}`
      else out.push(s)
      first = false
    }
  }
  return out
}

/**
 * The tag box at the centre of the collar ring is a heap of dead moths (owner pass 10: the plain box said nothing).
 * The box keeps its collider as the click target, grown to cover the heap; the heap is drawn on the bunker root.
 */
function dressTags(box: Entity) {
  const t = Transform.getMutable(box)
  const parent = t.parent
  MeshRenderer.deleteFrom(box)
  t.position = Vector3.create(t.position.x, 0.3, t.position.z)
  t.scale = Vector3.create(1.4, 0.6, 1.4)
  const at = Vector3.create(t.position.x, 0, t.position.z)
  const core = engine.addEntity()
  Transform.create(core, { parent, position: Vector3.add(at, Vector3.create(0, 0.2, 0)), scale: Vector3.create(1.0, 0.4, 1.0) })
  MeshRenderer.setCylinder(core, 0.05, 1)
  Material.setPbrMaterial(core, { albedoColor: Color4.create(0.2, 0.18, 0.14, 1), roughness: 1, metallic: 0 })
  const heap = {
    texture: Material.Texture.Common({ src: 'assets/images/mothheap.png' }),
    alphaTexture: Material.Texture.Common({ src: 'assets/images/mothheap.png' }),
    transparencyMode: MaterialTransparencyMode.MTM_ALPHA_TEST,
    alphaTest: 0.5,
    albedoColor: Color4.create(0.95, 0.92, 0.85, 1),
    roughness: 1,
    metallic: 0
  }
  let seed = 7
  const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280 }
  for (let i = 0; i < 18; i++) {
    // layers of moths from the skirt up to the crown, each a little smaller and higher, turned at random
    const k = i / 17
    const size = 2.2 * (1 - 0.8 * k) * (0.9 + 0.2 * rnd())
    const room = Math.max(0, 1.0 - size / 2 - 0.1)
    const a = rnd() * Math.PI * 2
    const e = engine.addEntity()
    Transform.create(e, {
      parent,
      position: Vector3.add(at, Vector3.create(Math.cos(a) * room * rnd(), 0.02 + 0.42 * k, Math.sin(a) * room * rnd())),
      rotation: Quaternion.fromEulerDegrees(90, rnd() * 360, 0),
      scale: Vector3.create(size, size, 1)
    })
    MeshRenderer.setPlane(e)
    Material.setPbrMaterial(e, heap)
  }
  for (let i = 0; i < 8; i++) {
    // the slope: moths lying tilted on the flank of the heap
    const a = (i / 8) * Math.PI * 2 + rnd() * 0.5
    const e = engine.addEntity()
    Transform.create(e, {
      parent,
      position: Vector3.add(at, Vector3.create(Math.cos(a) * 0.62, 0.2, Math.sin(a) * 0.62)),
      rotation: Quaternion.multiply(Quaternion.fromEulerDegrees(0, -(a * 180) / Math.PI + 90, 0), Quaternion.fromEulerDegrees(52, 0, 0)),
      scale: Vector3.create(0.9, 0.9, 1)
    })
    MeshRenderer.setPlane(e)
    Material.setPbrMaterial(e, heap)
  }
}
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
      if (doc.style === 'monologue' && captionsPending() > 0) return // still saying the last thing
      if (!doc.readOnce) { doc.readOnce = true; documents.read++ }
      if (doc.style === 'monologue') {
        // not a paper: what you make of it, said in your head, then the lines that follow
        sayAfter(monologueLines(doc.text).concat(doc.after ?? []))
      } else {
        pendingAfter = doc.after ?? null
        showDocument(doc.text, doc.style ?? 'look', doc.note ?? '', doc.ink ?? 'ballpoint')
        AudioSource.playSound(pageSound, 'assets/audio/page.ogg')
      }
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
      if (key === 'tags') dressTags(e)
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

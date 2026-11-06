import { engine, Transform } from '@dcl/sdk/ecs'
import { Vector3 } from '@dcl/sdk/math'
import { layout } from './layout'
import { docOpenFor } from './telepathy'

/**
 * Enclosed places. The bunkers are safe: he never goes in and does nothing to a player inside. He also never passes
 * through the walls or the earth mound of a bunker, or the cabin walls (he uses the door, when the story opens it).
 * Geometry mirrors scripts/gen-forest.py bunker(): a 6 x 9 x 3.2 m room with the door on its -z side, a 12 m headwall
 * at z = -4.8, and a half-ellipsoid mound behind the headwall (mound.glb scaled 6 x 3.5 x 12.5).
 */
const ROOM = { w: 6, d: 9, h: 3.2 }
const MOUND = { rx: 6, ry: 3.5, rz: 12.5 }
const BODY = 0.7 // his half-width: positions keep this far from a wall
const BUNKERS = [layout.bunkers.count, layout.bunkers.collars, layout.bunkers.roost]

/** The player is in a bunker (the room, or the doorway at its step). */
export function insideBunker(p: Vector3): boolean {
  for (const b of BUNKERS) {
    const dx = p.x - b.x, dz = p.z - b.z
    if (Math.abs(dx) < ROOM.w / 2 + 0.3 && dz > -ROOM.d / 2 - 1.0 && dz < ROOM.d / 2 && p.y < ROOM.h) return true
  }
  return false
}

/** Slack: a page is open on the screen, or the player is in a bunker. The clocks that bring him closer stop. */
export function grace(): boolean {
  return docOpenFor() >= 0 || insideBunker(Transform.get(engine.PlayerEntity).position)
}

/** Push a point out of an axis-aligned box (centre c, half sizes h, floor at y 0): the least move that clears it. */
function outOfBox(p: Vector3, cx: number, cz: number, hx: number, hz: number, top: number): Vector3 {
  const dx = p.x - cx, dz = p.z - cz
  if (Math.abs(dx) >= hx || Math.abs(dz) >= hz || p.y >= top) return p
  const px = hx - Math.abs(dx), pz = hz - Math.abs(dz), py = top - p.y
  if (px <= pz && px <= py) return Vector3.create(cx + Math.sign(dx || 1) * hx, p.y, p.z)
  if (pz <= py) return Vector3.create(p.x, p.y, cz + Math.sign(dz || 1) * hz)
  return Vector3.create(p.x, top, p.z)
}

/** Keep a point of his outside every enclosed volume. `cabinOpen`: he may be inside the cabin (!enter, !take). */
export function keepOut(p: Vector3, cabinOpen = false): Vector3 {
  let v = p
  for (const b of BUNKERS) {
    // the room with its walls and the headwall, as one box from the headwall's front to the back wall
    const front = -ROOM.d / 2 - 0.6 - BODY, back = ROOM.d / 2 + 0.3 + BODY
    v = outOfBox(v, b.x, b.z + (front + back) / 2, ROOM.w / 2 + 0.3 + BODY, (back - front) / 2, ROOM.h + 0.3 + BODY)
    // the mound: the half of the ellipsoid behind the headwall
    const dx = v.x - b.x, dz = v.z - (b.z - ROOM.d / 2)
    if (dz > 0) {
      const rx = MOUND.rx + BODY, ry = MOUND.ry + BODY, rz = MOUND.rz + BODY
      const n = Math.hypot(dx / rx, v.y / ry, dz / rz)
      if (n < 1) v = n < 0.05 ? Vector3.create(v.x, ry, v.z) : Vector3.create(b.x + dx / n, v.y / n, b.z - ROOM.d / 2 + dz / n)
    }
  }
  if (!cabinOpen) {
    const c = layout.cabin
    v = outOfBox(v, c.x, c.z, c.w / 2 + BODY, c.d / 2 + BODY, c.h + BODY)
  }
  return v
}

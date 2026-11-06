import { executeTask } from '@dcl/sdk/ecs'
import { getSceneInformation } from '~system/Runtime'
import { layout } from './layout'

/** Scene bounds in metres and the Mothman's distance bands. The generated layout is the source of truth for spots. */
export const bounds = { w: layout.size.w, d: layout.size.d, ready: false }
export const bands = { near: 2.8, mid: 9, far: 18 }

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v))

export function loadBounds() {
  executeTask(async () => {
    try {
      const info = await getSceneInformation({})
      const meta = JSON.parse(info.metadataJson)
      const parcels: string[] = meta.scene.parcels
      let minx = Infinity, maxx = -Infinity, minz = Infinity, maxz = -Infinity
      for (const p of parcels) {
        const [x, z] = p.split(',').map(Number)
        minx = Math.min(minx, x); maxx = Math.max(maxx, x); minz = Math.min(minz, z); maxz = Math.max(maxz, z)
      }
      bounds.w = (maxx - minx + 1) * 16
      bounds.d = (maxz - minz + 1) * 16
      bounds.ready = true
      const s = Math.min(bounds.w, bounds.d)
      bands.mid = clamp(s * 0.3, 4.5, 9)
      bands.far = clamp(s * 0.45, 7, 18)
      console.log(`[mothman] scene ${bounds.w}x${bounds.d} m, bands near ${bands.near} mid ${bands.mid} far ${bands.far}`)
    } catch (e) {
      console.log('[mothman] scene information unavailable, keeping layout defaults', e)
    }
  })
}

/** His roost: bunker 7, where the road ends. */
export function roostSpot() {
  return { x: layout.bunkers.roost.x, z: layout.bunkers.roost.z, top: 7.5, door: layout.bunkers.roost.door }
}

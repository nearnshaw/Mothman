import ReactEcs, { UiEntity, Label, Button } from '@dcl/sdk/react-ecs'
import { engine, executeTask } from '@dcl/sdk/ecs'
import { Color4 } from '@dcl/sdk/math'
import { getRealm } from '~system/Runtime'
import { tune } from './tune'
import { applyEnvironment } from './environment'

/**
 * TEMPORARY tuning panel, preview only (realmInfo.isPreview): sky and sun brightness, fog, the flashlight's cone and
 * brightness. Hidden behind a small "tune" button on the right edge. Remove once the values are settled into
 * src/tune.ts defaults, src/environment.ts and src/flashlight.ts.
 */
export const debug = { enabled: false, visible: false }

type Knob = { label: string; key: 'sky' | 'sun' | 'fog' | 'stars' | 'beamAngle' | 'beam'; step: number; min: number; max: number; digits: number }
const KNOBS: Knob[] = [
  { label: 'Sky / ambient', key: 'sky', step: 0.1, min: 0, max: 5, digits: 1 },
  { label: 'Sun light', key: 'sun', step: 0.1, min: 0, max: 3, digits: 1 },
  { label: 'Fog density', key: 'fog', step: 0.01, min: 0, max: 0.6, digits: 2 },
  { label: 'Stars', key: 'stars', step: 0.5, min: 0, max: 20, digits: 1 },
  { label: 'Beam angle', key: 'beamAngle', step: 4, min: 8, max: 140, digits: 0 },
  { label: 'Beam brightness', key: 'beam', step: 0.1, min: 0.1, max: 4, digits: 1 }
]
const DEFAULTS = { sky: tune.sky, sun: tune.sun, fog: tune.fog, stars: tune.stars, beamAngle: tune.beamAngle, beam: tune.beam }

function nudge(k: Knob, dir: number) {
  const v = Math.max(k.min, Math.min(k.max, tune[k.key] + dir * k.step))
  tune[k.key] = Number(v.toFixed(k.digits + 1))
  tune.dirty = true
}

export function setupDebug() {
  executeTask(async () => {
    try {
      const realm = await getRealm({})
      debug.enabled = realm.realmInfo?.isPreview === true
    } catch {
      debug.enabled = false
    }
  })
  engine.addSystem(() => {
    if (!tune.dirty) return
    tune.dirty = false
    applyEnvironment() // the flashlight reads tune.* itself, every frame
  })
}

const TEXT = Color4.create(0.9, 0.9, 0.88, 1)
const DIM = Color4.create(0.65, 0.65, 0.62, 1)

export const DebugPanel = () => {
  if (!debug.enabled) return <UiEntity uiTransform={{ width: 0, height: 0, display: 'none' }} />
  // Right edge, below the Explorer's Local Tools menu (top-right in preview); the left edge is the client's HUD.
  return (
    <UiEntity uiTransform={{ width: 440, height: 400, positionType: 'absolute', position: { top: 200, right: 40 }, flexDirection: 'column', alignItems: 'flex-end' }}>
      <Button value={debug.visible ? 'hide tuning' : 'tune'} variant="secondary" fontSize={14} uiTransform={{ width: 120, height: 30 }} onMouseDown={() => { debug.visible = !debug.visible }} />
      <UiEntity uiTransform={{ width: 440, height: 320, margin: { top: 8 }, padding: 10, flexDirection: 'column', display: debug.visible ? 'flex' : 'none' }}
        uiBackground={{ color: Color4.create(0.05, 0.05, 0.06, 0.85) }}>
        <Label value="PREVIEW TUNING  (temporary)" fontSize={13} font="sans-serif" color={DIM} uiTransform={{ width: 420, height: 22 }} />
        {KNOBS.map((k) => (
          <UiEntity key={k.key} uiTransform={{ width: 420, height: 44, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
            <Label value={k.label} fontSize={16} font="sans-serif" textAlign="middle-left" color={TEXT} uiTransform={{ width: 190, height: 40 }} />
            <Label value={tune[k.key].toFixed(k.digits)} fontSize={16} font="sans-serif" textAlign="middle-right" color={TEXT} uiTransform={{ width: 90, height: 40 }} />
            <Button value="-" variant="secondary" fontSize={18} uiTransform={{ width: 56, height: 36 }} onMouseDown={() => nudge(k, -1)} />
            <Button value="+" variant="secondary" fontSize={18} uiTransform={{ width: 56, height: 36 }} onMouseDown={() => nudge(k, 1)} />
          </UiEntity>
        ))}
        <UiEntity uiTransform={{ width: 420, height: 40, flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end' }}>
          <Button value="reset" variant="secondary" fontSize={14} uiTransform={{ width: 100, height: 32 }}
            onMouseDown={() => { Object.assign(tune, DEFAULTS); tune.dirty = true }} />
        </UiEntity>
      </UiEntity>
    </UiEntity>
  )
}

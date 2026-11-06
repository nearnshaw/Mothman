import ReactEcs, { ReactEcsRenderer, UiEntity, Label, Button } from '@dcl/sdk/react-ecs'
import { Color4 } from '@dcl/sdk/math'
import { hud, closeDocument } from './telepathy'
import { objective, objectiveAge } from './objectives'

// Coded UI (not editable in the Creator Hub UI Designer): the text content and alpha are driven per frame.
const Hud = () => {
  const age = objectiveAge()
  const pulse = age < 4 ? 0.7 + 0.3 * Math.sin(age * 6) : 0.75
  return (
    <UiEntity uiTransform={{ width: '100%', height: '100%', positionType: 'absolute', flexDirection: 'column', alignItems: 'center' }}>
      <UiEntity uiTransform={{ width: 700, height: 70, positionType: 'absolute', position: { top: 36, left: 40 }, flexDirection: 'column' }}>
        <Label value={objective.text} fontSize={20} font="serif" textAlign="top-left" color={Color4.create(0.82, 0.78, 0.7, pulse)} uiTransform={{ width: 700, height: 30 }} />
        <Label value={objective.sub} fontSize={16} font="sans-serif" textAlign="top-left" color={Color4.create(0.6, 0.6, 0.58, 0.8)} uiTransform={{ width: 700, height: 26 }} />
      </UiEntity>
      <UiEntity
        uiTransform={{ width: 1500, height: 100, positionType: 'absolute', position: { top: 200 } }}
        uiText={{ value: hud.caption, fontSize: 26, font: 'serif', textAlign: 'middle-center', color: Color4.create(0.85, 0.82, 0.75, hud.captionAlpha) }}
      />
      <UiEntity
        uiTransform={{ width: 1500, height: 170, positionType: 'absolute', position: { top: 320 } }}
        uiText={{ value: hud.line, fontSize: 36, font: 'serif', textAlign: 'middle-center', color: Color4.create(0.92, 0.9, 0.86, hud.lineAlpha) }}
      />
      <UiEntity
        uiTransform={{ width: 1500, height: 60, positionType: 'absolute', position: { bottom: 70 } }}
        uiText={{ value: hud.hint, fontSize: 22, font: 'sans-serif', textAlign: 'middle-center', color: Color4.create(0.7, 0.7, 0.7, hud.hintAlpha) }}
      />
    </UiEntity>
  )
}

const Overlay = () => (
  <UiEntity uiTransform={{ width: '100%', height: '100%', positionType: 'absolute', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}
    uiBackground={{ color: Color4.create(0, 0, 0, hud.black) }}>
    <UiEntity uiTransform={{ width: 1400, height: 200 }}
      uiText={{ value: hud.deathText, fontSize: 34, font: 'serif', textAlign: 'middle-center', color: Color4.create(0.85, 0.82, 0.78, hud.deathAlpha) }} />
  </UiEntity>
)

/** A found paper. It stays up until the player presses E again or clicks Close; nothing hides it on a timer. */
const Document = () => (
  <UiEntity uiTransform={{ width: '100%', height: '100%', positionType: 'absolute', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', display: hud.docAlpha > 0.01 ? 'flex' : 'none' }}>
    <UiEntity uiTransform={{ width: 860, height: 520, flexDirection: 'column', alignItems: 'center' }}
      uiBackground={{ color: Color4.create(0.9, 0.86, 0.76, 0.985 * hud.docAlpha) }}>
      <UiEntity uiTransform={{ width: 804, height: 420, margin: { top: 28 } }}
        uiText={{ value: hud.doc, fontSize: 23, font: 'serif', textAlign: 'top-left', color: Color4.create(0.08, 0.06, 0.05, hud.docAlpha) }} />
      <UiEntity uiTransform={{ width: 804, height: 44, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <Label value="E  —  put it down" fontSize={18} font="sans-serif" color={Color4.create(0.35, 0.3, 0.25, hud.docAlpha)} uiTransform={{ width: 400, height: 40 }} />
        <Button value="Close" variant="secondary" fontSize={18} uiTransform={{ width: 120, height: 36 }} onMouseDown={() => closeDocument()} />
      </UiEntity>
    </UiEntity>
  </UiEntity>
)

export function setupHud() {
  ReactEcsRenderer.setUiRenderer(() => [Hud(), Document(), Overlay()], { virtualWidth: 1920, virtualHeight: 1080 })
}

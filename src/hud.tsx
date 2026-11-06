import ReactEcs, { ReactEcsRenderer, UiEntity, Label, Button } from '@dcl/sdk/react-ecs'
import { Color4 } from '@dcl/sdk/math'
import { hud, closeDocument } from './telepathy'
import { objective, objectiveAge } from './objectives'
import { DebugPanel } from './debug'

// Coded UI (not editable in the Creator Hub UI Designer): the text content and alpha are driven per frame.
const Hud = () => {
  const age = objectiveAge()
  const pulse = age < 4 ? 0.7 + 0.3 * Math.sin(age * 6) : 0.75
  return (
    <UiEntity uiTransform={{ width: '100%', height: '100%', positionType: 'absolute', flexDirection: 'column', alignItems: 'center' }}>
      {/* Top-centre: the top-left corner and the left edge belong to the Explorer's HUD (place card, sidebar, chat), and in
          preview its Local Tools menu takes the top-right. The centre strip is the one place nothing of the client's sits. */}
      <UiEntity uiTransform={{ width: 900, height: 70, positionType: 'absolute', position: { top: 30 }, flexDirection: 'column', alignItems: 'center' }}>
        <Label value={objective.text} fontSize={20} font="serif" textAlign="top-center" color={Color4.create(0.82, 0.78, 0.7, pulse)} uiTransform={{ width: 900, height: 30 }} />
        <Label value={objective.sub} fontSize={16} font="sans-serif" textAlign="top-center" color={Color4.create(0.6, 0.6, 0.58, 0.8)} uiTransform={{ width: 900, height: 26 }} />
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

/**
 * A found paper. It stays up until the player presses E again or clicks Close; nothing hides it on a timer.
 * Three looks (src/script.ts `style`): typed pages on aged paper in a typewriter face, handwritten pages in pen on a
 * notebook leaf, and `look` for what is in front of you rather than written: a dark panel, no paper. A `note` is
 * handwriting under the text, in ballpoint or pencil. The custom fonts need @dcl/sdk 7.31+; the mobile app and the
 * Creator Hub canvas draw the built-in fallback faces, so the boxes are sized for those too.
 */
const TYPEWRITER = 'assets/fonts/SpecialElite-Regular.ttf' // Special Elite, Apache 2.0 (licence beside it)
const PEN = 'assets/fonts/Kalam-Regular.ttf' // Kalam, SIL OFL (licence beside it)
const Document = () => {
  const a = hud.docAlpha
  const style = hud.docStyle
  const paper = style !== 'look'
  const hasNote = hud.docNote !== ''
  const pencil = hud.docInk === 'pencil'
  const noteColor = paper
    ? (pencil ? Color4.create(0.3, 0.28, 0.26, a) : Color4.create(0.12, 0.16, 0.42, a))
    : (pencil ? Color4.create(0.72, 0.7, 0.66, a) : Color4.create(0.6, 0.66, 0.9, a))
  const text = style === 'typed'
    ? { value: hud.doc, fontSize: 21, font: 'monospace' as const, fontSrc: TYPEWRITER, textAlign: 'top-left' as const, color: Color4.create(0.13, 0.11, 0.1, a) }
    : style === 'hand'
      ? { value: hud.doc, fontSize: 26, font: 'sans-serif' as const, fontSrc: PEN, textAlign: 'top-left' as const, color: Color4.create(0.12, 0.16, 0.42, a) }
      : { value: hud.doc, fontSize: 23, font: 'serif' as const, textAlign: 'top-left' as const, color: Color4.create(0.86, 0.83, 0.76, a) }
  return (
    <UiEntity uiTransform={{ width: '100%', height: '100%', positionType: 'absolute', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', display: a > 0.01 ? 'flex' : 'none' }}>
      <UiEntity uiTransform={{ width: 910, height: 570 }}>
      {/* the shadow of the sheet: a sibling drawn before it (children always draw over their parent's background) */}
      <UiEntity uiTransform={{ width: 900, height: 560, positionType: 'absolute', position: { top: 10, left: 10 } }}
        uiBackground={{ color: Color4.create(0, 0, 0, 0.5 * a) }} />
      <UiEntity uiTransform={{ width: 900, height: 560, positionType: 'absolute', position: { top: 0, left: 0 }, flexDirection: 'column', alignItems: 'center' }}
        uiBackground={paper
          ? { textureMode: 'stretch', texture: { src: style === 'hand' ? 'assets/images/paper-hand.png' : 'assets/images/paper-typed.png' }, color: Color4.create(1, 1, 1, a) }
          : { color: Color4.create(0.07, 0.07, 0.08, 0.92 * a) }}>
        {/* on the notebook leaf the writing starts right of the red margin line */}
        <UiEntity uiTransform={style === 'hand' ? { width: 700, height: 420, margin: { top: 60, left: 120 } } : { width: 780, height: hasNote ? 300 : 420, margin: { top: 54 } }} uiText={text} />
        {hasNote && (
          <UiEntity uiTransform={{ width: 740, height: 112, margin: { top: 8, left: 40 } }}
            uiText={{ value: hud.docNote, fontSize: 25, font: 'sans-serif', fontSrc: PEN, textAlign: 'top-left', color: noteColor }} />
        )}
        <UiEntity uiTransform={{ width: 780, height: 44, positionType: 'absolute', position: { bottom: 18 }, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <Label value="E  —  put it down" fontSize={17} font="sans-serif" color={paper ? Color4.create(0.4, 0.35, 0.3, a) : Color4.create(0.6, 0.6, 0.6, a)} uiTransform={{ width: 400, height: 40 }} />
          <Button value="Close" variant="secondary" fontSize={17} uiTransform={{ width: 110, height: 34 }} onMouseDown={() => closeDocument()} />
        </UiEntity>
      </UiEntity>
      </UiEntity>
    </UiEntity>
  )
}

export function setupHud() {
  ReactEcsRenderer.setUiRenderer(() => [Hud(), Document(), Overlay(), DebugPanel()], { virtualWidth: 1920, virtualHeight: 1080 })
}

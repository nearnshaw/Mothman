/**
 * EVERY WORD THE PLAYER READS OR HEARS. Edit here; nothing else needs to change.
 *
 *   SIGN      the board at the gate                       PAGES    the papers, stencils and marks you can click on
 *   OPENING   captions in the first half minute            VOICE    his telepathic passage, line by line
 *   HINTS     grey helper lines at the bottom of the screen DEATHS   the black-screen text when he takes you
 *   CAPTIONS  the narrator's lines, keyed by moment         ENDINGS  the black-screen text at the gate, lit or dark
 *   OBJECTIVES the top-left goal line and its sub-line
 *
 * Captions are one line each; a line stays up about as long as it takes to read (the duration is set where it is
 * shown). A page's `after` lines are what the narrator makes of it, said one after another once the page is put down.
 * `\n` breaks a line inside a page. The stencils are a single template (`stencil`).
 *
 * Not here: the painted textures (the plant map, the three bunker stencils, the sheriff's statement with its pencil
 * note, the gate sign) are drawn by scripts/gen-forest.py; edit the strings there, run `python3 scripts/gen-forest.py`, then `npm run build`.
 */

export const SIGN = 'W.VA. ORDNANCE WORKS\nFORMER EXPLOSIVES PLANT\n1942 - 1945\nSTORAGE BUNKERS AHEAD\n\nNO TRESPASSING\nNO ENTRY AT NIGHT'

export const OPENING = {
  where: 'The TNT area, north of Point Pleasant. The old explosives plant.',
  gate: 'The plant gate, chained since 1945. Duke went under the wire at dusk, after something in the trees. So did you.',
  howl: 'He has not come back. That is him, howling. Somewhere far up the road.'
}

export const HINTS = {
  flashlight: 'F  —  flashlight on and off', // shown until the first F
  use: 'E  —  read what you find, open doors, etc',
  graphics: 'No flashlight? Raise graphics quality above Low.',
  stutter: 'Not a battery problem. The light only fails when it is near.',
  comesBack: 'It comes back on its own, in the dark.',
  afterVoice: 'A lit lamp he answers at once. In the dark he only calls.'
}

export const CAPTIONS = {
  // the road
  dogSeen: 'A dog on the road. Not Duke. Somebody\'s hound, still wearing its collar.',
  dogGone: 'You look back for the dead dog. The road is empty. Something took it while your back was turned.',
  howlStopped: 'The howling has stopped.',
  // the flashlight
  stutter: 'The beam stutters. It does that when something is close.',
  putOut: 'He put it out.',
  putOutAgain: 'Out again.',
  deadClick: 'Nothing. It is not the batteries.',
  // the cabin
  cabinFirst: 'The watchman\'s cabin. The bulb is still on. Nobody has been here in a while.',
  window: 'Something is at the window.',
  notTheDoor: 'It is not the door he wants. It is the bulb.',
  // after the voice
  getOut: 'Get out now! Back down the road, to the gate. NOW.'
}

/** [goal line, sub-line] pairs for the top-left corner. */
type Objective = [text: string, sub: string]
export const OBJECTIVES: Record<'start' | 'map' | 'tally' | 'tags' | 'collar' | 'window' | 'listen' | 'gate' | 'over', Objective> = {
  start: ['Find Duke. He ran up the plant road.', ''],
  map: ['Find Duke. His tracks run up the plant road, toward the bunkers.', 'Bunkers 5, 6 and 7 are on the map.'],
  tally: ['Find Duke.', 'Whatever lives in the bunkers keeps a count. Of what?'],
  tags: ['Duke is not the first. Find out what is taking them.', 'Bunker 7 is the last one on the road.'],
  collar: ['It is here.', ''],
  window: ['Something is at the window.', 'The bulb is on. It can see the bulb.'],
  listen: ['Listen.', ''],
  gate: ['Get back to the gate.', 'In the dark, if you believe him.'],
  over: ['The night is over.', 'Duke is not in these woods. The woods belong to him.']
}

export const DEATHS = {
  road: 'They found you on the plant road in the morning.\nThe flashlight was still on, and the ground around it was grey with moths.',
  cabin: 'They found the cabin door open in the morning.\nThe bulb was still burning. The floor was grey with moths.'
}

export const ENDINGS = {
  lit: 'You kept the light on all the way down the plant road.\nHe let you. This time.',
  dark: 'You walked out in the dark.\nThe moths went straight in their flight, the way they wanted to all along.'
}

/** The passage, in his voice, inside the player's head, while the moths circle the beam. GDD §10. */
export const VOICE = [
  'You think they come to your light because they love it.',
  'They do not come. They were passing. Then they could not leave.',
  'Every one of them is trying to fly straight. Your lamp tells them where the moon is, and it LIES.',
  'They JUST WANT TO FLY STRAIGHT. They can not get away... they come back again and AGAIN and AGAIN',
  'So they turn. They turn, and climb, and fall, and turn, until they drop.',
  'I have counted them. Every one, on every wall, for every lamp your kind has ever left burning.',
  'The dogs came when I called. Their masters\' lamps burned on the barns all night. Now the masters know what it is to lose something.',
  'That is what you are to me. A light that LIES and that will not go out.',
  'Put. It. Out. Or I´ll put you out'
]

/**
 * The papers. `hover` is the prompt on the crosshair; `text` is the page; `after` is said once it is put down;
 * `reach` is how close you must be, in metres (default 4); `remove` takes the prop away once read (the collar).
 * Texts draw on the public record (design/lore.md). Your dog is Duke; Bandit is Newell Partridge's, from the record.
 */
export type Page = {
  hover: string
  text: string
  /** How the page is drawn: `typed` on aged paper in a typewriter face (newsprint, forms, stencils), `hand` in pen
   *  on a notebook leaf, `look` for what is in front of you rather than written (a dark panel, no paper). */
  style?: 'typed' | 'hand' | 'look'
  /** Something written by hand on the page, under the text: ballpoint by default, or pencil. */
  note?: string
  ink?: 'ballpoint' | 'pencil'
  remove?: boolean
  reach?: number
  after?: string[]
}

export function stencil(n: number): string {
  return `STORAGE BUNKER No. ${n}\nWEST VIRGINIA ORDNANCE WORKS\n\nT.N.T. — HIGH EXPLOSIVE\nCAPACITY 250 TONS\n\nNO FLAME. NO SMOKING. NO OPEN LIGHT.\n\nU.S. ARMY ORDNANCE DEPT. 1943`
}

export const PAGES: Record<string, Page> = {
  register: {
    hover: 'Read the paper', style: 'typed',
    text:
      'POINT PLEASANT REGISTER — Wednesday, November 16, 1966\n\n' +
      'COUPLES SEE MAN-SIZED BIRD... CREATURE... SOMETHING\n\n' +
      'Two young couples told deputies they were chased out of the old TNT area late Tuesday by a grey, man-shaped thing with wings and eyes that "glowed red when the headlights hit it." ' +
      'They say it kept pace with the car at close to a hundred miles an hour. Sheriff Johnson suggests a large heron.\n\n' +
      'Several residents on Route 62 report television sets going dark at about the same hour, with a high whine from the set. Two farms report dogs missing.'
  },
  map: {
    hover: 'Read the plant map', style: 'typed', note: 'bunker 7 — the big one — lights fail here',
    text:
      'WEST VIRGINIA ORDNANCE WORKS — T.N.T. (EXPLOSIVES) STORAGE AREA — PLANT MAP, 1944\n\n' +
      'The plant made TNT for the war, 1942 to 1945, and stored it out here in concrete rooms buried under earth: the storage bunkers, numbered 1 to 100, kept four hundred yards apart so one could blow without the rest. ' +
      'The map shows the gatehouse (this cabin), the power house, the pond, and bunkers 5, 6 and 7 along the plant road.'
  },
  statement: {
    hover: 'Read the statement', style: 'typed', ink: 'pencil',
    note: 'Third dog this month. If it comes to the cabin, kill the bulb. The switch is by the door. Sit in the dark till it goes.',
    text:
      'MASON COUNTY SHERIFF — STATEMENT OF WITNESS\n\n' +
      'Newell Partridge, Salem, Nov. 15:\n\n' +
      '"The television set went dark and began to whine. A high note, climbing. Bandit, my hunting dog, was howling at the hay barn. ' +
      'I pointed the flashlight on the barn and the eyes came back at me like bicycle reflectors, two red circles. ' +
      'The dog went after them. I called him. He never came back."\n\n' +
      '"I should have turned the light off."'
  },
  notebook: {
    hover: 'Read the notebook page', style: 'hand',
    text:
      'M. Hyre, Athens Messenger, Nov. 15:\n\n' +
      'Calls since Saturday: 500+. TVs going dark, whine first. Phones dead on Route 62. Cars stalling by the plant.\n\n' +
      'EVERY sighting involved a light. Headlights. A porch lamp. Partridge\'s flashlight.\n\n' +
      'Hal says a dog was found on the plant road Monday and was gone by the time he got back with the truck. Fourth dog this month.\n\n'
  },
  notice5: { hover: 'Read the stencil', style: 'typed', text: stencil(5), after: ['A storage bunker: a concrete room under a hill of earth, where the plant kept its finished TNT.', 'The steel door hangs open. The floor inside is grey with something.'] },
  notice6: { hover: 'Read the stencil', style: 'typed', text: stencil(6), after: ['The door has been forced from the outside. The frame is bent.', 'Dog prints in the dirt at the step, going in. None coming out.'] },
  notice7: { hover: 'Read the stencil', style: 'typed', text: stencil(7), after: ['The big one, the map said. Lights fail here.', 'Duke\'s tracks come right up the step.'] },
  tally: {
    hover: 'Look at the marks', reach: 8, style: 'look',
    text:
      'Scratches in the concrete, floor to ceiling, both walls, in groups of five. Thousands of them. Tens of thousands.\n\n' +
      'The newest are sharp-edged. The oldest have been here longer than the plant has been shut.\n\n' +
      'The floor is a drift of dead moths, ankle deep in the corners.',
    after: ['Something has been counting. For a very long time.', 'It counts them.']
  },
  tags: {
    hover: 'Read the tags', style: 'look', ink: 'pencil',
    note: 'Pruett, Cooper, Holstein, Thomas, McDaniel, Partridge: every one had the yard light burning. EVERY ONE. — H.',
    text:
      'Nine dog collars in a ring, each chewed through, each with its tag:\n\n' +
      'REX — PRUETT FARM, RT. 62\nSALLY — COOPER\nKING — HOLSTEIN, CAMP CONLEY RD.\nQUEENIE — THOMAS, RT. 62\nBLUE — McDANIEL\n' +
      'TIPPY — HOLSTEIN\nBANDIT — N. PARTRIDGE, SALEM\nLADY — RT. 62, NO NAME\nMAJOR — PRUETT FARM',
    after: ['Nine dogs. Nine farms along the plant road.', 'Every one of them had a yard light burning.']
  },
  collar: {
    hover: 'Pick up the collar', remove: true, style: 'look',
    text:
      'Duke\'s collar, chewed through. The buckle is still done up.\n\n' +
      'The tag reads:  DUKE  —  RT. 62  —  IF FOUND CONTACT THE FARM',
    after: ['It was lying on the step, in a ring of dead moths.', 'Duke\'s collar. No Duke.', 'The woods behind you have gone very quiet.']
  }
}

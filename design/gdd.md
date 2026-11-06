# Mothman 🦋🔦 — working design

*Draft 2 · 2026-11-04 · general game design (not a Creator Success proposal) · owner: Nico*

How to read this: **Owner** lines are what Nico said. **Proposed** lines are the agent's suggestions and stay proposals until Nico picks them. `[OPEN: …]` is waiting on something named; `TBD:` is a fact nobody knows yet. History: [decisions.md](decisions.md). Tech: [implementation-notes.md](implementation-notes.md). Lore bank: [lore.md](lore.md). Audience research: [acquisition.md](acquisition.md). Sources: [references.md](references.md). Spare ideas: [ideas.md](ideas.md).

> What changed in draft 2: the owner's research sheet (a Reddit community study of r/Cryptozoology and r/cryptids) was read as CSV. Its only Mothman-specific entries point at the Mothman Museum archive. Its real contribution is the audience: who these players are, what they count as evidence, which games already serve them, and the words that lose their trust. Sections 2, 3, 5, 9, 10 and 11 are new or rewritten because of it.

---

## 1. The seed (owner)

- A game based on the Mothman. A scary, dark forest. You are armed with just a flashlight.
- The thematic core: it is a myth that moths are attracted to a flame. They are not. Their flight navigation treats any bright light as the moon, so a nearby light confuses them; they keep correcting their path against it and end up flying in circles when all they want is to get away. It is truly sad and heartbreaking.
- At some point the Mothman communicates this **telepathically**. You should understand that this is his motivation, that he is somewhat justified, and that he has a strong reason to be after you.
- You should feel **guilt** for having your flashlight on (there are moths in the game too) and **fear of what the punishment will be** for it.
- **Do not start with this revelation.** Let the player play ignorantly at first. It will land harder.

## 2. Who this is for, and what they already play (from the sheet)

The sheet separates two crowds. **r/Cryptozoology** is evidence-minded: they argue plausibility, dissect grainy footage frame by frame, distinguish a cryptid (a claimed unknown animal) from a "fearsome critter" (a tall tale) and from folklore beings, and they mock sensational videos and wrong categories. **r/cryptids** is playful: creatures as mascots, "leggy bois", walking-pants jokes. The sheet's standing instruction: do not assume one shared definition across them.

**Where this game sits (proposed, follows from the owner's tone):** the serious crowd. Scary, sad, built on the documented record, with the creature's nature left arguable until the voice. The playful crowd is not the target, though the moths may travel there on their own.

**Already served:** when members asked for "a cryptid hunter in a forest" game they were pointed at *BIGFOOT* and *Folklore Hunter*, both co-op hunts: clue → identify → research → bait/trap. The sheet's question is which activity those do not serve. **Proposed answer:** they put you on the hunter's side of the flashlight. This game puts you on the moth's. You never hunt, trap or shoot; you carry the lamp, and the game is about learning what the lamp does. The sheet also records the community's own suggestion that a *respectful search* may appeal more than killing. That is this game's whole second half.

Full notes, the specific threads and the open audience questions: [acquisition.md](acquisition.md).

## 3. Intended experience

**Owner's feeling:** dread in the dark → sadness and heartbreak at the truth → guilt → fear of punishment.

**Proposed emotional arc (agent):**

| Movement | What the player feels | What they believe |
|---|---|---|
| Comfort | the beam is safety; moths in it are pretty | "I have a flashlight, I'm fine" |
| Dread | something answers the light | "it hunts by light; dark = safe" (a misreading) |
| Truth | the voice; the beam full of circling moths becomes a crime scene | "it was never chasing me, it was chasing my light" |
| Reckoning | guilt, and fear of what comes next | "what does it do to people who don't put it out?" |

**Proposed thematic spine (agent, unchosen):** in the real sightings, nearly every encounter happened inside a light aimed at the creature: car headlights, Newell Partridge's flashlight, the eyes "like bicycle reflectors". The couples who were "chased" at 100 mph were driving with headlights on. The game can replay those beats straight in the ignorant phase and let the reveal reinterpret the whole legend at once: *he was never after the people. He was after the lights.*

**Sceptic and believer both get to play (proposed, from the sheet):** the community includes people who think every sighting was an owl or a crane. Until the voice, the game never contradicts them. The eyes in the beam could be eyeshine; the screech could be an owl; the gliding shape could be a heron. Only the telepathy settles it, and by then the sceptic has been talking to the moths for twenty minutes anyway.

## 4. Player promise (proposed drafts, pick or rewrite)

1. *A night walk through the TNT woods outside Point Pleasant with one flashlight. The thing with red eyes only comes when the beam is on.*
2. *You have a flashlight, the woods have moths, and something out there has been counting them.*
3. *Every sighting in 1966 happened in somebody's headlights. Tonight it's your flashlight.*

`[OPEN: owner's choice]`

## 5. What the player does (proposed core action)

The verb set is deliberately tiny:

- **Walk** in first person through a dark forest.
- **Aim** the flashlight by looking.
- **Toggle** the flashlight on / off (one key, one button).
- **Look closely** at a few things (a newspaper, a plant map, a sheriff's statement, the stencils on the bunkers, a wall of scratches, a ring of collars, your dog's collar).
- **Open a door, flip a switch** (the gatehouse cabin: the one place with a light that is not yours).

**The cabin (owner pass 4, built):** a watchman's cabin stands off the road with its bulb still burning. Inside it is the safe-feeling place: walls, a door, a map of the plant, the sheriff's statement about the first dog. It is not safe. The bulb is a lamp left burning, which is exactly what he hunts: for half a minute nothing happens (time to feel safe and read the statement, whose pencil note says to kill the bulb: owner pass 5), then he is at the window (a face at the glass, the bulb flickering), then he hits the door, and if the bulb burns for about two minutes he opens the door and comes in. Switch the bulb off and he loses the place: he retreats and lurks. The lesson of the cabin, learned before the voice says it: *his problem is the light, not you.* Leaving in the dark is the only safe way out.

**The flashlight trade (proposed):**

- **On:** you see the path and ~15–20 m ahead. Within seconds, moths gather in the beam and start to orbit it. The Mothman's eyes shine back when the beam sweeps him; the longer the beam stays on, the closer he comes.
- **Off:** near darkness. You keep faint cues: sky between the trees, the far glow of Point Pleasant across the river, the pale concrete of a dome, water catching starlight. Moths leave the beam in a straight line within a second. The Mothman backs off, or stops approaching.

The tension is *see vs. be safe*, and the ignorant player reads it as "it hates light". No battery meter: the cost of light is attention, not a resource (battery is parked in [ideas.md](ideas.md)). **Owner note (2026-11-04):** a failing light that is not explained reads as a glitch, not a mechanic ("am I running out of battery?"). So every failure must say why: the 1966 TV whine rises whenever the beam stutters, the first stutter is captioned ("It does that when something is close"), a hint says there are no batteries, and after the reveal "He put it out" / "It comes back on its own, in the dark." He also only takes notice after 18 s of continuous beam and only presses after 45 s (owner pass 4: "he comes up at me too fast, it loses its fright factor"), so the light is usable for most of a walk, and every time he vanishes the clock starts over.

**Evidence instead of weapons (proposed, from the sheet):** the community's visual language is clippings, field journals, footprint casts and disputed footage, and their standing question is "what makes an in-game sighting arguable?" The player carries no camera, but the game can keep a **witness statement** that writes itself from what the player actually did: *"Subject reports two red lights at approx. 40 yards. Subject's flashlight was on at the time."* That last clause appears in every entry and nobody comments on it until the reveal. Where the statement lives (a pause screen, the ending) is open.

**Proposed "punishment" (agent, unchosen):** it mirrors what the lamp does to moths. While the light stays on after the reveal, *the forest circles*: paths bend back on themselves, you arrive where you started, your own footprints cross your path. With the light off the trails run straight. Second candidate: the lore's electronics failures (TVs going dark, a rising whine, stalled cars) become the flashlight flickering and dying when he is near. Both could coexist. `[OPEN: owner's choice]`

## 6. Moths as a system (proposed)

The moths are the truth, visible from minute one, understood only after the reveal.

- Moths appear in any lit beam and **orbit** it, banking toward the light. Some **stall** upward and fall back; some **flip** when they pass over the lamp and drop. These are the three motions the 2024 study filmed (see §9). In a long-held beam, moths begin to **drop** into the circle of light on the ground, spent. Planted quietly in the dread phase, never pointed at.
- Light off → every moth flies away straight. The player sees it dozens of times before they know what it means.
- After the reveal the same behaviour reads as suffering. No new art is needed for the turn; the meaning changes, not the moths.
- Counts: a few scripted moth entities around the beam for the readable orbit, plus a particle layer for ambient moths. Budget: ≤ 1,000 live particles and ≤ 8 emitters per scene on desktop.

## 7. The Mothman as a system (built; HTN domain `src/npc/mothman/mothman.domain`)

He plans with an HTN (hierarchical task network): every tick the game writes what he can know as facts, and the planner picks the first branch whose condition holds and runs its steps. He replans only when something outside his control changes (the flashlight, the cabin bulb, the room the player is in, the story), never because of his own progress.

**Facts he plans against:** `beam on|off`; `lit none|some|long` (continuous beam: some ≥ 18 s, long ≥ 45 s); `dist far|mid|near` (18 / 9 / 2.8 m); `place woods|cabin`; `lamp on|off` (the cabin bulb); `lamp_lit none|some|long|spent` (bulb on with the player inside: some ≥ 30 s, long ≥ 65 s, spent ≥ 110 s; owner pass 5: half a minute of quiet first); `phase ignorant|revealed`; `summoned` (Duke's collar picked up); `scared` (survived the first lunge); `dormant` (the player has not yet walked 55 m from the gate: he is not rendered and nothing happens; the beam clock starts when he wakes, so a paper read in the light at the gate counts for nothing).

**Branches, in priority order** (first match wins):

| Branch | When | What he does | What the player sees / hears |
|---|---|---|---|
| speak | summoned | approach near, speak | stands at the bunker door; waits for you to put the collar's page down; then the passage runs in your head |
| hidden | collar in hand, its page or lines still running | hide, wait | nowhere: the roost is empty when you turn |
| dormant | dormant | wait | nothing: the first stretch of road is yours |
| break_in | cabin, bulb on ≥ 110 s | enter, take | the door opens by itself; blackout |
| haunt | cabin, bulb on ≥ 65 s | window 6 s, bang, window 7 s, wait | a face at the glass, the bulb flickering, a blow on the door |
| peek | cabin, bulb on ≥ 30 s | window 5 s, wait 10 s | eyes at the nearest window ("Something is at the window." once per visit) |
| settle | cabin, bulb on | lurk, wait 6 s | nothing: half a minute to feel safe and read the statement |
| leave_cabin | cabin, bulb off | retreat, lurk, wait | wings going away; silence |
| take | beam on, near, lit long, scared | take | the kill: into the face, blackout, you wake at the gate |
| scare | beam on, near, lit long | lunge, rise, retreat | the jumpscare, then he is gone straight up |
| flee_the_dark | beam off, near | rise, retreat | "like a helicopter" |
| slip_away | beam off, mid | retreat | |
| lurk | beam off | lurk, wait 6 s | a rare call from somewhere else each time |
| punish | revealed, beam on | approach mid, hover, screech, approach near, loom | after the voice, a lit beam is answered at once |
| press | beam on, lit long | screech, approach near, loom 3 s | the scream, him close, the beam stuttering and the TV whine |
| stalk | beam on, lit some | approach mid, hover 7 s, screech, retreat, lurk, wait | he comes to ~9 m where you are looking, hangs there swaying, screams, and is gone into the dark before you get used to him; next time from elsewhere |
| watch | (fallback) | watch 1 s | two red reflections when the beam sweeps him |

The hover is a sway in front of the player (never a circle around them: owner pass 4). He never kills on sight in the ignorant phase; being "caught" is being looked at for too long, after a first warning lunge. Until the voice, every state above has an animal explanation a sceptic could hold onto (§3).

**Owner decision:** his behaviour is an HTN plan; the unreleased skill for it is installed in this scene; details in [implementation-notes.md](implementation-notes.md). Everything he does traces to one top-level task (*behave*, which is *put the light out*), and the reveal is the moment the player learns what it was.

## 8. Structure (built, four movements; the objective line on screen changes with each)

The owner's pass-4 note: "I need an objective. I'm initially after my lost dog, not bad, but then I should realize I'm caught in something bigger." So the objective starts small and is rewritten by what you read:

1. **The gate.** *Find Duke. He ran up the plant road.* The chained plant gate behind you (you both came in under the wire), the sign (ordnance works, storage bunkers ahead, no trespassing, no entry at night), the Register's first report on the ground, paw prints on the road in the beam, the first moths, the howl far up the road. A dead dog on the road that is not yours and is gone when you look back. Nothing of him for the first 55 m.
2. **The gatehouse.** The watchman's cabin with its bulb on: the plant map (bunkers 5, 6, 7; a ballpoint note "7, the big one, lights fail here", the bunker ringed in pen) and the sheriff's statement about Partridge's dog. Objective: *His tracks run up the plant road, toward the bunkers.* The cabin set piece (§5): window, door, break-in; lights off to leave. The chase in the woods meanwhile: eyes, the hover, the scream, the first lunge.
3. **The bunkers.** Bunker 5: both walls scratched floor to ceiling in fives, the floor a drift of dead moths (*"It counts them."*). Bunker 6: nine chewed collars in a ring, nine farms, every one with a yard light burning (*Duke is not the first. Find out what is taking them.*). The howling stops 36 m short of bunker 7. Bunker 7: Duke's collar on the step; the lines about it run with him nowhere in sight; then he comes and speaks (§10), and a line sends you back to the gate.
4. **The walk out.** *Get back to the gate.* The light is now a moral choice, not a tool: with it on he answers at once and puts it out; in the dark the moths go straight up through the trees. Two ending lines at the gate; the screen goes black and stays black. Other ending shapes stay in [ideas.md](ideas.md).

Target length: `TBD: not discussed yet` (15–25 minutes in one sitting is what the structure implies; agent estimate, not a decision).

## 9. Lore the game uses (selected; full bank in [lore.md](lore.md))

- **Place:** the "TNT area" north of Point Pleasant, West Virginia. It really is explosives: the West Virginia Ordnance Works made TNT (trinitrotoluene) there from 1942 to 1945 and stored it in concrete rooms buried under earth mounds ("igloos"; the Army called them storage magazines) spread through the woods so one blast would not take the rest. After the war it became the McClintic Wildlife Management Area; the mounds, the old power house and the ponds stayed. Teenagers used its dirt roads as lovers' lanes, and the first 1966 sighting was by the old power plant there. In the playable the words are plain (owner pass 4: "TNT zone" and "magazines" meant nothing): the sign says *former explosives plant, storage bunkers ahead*, the map says the bunkers are concrete rooms under earth where the finished TNT was kept, and each bunker's stencil repeats it. The bunkers are also *his*: the count on the walls of No. 5, the collars in No. 6, his roost in No. 7. They are where he has been all along, not scenery.
- **Time:** 15 November 1966 to 15 December 1967, the night the Silver Bridge fell into the Ohio with 46 people on it. Sightings faded after.
- **The creature as described:** 6–7 ft, wider than a man, grey or brown (some say black with white wings), bat-like wings ~10 ft, eyes near the top of the shoulders, glowing red, hypnotic; no face anyone could make out. Rose straight up "like a helicopter", glided without flapping, hummed, screeched.
- **Light in every encounter:** headlights, a flashlight, a porch light. Eyeshine "like bicycle reflectors".
- **The dog:** Newell Partridge's hunting dog Bandit chased two glowing red circles toward a barn and was never seen again; his TV had gone dark with a rising whine. A dead dog lay on the road near the TNT area and was gone minutes later.
- **Electronics:** TVs, phones, police radios and car engines failing that winter.
- **Paper:** the *Point Pleasant Register*'s first report, Mary Hyre's 500 phone calls, the Mothman Museum's clippings archive (the sheet's pointer). Newsprint is the community's native visual, and it dates every scene without a title card.
- **Explanations the town rejected:** a sandhill crane off its route, a barred owl's eyeshine, a snowy owl someone shot, hoaxers tying flashlights to helium balloons. All of them are usable as sceptic-bait in the first two movements.

**Lore use notes (facts, agent):**
- The legend and the public record are free to use. John Keel's book and the 2002 film are protected works: use documented events, not their inventions.
- The witnesses were real private people; some are still alive. `[OPEN: real names in-game or fictionalised — owner's choice]`
- The sheet warns twice against claiming sightings as fact and against reproducing archival photos or film frames without rights. Original visuals only; the clippings in-game should be written, not scanned.
- The sheet flags that this audience punishes cultural sloppiness ("that's not a cryptid", Indigenous beliefs taken out of context). The "Cornstalk curse" is a settler legend about a murdered Shawnee leader; the game can do without it. Proposed standing non-goal: no curse, no Indigenous framing of the creature. `[OPEN: owner's confirmation]`

## 10. The telepathic passage (draft, owner's framing, for rewriting)

Rules the owner set: he explains the moths; he is somewhat justified; he has a strong reason; the player should feel guilt and fear. Not at the start.

Draft lines, Mothman's voice, inside the player's head, while moths circle the beam:

> You think they come to your light because they love it.
> They do not come. They were passing. Then they could not leave.
> Every one of them is trying to fly straight. Your lamp tells them where the moon is, and it lies.
> So they turn. They turn, and climb, and fall, and turn, until they drop.
> I have counted them. Every one, on every wall, for every lamp your kind has ever left burning.
> The dogs came when I called. Their masters' lamps burned on the barns all night. Now the masters know what it is to lose something.
> Put it out. Or I take you too, and your lamp lies burning on the road till morning, and every moth in the valley comes to it.
> That is what you are to me. A lamp that will not go out.

*Revised 2026-11-04, twice (owner notes): "the moon", not "the sky"; the closing lines threaten and name the revenge (the dogs, the barn lamps from Partridge's statement). "I will not be quick" is retired: taking a light slowly is no threat (owner pass 4). The threat is now what your lamp does after you are gone. The earlier "I do not want you. I want it out." is retired as too mild.*

Then silence, and the sound of the moths. Nothing attacks. The next thing the player does is the real test of the scene.

*Presentation (owner pass 5): the lines sit in the upper third of the screen, clear of the crosshair, and each stays up for about three words a second (four seconds at least), so the long lines can be read.*

**Science note for the writing (fact, agent):** the owner's framing (moths mistake the lamp for the moon and keep correcting) is the classic "transverse orientation" explanation. A 2024 *Nature Communications* study (Fabian et al.) tested it and rejected it in favour of the **dorsal light response**: insects keep their backs to the brightest thing in view because that has always been the sky; a nearby lamp becomes a false sky, so they bank toward it and orbit, stall or flip, and crash. The owner's emotional core is untouched and arguably sadder: *they are not drawn in; they are trying to fly level and the world keeps turning under them.* The draft is written to be true under both framings. The evidence-minded audience in §2 is exactly the crowd that will check. `[OPEN: which framing the monologue uses — owner's choice]`

## 11. Why the player is in the woods

**In the playable since 2026-11-04: option 1, the dog** `[agent-decided]`, confirmed in use by the owner's pass-4 note ("I'm initially after my lost dog, not bad"). Your dog is **Duke**; Bandit stays Newell Partridge's dog from the record (owner pass 4: two Bandits was too much coincidence). How it plays: the opening lines say Duke ran up the plant road at dusk after something in the trees. A howl comes from the far end of the woods, from bunker 7, louder as you near. On the road: paw prints in the beam, and a dead dog that is not yours and is gone when you look back. In the cabin, the statement about Bandit; in bunker 6, nine collars with Bandit's tag among them; at bunker 7's step, Duke's chewed collar in a ring of dead moths; the howling stops. Keep the light on a few seconds more and he speaks. The mystery is solved by the voice: nothing is hunting dogs; something is answering lamps, and the dogs were the lesson it chose for their owners. After the voice, the road back is the ending (§8). The options were:

1. **The dog.** You are looking for your dog. Collar found, dog not. Ties to Bandit and the vanished dead dog.
2. **The dare.** It's lovers' lane; you came because everyone's talking about the red eyes. Keeps the guilt sharper: you brought the light on purpose.
3. **The stringer.** You are checking the TNT area for the local reporter after the 500 calls. Gives a radio and a notebook as lore objects, and makes the witness statement (§5) diegetic: you are writing it.

## 12. Space

The forest road, the bunkers, the power house, the plant fence, a pond, a ridge with a view of the town's lights and the bridge across the Ohio. **Owner decision (2026-11-04):** many parcels, no limit; pass 4: "even bigger, I can still easily walk off". The playable is 12 × 12 parcels (192 × 192 m) inside a chain-link fence with a gate at the spawn; a 274 m winding road with spurs, the cabin, three bunkers, a pond, the power house and ~540 trees; fog keeps visibility around 20 m. With the lamp off the night is not pitch black: a trace of ambient (the sky colours) lets a shape be guessed against the trees, not walked by (owner pass 5). No jumping or gliding, so the fence and the mounds hold. `[OPEN: land vs World for deployment — owner's choice]`

## 13. Player mode

Not discussed. The design reads as **solo**. Decentraland scenes are shared by default, so other players and their flashlights would be present unless this is a World with low concurrency or the design embraces it (a second beam in the dark is either a ruin or a gift). `[OPEN: solo or shared — owner's choice before any build]`

## 14. Platform fit (facts checked against the installed SDK skills, 2026-11)

- **True darkness is desktop-only.** The sky, sun and fog overrides that make a scene black are ignored on the mobile app and the Bevy explorer; those keep the normal sky. A fixed night time of day works everywhere but is not pitch black. `[OPEN: desktop-only, or a lighter mobile version — owner's choice]`
- **Scene lights can be off entirely.** On the desktop *Low* quality preset (and mobile *Very Low*) no scene light renders, so the flashlight beam would be invisible. The scene needs an in-game prompt to raise quality, or an emissive fallback. Hard dependency on the core mechanic.
- **The flashlight** is a spotlight with shadows parented to the camera (the documented "aim item" pattern). Desktop *Medium* renders 6 scene lights, *High* 10, at most 3 with shadows. Enough for one flashlight plus a few accents.
- **First person** can be forced with a camera-mode area covering the whole play space.
- **Moths**: scripted entities plus particles within the budgets in §6.
- **Telepathy** is screen text plus audio. A short cinematic camera is available for the reveal if wanted.
- **Flashing lights**: the beam flicker and any lightning must stay ≤ 3 flashes per second and avoid large saturated red flashes.

## 15. Current playable scope

A first playable exists (2026-11-04, five passes): 12 × 12 fenced parcels, catalog-model forest, a winding plant road with paw prints and spurs, flashlight, sprite moths, the HTN-driven Mothman (a Blender-built winged model with idle, flap and glide clips: stalk → vanish → scream → jumpscare → kill, plus the cabin branches), the gatehouse cabin set piece, three storage bunkers with their lore, ten readable objects, an on-screen objective that changes with what you read, attention sounds, the dog frame (§11), the telepathic passage and a walk-out ending. Build record: [01-experiments/playable-2026-11-04-first-playable.md](01-experiments/playable-2026-11-04-first-playable.md). Played by the owner three times; pass 5 answers the third set of notes.

## 16. Open questions, in the order they block work

1. Solo or shared (§13).
2. Desktop-only darkness, or a mobile version (§14).
3. Deployment target: land or a World (§12).
4. Confirm or swap the dog frame (§11) and the walk-out ending now in the build (§8).
5. Science framing of the monologue (§10).
6. Real or fictional witness names; the no-curse non-goal (§9).
7. Whether the witness statement is in (§5).

## 17. First thing worth testing (candidate, not yet parked)

*IF moths visibly orbit the beam from minute one and the reveal comes around two-thirds through, THEN players who hear the reveal switch the light off within the next minute without being told to.* The criterion (how many players, how fast) is the owner's to set before this becomes a registered test. Cheapest check: a desktop build of movements 1–3 with placeholder trees, one dome, the moth orbit and the text. What the player does with the switch is the observation. The sheet suggests where the first testers are: the two subreddits, approached with the game's own uncertainty rather than a monster reveal (see [acquisition.md](acquisition.md)).

# Decisions

Append-only, newest first. `owner call` = Nico chose; `agent call` = the agent chose alone and the line carries `[agent-decided]` where it is used.

- 2026-11-05 · **He does not exist until 55 m up the road.** The 110 s timer is gone (reading the register in the light was enough to bring him): he wakes on distance from the gate only (or the collar, or a death), is not rendered before, and the beam clock starts at his waking. · owner call (not so fast) / agent call (55 m, beam clock reset) `[agent-decided]`
- 2026-11-05 · **The ending stays black.** After the gate the screen goes black with the ending text and never comes back to the world. · owner call
- 2026-11-05 · **Every word in one file:** `src/script.ts` holds the sign, the opening, the hints, the captions, the objectives, the pages, the passage, the deaths and the endings; the painted textures keep their strings in `scripts/gen-forest.py`. · owner call (I want to edit those directly) / agent call (one file) `[agent-decided]`
- 2026-11-05 · **The sign reads NO TRESPASSING / NO ENTRY AT NIGHT**; the map's bunker-7 note is in blue ballpoint, ringed; captions sit lower (top 200) and the passage below them (320); the sparks carry a flare sprite and fall; the cabin barrel is the Pirates pack's wooden rum barrel. · owner call
- 2026-11-05 · **A chained gate at the spawn.** The plant gate (two leaves, chain, padlock, KEEP OUT) stands in the south fence where the road leaves; it does not open. You and the dog came in under the wire; "get back to the gate" is the way out the same way. · owner call (a gate you cannot cross) / agent call (under the wire)
- 2026-11-05 · **The howl stops before the roost, not at the collar.** At 36 m from bunker 7's door the howling stops ("The howling has stopped."); the dog has been dead a while. · owner call
- 2026-11-05 · **He is hidden until the collar's lines are over.** New `hidden` fact between picking up the collar and the end of its captions: he glides away behind the player, eyes dark; the final approach starts only after. · owner call
- 2026-11-05 · **After the voice, a line tells you to go:** "Get out of here. Back down the road, to the gate. Now." and a hint about lit versus dark. · owner call
- 2026-11-05 · **Sparks when he puts the light out**; the tally wall is clickable from 8 m; the dead-dog line says plainly that the body is gone; the collars box carries a pencil note (every farm had the yard light on) so the narrator infers only what is written; the blank tag is gone; no sound plays on the first frame (the editor's mute needs it). · owner call
- 2026-11-05 · **Moths beat their wings:** the sprite's width closes and opens with the roll. · owner call
- 2026-11-05 · **No eyes in the first second.** He stays at the roost with his eyes dark until the player has walked 42 m from the gate (or 110 s have passed); the collar or a death also wakes him. · owner call (wait till I walked a bit) / agent call (42 m / 110 s) `[agent-decided]`
- 2026-11-05 · **Moths fly in three dimensions.** No billboard: each sprite's head points along its own flight, it rolls ±60° with the wingbeat, banks into the orbit and tumbles when it drops. · owner call
- 2026-11-05 · **Ambient doubled again** (sky colours ≈ 0.1–0.2) after "still pitch black". · owner call
- 2026-11-05 · **A page shows only what is written; what you make of it comes after.** The narrator's conclusions (nine farms, it counts them, the howling has stopped, what the stencilled bunkers look like) are captions after the page is put down, never on the page. · owner call
- 2026-11-05 · **The voice waits** until any open page is down and the captions have run out, then 1.5 s of quiet. · owner call
- 2026-11-05 · **Sill shelves under the cabin windows** keep the player a step back from the glass, because the beam starts half a metre ahead of the camera and went dark against it. · owner call (block me) / agent call (shelves)
- 2026-11-05 · **Tally tiles.** Custom plane UVs still came out stretched in the Explorer; the walls are now twelve 3 × 1.5 m planes with default UVs, every one clickable. · owner call
- 2026-11-05 · **Half a minute of quiet after entering the cabin.** He does nothing at the cabin until the bulb has burned 30 s with the player inside (then the window; the door at 65 s; in at 110 s), so there is time to feel safe and read the statement. The statement now carries the watchman's pencil note: kill the bulb, the switch is by the door. · owner call (the grace, the hint) / agent call (30 / 65 / 110 s) `[agent-decided]`
- 2026-11-05 · **"Something is at the window." once per visit**, so it stops walking over other captions. · owner call
- 2026-11-05 · **Not pitch black.** The sky colours (which are the ambient light) carry a trace of blue-grey: enough to guess that something moved, not enough to walk by. · owner call (some light, barely) / agent call (the values)
- 2026-11-05 · **The gate sign reads black on a pale board.** `TextShape` is unlit, so white letters glowed in the dark; a lit plane behind black letters goes dark with everything else. · owner call
- 2026-11-05 · **His lines sit in the upper third of the screen** (clear of the crosshair and the captions) and each line stays up for as long as it takes to read it (about three words a second, four seconds at least). · owner call
- 2026-11-05 · **The kill closes any open paper, and the flashlight works again after the respawn** (it was being re-killed every frame of the blackout after the respawn had cleared it). · owner call (both found in play)
- 2026-11-05 · **Bunker 5's scratches cover both long walls at one scale and the whole wall is readable** (two tiled planes instead of a textured box plus a small click panel); the plant map reads the right way round. · owner call
- 2026-11-04 · **No jumping, double jump or gliding** in the scene (InputModifier), so the fence, the cabin roof and the bunker mounds hold. · owner call
- 2026-11-04 · **The spawn is inside the fence**, at the gate; the cabin door is a plank leaf hinged on the jamb with the knob on the latch side; the roof is a proper pitch with stepped gables; the cabin's TV is a 1966 wooden console set built to match the planks, not the catalog's modern TV. · owner call (what was wrong) / agent call (the fixes)
- 2026-11-04 · **The wings beat symmetrically.** The Blender rig keyed the mirrored wing bones with opposite signs about their local X, which is the same global direction; same sign now. · owner call
- 2026-11-04 · **An objective line on screen**, starting with the dog and rewritten by what the player reads (map → bunkers; tally → "it counts"; collars → "Duke is not the first"; Duke's collar → "It is here"; after the voice → "Get back to the gate"). The mystery is solved by the voice. · owner call (an objective, the escalation) / agent call (the lines) `[agent-decided]`
- 2026-11-04 · **Scene 12 × 12 parcels (192 × 192 m), fenced**, with a gate at the spawn. · owner call (even bigger) / agent call (12 × 12 and the fence) `[agent-decided]`
- 2026-11-04 · **The gatehouse cabin as the safe-looking place.** Enterable, a bulb on a switch, windows; he comes to the windows, hits the door, comes in if the bulb burns ~1 min; bulb off and he leaves. Leaving in the dark is the way out. · owner call (the cottage, the window, the lights-off lesson) / agent call (timings, that it is the plant gatehouse)
- 2026-11-04 · **He comes slower and never circles.** Notice after 18 s of beam, press after 45 s (was 8 / 22); approach at a slow glide; the hover is a sway in front of the player at 9 m, then he vanishes into the dark and returns from elsewhere. · owner call (too fast, no 360) / agent call (numbers) `[agent-decided]`
- 2026-11-04 · **The monologue trigger is one thing: pick up Duke's collar at bunker 7.** He comes regardless of the light and speaks; no beam clock involved. · owner call (must be reliable) / agent call (collar only)
- 2026-11-04 · **The domes are storage bunkers, and they are his.** Three along the road: No. 5 the count (walls of scratches, dead moths), No. 6 the collars, No. 7 the roost. Each has a stencil in plain words; the sign says "former explosives plant, storage bunkers ahead"; "magazines" and "TNT zone" are gone from the player-facing text. · owner call (explain or remove; connect to him) / agent call (which lore)
- 2026-11-04 · **Your dog is Duke.** Bandit stays Partridge's dog in the record and on a collar in bunker 6. · owner call
- 2026-11-04 · **"I will not be quick" is retired.** The threat is what your lamp does after you are gone (it lies burning on the road and every moth in the valley comes to it). · owner call (it made no sense) / agent call (the new line)
- 2026-11-04 · Blender-built Mothman model with a wing rig and three clips, replacing the primitive figure; new creepy sounds (hum, wingbeats, call, screech, tap, lunge, door, switch, buzz, howl) synthesized; the owner's go-ahead to run Blender is taken from "make a better model". · owner call (better model, creepy sounds) / agent call (how) `[agent-decided]`
- 2026-11-04 · Clues about the dog are physical: paw prints on the road, the dead dog as a model, the ring of collars, Duke's collar on the step. · owner call

- 2026-11-04 · **A found paper stays open until the player puts it down** (E again, or the Close button); nothing hides it on a timer, because slower readers were losing the text. · owner call
- 2026-11-04 · **Every flashlight failure must say why.** No battery exists; the light only fails when he is close (stutter + the 1966 TV whine + a one-time caption and hint) or when he puts it out after the reveal ("He put it out." / "It comes back on its own, in the dark."). He notices the beam after 8 s and presses after 22 s (was 5/14). · owner call (legibility) / agent call (the sounds, lines and timings) `[agent-decided]`
- 2026-11-04 · **TNT is literal and the game says so.** The sign at the road and the stencil on Magazine No. 7 state that the West Virginia Ordnance Works made and stored TNT here, 1942–45. · owner question → agent call (wording)
- 2026-11-04 · **Why you are here: the dog (GDD §11 option 1), in the build.** Bandit's howl from Magazine No. 7 is the lure; the collar at its door is the goal; the road back after the voice is the ending (two lines, light on or off). Chosen by the agent to answer "what's the point of walking in the forest"; the owner can swap it. · agent call `[agent-decided]`
- 2026-11-04 · The five readable things are five different objects (newspaper page, collar, notebook, wall stencil, typed page on the power-house wall), not five copies of a book. · owner call
- 2026-11-04 · The plant road winds (six bends, three spurs: pond, power house, a dead end) and has no glow: it exists only in the beam. · owner call (less linear, less visible) / agent call (shape)
- 2026-11-04 · Fewer moths, slower: one at first, about three after 10 s, six at most (was two at once, up to ten). · owner call
- 2026-11-04 · The passage says "where the moon is", and the closing lines threaten and name the revenge (the dog). New text in GDD §10. · owner call

- 2026-11-04 · **Being caught kills you, eventually, after a first jumpscare.** Implemented as: first catch = lunge into the face and release; second catch (light still on) = blackout, a line, respawn at the road. · owner call (rule) / agent call (the exact sequence and timings) `[agent-decided]`
- 2026-11-04 · Something must direct attention to him when he is behind you: a sound. Implemented as spatial calls and wing-rustles from his position when out of view, plus closing in where the player is looking. · owner call (sound) / agent call (which sounds)
- 2026-11-04 · Lore documents to find and read; a UI hint for F; a little fog; better art everywhere. Catalog trees, sign, book model and a drawn moth sprite were fetched/made under the "better art" instruction. · owner call

- 2026-11-04 · **Scene size: many more parcels, "there is no limit."** Set to 8 × 8 parcels (128 × 128 m); the exact count was the agent's pick within the owner's instruction. Replaces the 1-parcel entry below. · owner call (size) / agent call (8 × 8) `[agent-decided]`
- 2026-11-04 · The flashlight must be unmistakable: turning it on has to change what you see. · owner call (from the first play)

- 2026-11-04 · Build a first playable demo of the GDD (exploratory, no criterion). · owner call
- 2026-11-04 · First playable is a greybox: primitive trees, body and moths, synthesized placeholder sound, no downloaded assets (asset downloads need the owner's yes). · agent call `[agent-decided]`
- 2026-11-04 · Scene stays at 1 parcel for the demo; enlarging needs the owner's yes. Layout and distance bands are parameterized so the change is a scene.json edit plus one script run. · agent call (pending owner)
- 2026-11-04 · Reveal trigger for the demo: 40 s of total beam time plus one dropped moth, or 75 s of beam time; punishment after the reveal: the flashlight dies for 6 s after 18 s of beam. Tuning placeholders, not design decisions. · agent call `[agent-decided]`

- 2026-11-04 · The Mothman's behaviour will use the unreleased HTN domain-authoring skill (sdk-skills PR #155); installed scene-locally, see [implementation-notes.md](implementation-notes.md). · owner call ("for sure the mothman will use this")

- 2026-11-04 · Research sheet supplied as CSV and imported: it is community research on r/Cryptozoology and r/cryptids, not a Mothman source list; GDD rewritten (draft 2) around its audience, rival and evidence-culture findings; the earlier public-source lore bank stands. · owner call (import) / replaces the "outstanding check (access)" entry below
- 2026-11-04 · Proposed, not yet decided: the game targets the evidence-minded crowd; no hunting, trapping or shooting; every pre-reveal sighting stays arguable; no Cornstalk curse or Indigenous framing. · agent proposals awaiting owner

- 2026-11-04 · **Working direction: general game design** (the default; not a Creator Success proposal, not doc-only). Aim: write the first GDD for the Mothman game. Active document: [gdd.md](gdd.md). · agent call (default applied; owner asked for "the GDD")
- 2026-11-04 · The game is a Mothman horror: a scary dark forest, armed with just a flashlight. · owner call
- 2026-11-04 · Thematic core: the moth-and-flame myth is false; moths are confused by nearby light and circle when they want to leave. This is the Mothman's motivation; he is somewhat justified and has a strong reason to be after the player. · owner call
- 2026-11-04 · The Mothman tells the player this **telepathically**, at some point in the game. · owner call
- 2026-11-04 · The player should feel **guilt** for having the flashlight on and **fear of the punishment** for it. · owner call
- 2026-11-04 · There are **moths in the game**. · owner call
- 2026-11-04 · **The reveal does not open the game.** The player plays ignorant first ("it will land harder"). · owner call
- 2026-11-04 · Lore is to be taken from the sources cited in the owner's spreadsheet. The sheet is private and unreadable so far; public sources were used as a stand-in and the lore bank is marked for re-check. · owner call (sources) / outstanding check (access)

## Standing non-goals

- None recorded yet.

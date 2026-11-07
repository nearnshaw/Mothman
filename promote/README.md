# Mothman — marketing kit

Built with the promote-scene skill on 2026-11-06, from `design/gdd.md`, `design/lore.md`, `src/script.ts` (the in-game lines) and
`scene.json`. Nothing here is deployed with the scene (`promote` is in `.dclignore`). Open `index.html` in a browser: it works
offline. Audience first, then the posts per destination (X / Twitter, Instagram, Reddit, YouTube Shorts), then brand and assets.

**Link:** not published yet. Every post keeps `{LINK}`; rebuild the page after deploying (step 4 below) and the real link fills in.

## What is here

- `posts.json`: the single source of truth: audience and venues (every row with its source), the plan, the listing texts, the brand,
  the quote cards and 23 posts (launch 4, coming soon 4, footage 5, quote 3, behind the scenes 2, Reddit 3, Shorts 2).
- `index.html` + `kit-data.js`: the kit page (edit, preview, copy, download each post). `copy.md`: the same copy as text, with the
  scene-description rewrites at the top. `footage-shotlist.md`: what to record in-world, including the Foundation's screenshot
  and trailer asks and the two Shorts.
- `logo/`: `mothman_wordmark.png` (transparent, hard shadow), `mothman_lockup_on_black.png` (wordmark + tagline),
  `mothman_icon_1024.png` ("66" over POINT PLEASANT / NOVEMBER). Face: Special Elite, the scene's own typewriter font
  (`assets/fonts/`, Apache 2.0).
- `images/renders/`: six stills rendered in Blender from the scene's own layout and models, 1600 px square:
  `hero` (him on the plant road in the beam), `gate` (the sign at the start), `cabin` (the bulb lit, him at the glass), `dog`
  (the hound on the road), `collars` (bunker 6's ring and the moth heap), `bunker` (bunker 7's headwall and door).
- `images/keyart/`: the hero shot re-rendered at 1920x1080 and 1080x1080 with headroom, no text.
- `images/social/`: key art with the wordmark (landscape and square), the X header 1500x500, three quote cards
  (`quote_window`, `quote_close`, `quote_hound`).
- `videos/footage-01.mp4`: a 30 s teaser cut from the key art and the scene's own sounds (`scripts/build-trailer.py`, upscaled to
  1080p). It is **not gameplay**: the first-three-seconds rule of the Foundation's trailer ask needs a recording. Replace it.
- `tools/`: the scripts to regenerate everything (below), including `capture_play.py` for gameplay takes through the Explorer MCP.

## Regenerate (run from the scene root, in this order)

```
B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b -P promote/tools/render_shots.py -- preview            # read promote/images/preview/*.png first
$B -b -P promote/tools/render_shots.py -- final hero gate     # one or two shots per command: a final took 10-60 min here
$B -b -P promote/tools/render_shots.py -- keyart              # the two key-art plates (3 h for the pair on this machine)
python3 promote/tools/make_logo.py
python3 promote/tools/compose_social.py
python3 promote/tools/build_kit.py                            # kit-data.js, copy.md, footage-shotlist.md
python3 promote/tools/research_venues.py reddit Mothman cryptids IndieDev   # top posts, for modelled_on
```

`render_shots.py` rebuilds each shot's region from `assets/scene/main.composite` (trees, bunkers, fence, paw prints, the cabin's
boxes) plus the flashlight, the cabin bulb and `assets/Models/mothman.glb`; the gate sign is rebuilt as `src/index.ts` draws it.
The finals are slow because every shot carries the whole 192 m ground mesh and dozens of trees; previews take seconds.

## Notes

- **Audience**: assumed, not confirmed. The GDD's audience is the agent's proposal from the owner's research sheet. The page's
  Audience panel lists the assumptions to correct first.
- **r/Cryptozoology bans Mothman posts** (rule 8, read on a mirror site 2026-11-06). It is kept as a listening venue with no post.
  Every subreddit rule here was read on subriff.com mirrors; re-read the live sidebars before posting (`[CHECK]` marks).
- **Placeholders**: the footage posts and the Shorts need in-world recordings; `videos/footage-01.mp4` is a key-art teaser, not
  gameplay; the clean in-world screenshot and the gameplay stills in the Foundation's package are shot-list items.
- **Could not render**: nothing was skipped, but the Mothman in the stills is the un-rigged `mothman.glb` in its rest pose; the
  animated, eye-lit version only exists in the Explorer. Avatars never appear (none are in the design).
- **Secrets kept out**: the telepathic passage, what he is after, bunker 7's step and the walk out. No line from `VOICE` is quoted.
- **Inspirations kept out**: John Keel's book and the 2002 film are named nowhere; the copy uses the public record only.
- **`[CHECK]` items**: the game's length (launch-03: the GDD has no measured time); the subreddit rules and flair lists; the
  Decentraland Discord channel for scene posts; the three YouTube channels; `modelled_on` posts for r/Mothman and r/cryptids
  (their feeds were rate-limited this session).
- **Scene metadata**: `display.description` sets a mood only; `copy.md` opens with the proposed rewrite (`listing.short`, 152
  characters) and the long description. Tags are `game` and `art`. The scene thumbnail (`assets/Images/thumbnail.png`) is a
  composed cover, not a gameplay screenshot; `images/social/keyart_1920x1080.png` is a candidate once it is checked against the
  thumbnail spec (16:9, under 1 MB, text inside the central square). This kit never overwrites the thumbnail.
- **Marketing package (Foundation checklist)**: name: flagged below · tags: done (`scene.json`) · jump-in link: missing (not
  deployed) · short and long description: in the kit (`copy.md`) · scene thumbnail: done (own cover) · clean in-world screenshot:
  shot list · social square: in the kit · gameplay stills: shot list · trailer 16:9 under 30 s with people in motion in the first
  three seconds: shot list (the teaser here does not satisfy it) · vertical cut: shot list · captions: the teaser has them.

## Rights

- **Title**: "Mothman" is a folklore name, but several other indie horror games carry it ("Mothman - Indie Horror Game",
  a "Mothman" Steam Next Fest demo, "Mothman | Retro Survival Horror" on YouTube, found 2026-11-06). Possible conflict; this
  kit does not clear it. The 1966 witnesses were real people: the copy names Newell Partridge and his dog as the public
  record does; `design/gdd.md` leaves real-versus-fictional names open.
- **Models**: `assets/Models/mothman.glb` carries a Tripo material name, so it was generated with an AI model tool; check its
  licence allows promotional use. Trees and furniture are Creator Hub asset-pack items. The rest is the owner's.
- **Fonts**: Special Elite (Apache 2.0) and Kalam (SIL OFL), licences in `assets/fonts/`.
- **Audio in the teaser**: the scene's own clips in `assets/audio/`; their provenance is not recorded in `design/references.md`.
  Add credits to the scene description if any are CC BY.
- Decentraland is named in full and never as an endorser; its logo is not used. Brand rules and the Content Policy:
  https://drive.google.com/drive/folders/1qX5snvvTxc-8fmX9RepW7BcPfWio1la7 and https://decentraland.org/content.

// dl-asset.mjs — download Creator Hub asset-pack items by id. Run from the scene root:
//   node scripts/dl-asset.mjs <asset-id> [<asset-id> ...]
import { mkdir, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'
const BASE = 'https://builder-items.decentraland.org'
const SKIP = new Set(['thumbnail.png', 'preview.webp'])
const { assetPacks } = await (await fetch(`${BASE}/asset-packs/latest/catalog.json`)).json()
for (const id of process.argv.slice(2)) {
  const asset = assetPacks.flatMap((p) => p.assets).find((a) => a.id === id)
  if (!asset) { console.error(`no catalog asset with id ${id}`); continue }
  const dir = `assets/asset-packs/${asset.name.trim().replaceAll(' ', '_').toLowerCase()}`
  for (const [rel, hash] of Object.entries(asset.contents)) {
    if (SKIP.has(rel)) continue
    const res = await fetch(`${BASE}/contents/${hash}`)
    if (!res.ok) throw new Error(`${rel}: HTTP ${res.status}`)
    const out = `${dir}/${rel}`
    await mkdir(dirname(out), { recursive: true })
    await writeFile(out, Buffer.from(await res.arrayBuffer()))
    console.log(out)
  }
}

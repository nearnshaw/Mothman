"""
Road surface for the Unity Explorer. The earlier pass feathered the shoulders with vertex-colour alpha (COLOR_0), which
the Bevy editor honours and the Unity renderer ignores: in-world the road had hard stair-stepped edges along the 0.4 m
grid. This build uses no vertex colours at all:
  - the gravel is an opaque mesh whose outline follows the exact road edge (marching-squares clipping of the grid), and
  - a thin 'shoulder' ring straddles that edge, textured with soil whose alpha is baked into the texture (u across the
    ring, v along the road), so the hard edge is hidden under soft soil that fades out on both sides.
Deterministic. Writes assets/Images/woodland-v3/road-shoulder.png and assets/Models/forest-tracks-v3.glb (the file the
composite already references). Pure Python: no Blender needed.
"""
import math, json, struct
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path.cwd()
s = (ROOT / 'scripts/gen-forest.py').read_text()
env = {'math': math, 'W': 192, 'D': 192, 'layout': {}}
exec(s[s.index('spawn = (4.0'):s.index('ROAD_MAT =')], env)
lines = env['polylines']

# ---- signed distance to the road edge, and the arc length along the nearest path ------------------------------------
step = 0.4
grid = np.arange(0, 192 + step / 2, step)
X, Z = np.meshgrid(grid, grid)
dist = np.full_like(X, 1e6)   # signed: negative inside the road
along = np.zeros_like(X)      # arc length along the nearest path, metres
for idx, pl in enumerate(lines):
    half = 1.8 if idx == 0 else 1.325
    cum = 0.0
    for a, b in zip(pl, pl[1:]):
        vx, vz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(vx, vz) or 1e-9
        t = np.clip(((X - a[0]) * vx + (Z - a[1]) * vz) / (L * L), 0, 1)
        d = np.hypot(X - a[0] - t * vx, Z - a[1] - t * vz) - half
        closer = d < dist
        dist = np.where(closer, d, dist)
        along = np.where(closer, cum + t * L, along)
        cum += L

# ---- the shoulder texture: soil with baked alpha, 1 m across (u, clamped) by 3 m along (v, repeating) ----------------
r = np.random.default_rng(1966)
TW, TH = 512, 1024
def pnoise(cv, cu):
    """Value noise, periodic along v (rows) so the strip tiles along the road."""
    g = r.random((cv, cu + 1))
    yy = np.arange(TH) / TH * cv; xx = np.arange(TW) / (TW - 1) * cu
    y0 = np.floor(yy).astype(int); fy = yy - y0; y1 = (y0 + 1) % cv
    x0 = np.minimum(np.floor(xx).astype(int), cu - 1); fx = xx - x0; x1 = x0 + 1
    fy = (fy * fy * (3 - 2 * fy))[:, None]; fx = (fx * fx * (3 - 2 * fx))[None, :]
    top = g[np.ix_(y0, x0)] * (1 - fx) + g[np.ix_(y0, x1)] * fx
    bot = g[np.ix_(y1, x0)] * (1 - fx) + g[np.ix_(y1, x1)] * fx
    return top * (1 - fy) + bot * fy
u = np.arange(TW)[None, :] / (TW - 1) * np.ones((TH, 1))
n_coarse = pnoise(12, 4); n_mid = pnoise(48, 16); n_fine = pnoise(256, 128); n_grain = pnoise(512, 256)
loam = np.array([81.5, 72.1, 49.4]); gravel = np.array([140.1, 128.7, 105.9])
shade = 0.85 + 0.3 * n_mid + 0.25 * (n_fine - 0.5) + 0.2 * (n_grain - 0.5)   # averages to the ground texture's tone
rgb = loam[None, None, :] * shade[:, :, None]
grains = n_grain > 0.84 + 0.3 * np.clip((u - 0.25) / 0.45, 0, 1)   # gravel bits in the soil, thinning out away from the road
rgb = np.where(grains[:, :, None], gravel[None, None, :] * (0.8 + 0.4 * n_fine)[:, :, None], rgb)
bump = 1 - (2 * u - 1) ** 2                 # 1 at the road edge (u = 0.5), 0 at both ends of the strip
alpha = np.clip(bump * 1.45 - 0.3 + 0.55 * (n_coarse - 0.5) + 0.35 * (n_mid - 0.5) + 0.15 * (n_fine - 0.5), 0, 1)
alpha *= np.clip(bump * 3, 0, 1)            # exactly transparent at the strip's ends
img = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
Image.fromarray(img, 'RGBA').save(ROOT / 'assets/Images/woodland-v3/road-shoulder.png')

# ---- meshes --------------------------------------------------------------------------------------------------------
BAND = 0.5   # the shoulder strip spans dist in [-BAND, +BAND]
def file_pos(x, z, h):
    """gen-forest (x, z) → the glTF coordinates Blender's exporter produced for the ground: (96-x, h, z-96)."""
    return (96 - x, h, z - 96)

class Mesh:
    def __init__(self): self.v = []; self.uv = []; self.idx = {}; self.tris = []
    def vertex(self, key, pos, uv):
        if key not in self.idx: self.idx[key] = len(self.v); self.v.append(pos); self.uv.append(uv)
        return self.idx[key]
    def fan(self, ids):
        for k in range(1, len(ids) - 1): self.tris.append((ids[0], ids[k], ids[k + 1]))

road = Mesh(); ring = Mesh()
n = len(grid)
corners = [(0, 0), (1, 0), (1, 1), (0, 1)]   # counter-clockwise seen from above in (x, z)
for j in range(n - 1):
    for i in range(n - 1):
        cs = [(i + di, j + dj) for di, dj in corners]
        ds = [dist[zz, xx] for xx, zz in cs]
        if min(ds) <= 0:
            # Clip the cell to the road (dist <= 0): corners inside stay, crossings land exactly on the edge.
            poly = []
            for k in range(4):
                (xa, za), da = cs[k], ds[k]; (xb, zb), db = cs[(k + 1) % 4], ds[(k + 1) % 4]
                if da <= 0:
                    x, z = grid[xa], grid[za]
                    poly.append(road.vertex(('c', xa, za), file_pos(x, z, 0.006), (x / 3, -z / 3)))
                if (da <= 0) != (db <= 0):
                    t = da / (da - db); x = grid[xa] + (grid[xb] - grid[xa]) * t; z = grid[za] + (grid[zb] - grid[za]) * t
                    key = ('e',) + tuple(sorted([(xa, za), (xb, zb)]))
                    poly.append(road.vertex(key, file_pos(x, z, 0.006), (x / 3, -z / 3)))
            if len(poly) >= 3: road.fan(poly)
        if min(abs(d) for d in ds) < BAND:
            ids = []
            for (xx, zz), d in zip(cs, ds):
                x, z = grid[xx], grid[zz]
                ids.append(ring.vertex(('c', xx, zz), file_pos(x, z, 0.012), (float(np.clip((d + BAND) / (2 * BAND), 0, 1)), -along[zz, xx] / 3)))
            ring.fan(ids)

# ---- GLB -------------------------------------------------------------------------------------------------------------
blob = bytearray(); views = []; accessors = []
def view(data: bytes, target):
    blob.extend(b'\0' * ((-len(blob)) % 4)); views.append({'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(data), 'target': target}); blob.extend(data); return len(views) - 1
def accessor(arr, ctype, atype, target, minmax=False):
    a = {'bufferView': view(arr.tobytes(), target), 'componentType': ctype, 'count': len(arr), 'type': atype}
    if minmax: a['min'] = arr.min(axis=0).tolist(); a['max'] = arr.max(axis=0).tolist()
    accessors.append(a); return len(accessors) - 1
def primitive(m, material):
    v = np.array(m.v, np.float32); uv = np.array(m.uv, np.float32); nrm = np.tile(np.array([[0, 1, 0]], np.float32), (len(v), 1))
    idx = np.array(m.tris, np.uint32).reshape(-1)
    return {'attributes': {'POSITION': accessor(v, 5126, 'VEC3', 34962, True), 'NORMAL': accessor(nrm, 5126, 'VEC3', 34962), 'TEXCOORD_0': accessor(uv, 5126, 'VEC2', 34962)},
            'indices': accessor(idx, 5125, 'SCALAR', 34963), 'material': material}
prims = [primitive(road, 0), primitive(ring, 1)]
g = {
    'asset': {'version': '2.0', 'generator': 'scripts/build-road-v4.py'},
    'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0, 'name': 'Unified road network'}],
    'meshes': [{'name': 'Unified road network', 'primitives': prims}],
    'materials': [
        {'name': 'Continuous gravel', 'doubleSided': True, 'normalTexture': {'index': 0},
         'pbrMetallicRoughness': {'baseColorTexture': {'index': 1}, 'metallicFactor': 0, 'roughnessFactor': 0.9}},
        {'name': 'Soil shoulder', 'doubleSided': True, 'alphaMode': 'BLEND',
         'pbrMetallicRoughness': {'baseColorTexture': {'index': 2}, 'metallicFactor': 0, 'roughnessFactor': 0.95}}],
    'textures': [{'sampler': 0, 'source': 0}, {'sampler': 0, 'source': 1}, {'sampler': 1, 'source': 2}],
    'samplers': [{'magFilter': 9729, 'minFilter': 9987}, {'magFilter': 9729, 'minFilter': 9987, 'wrapS': 33071, 'wrapT': 10497}],
    'images': [{'name': 'track-normal', 'uri': '../Images/woodland-v3/445e0c98cc498829.png'},
               {'name': 'track-aggregate', 'uri': '../Images/woodland-v3/f31003c3b33fb1dd.png'},
               {'name': 'road-shoulder', 'uri': '../Images/woodland-v3/road-shoulder.png'}],
    'bufferViews': views, 'accessors': accessors, 'buffers': [{'byteLength': len(blob)}]}
js = json.dumps(g, separators=(',', ':')).encode(); js += b' ' * ((-len(js)) % 4); blob.extend(b'\0' * ((-len(blob)) % 4))
out = ROOT / 'assets/Models/forest-tracks-v3.glb'
out.write_bytes(struct.pack('<III', 0x46546C67, 2, 28 + len(js) + len(blob)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(blob), 0x004E4942) + bytes(blob))
print(f'road: {len(road.v)} verts, {len(road.tris)} tris; shoulder: {len(ring.v)} verts, {len(ring.tris)} tris; {out.stat().st_size // 1024} KiB')

"""Paper backgrounds for the document UI (src/hud.tsx): an aged sheet for typed pages and a notebook leaf for
handwritten ones. Deterministic; writes assets/images/paper-typed.png and paper-hand.png (1024 x 640, RGBA)."""
import numpy as np
from PIL import Image, ImageFilter
from pathlib import Path
W, H = 1024, 640
r = np.random.default_rng(1966)
def noise(cells):
    g = r.random((cells, int(cells * W / H) + 1))
    return np.asarray(Image.fromarray((g * 255).astype('uint8')).resize((W, H), Image.Resampling.BICUBIC), dtype=float) / 255
y, x = np.mgrid[0:H, 0:W]; u, v = x / W, y / H
edge = np.minimum.reduce([u, 1 - u, v * 1.6, (1 - v) * 1.6])
def sheet(base, grain, stain, out):
    tone = 1 - 0.22 * np.clip(1 - edge * 6, 0, 1) ** 1.6           # darker, dirtier toward the edges
    tone *= 0.92 + 0.08 * noise(6) + 0.05 * (noise(140) - 0.5) * grain  # cloudiness and fibre
    rgb = np.array(base)[None, None, :] * tone[:, :, None]
    blot = noise(30)
    for i in range(stain):                                            # foxing: soft irregular brown blotches, one faint cup ring
        cx, cy, rad = r.random() * W, r.random() * H, 40 + r.random() * 90
        d = np.hypot(x - cx, y - cy) / rad * (0.8 + 0.5 * blot)
        mark = np.exp(-(d / 0.9) ** 2) * 0.16 if i else np.exp(-((d - 0.9) / 0.12) ** 2) * 0.22
        rgb = rgb * (1 - mark[:, :, None] * np.array([0.2, 0.38, 0.6])[None, None, :])
    return rgb
# typed: a yellowed sheet, a soft fold across the middle
rgb = sheet([228, 216, 186], 1.0, 4, 'typed')
fold = np.exp(-((v - 0.5) / 0.02) ** 2) * 0.06 + np.clip((0.5 - v) * 0.1, 0, 0.04)
rgb = rgb * (1 - fold[:, :, None])
Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.full((H, W), 255)]).astype(np.uint8), 'RGBA').save(Path('assets/images/paper-typed.png'))
# hand: a paler leaf torn from a reporter's pad, a red margin line and the holes of the spiral along the top
rgb = sheet([236, 232, 216], 0.6, 2, 'hand')
margin = np.exp(-((x - 118) / 1.6) ** 2)
rgb = rgb * (1 - margin[:, :, None] * np.array([0.05, 0.55, 0.5])[None, None, :])
alpha = np.full((H, W), 255.0)
tear = (noise(40)[0] - 0.5) * 7 + (noise(9)[0] - 0.5) * 5              # a ragged top edge
alpha[y < 12 + tear[None, :]] = 0
for cx in range(64, W, 64):                                           # spiral holes
    alpha[np.hypot(x - cx, y - 30) < 9] = 0
    rgb[np.abs(np.hypot(x - cx, y - 30) - 10) < 1.5] *= 0.75
Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8), 'RGBA').save(Path('assets/images/paper-hand.png'))
print('paper textures written')

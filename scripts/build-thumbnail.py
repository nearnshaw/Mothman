"""
Scene cover (scene.json display.navmapThumbnail): 1920 x 1080, the subject and the title inside the central
1080 x 1080 square the platform crops to, under 1 MB. Deterministic; writes assets/Images/thumbnail.png.
Composition: the plant road at night under the flashlight beam, him standing on it with his eyes lit, moths in the beam.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path

W, H = 1920, 1080
VP = (980, 505)  # the road's vanishing point
r = np.random.default_rng(1966)
Y, X = np.mgrid[0:H, 0:W].astype(float)

def noise(cells_x, cells_y=None):
    cells_y = cells_y or max(2, int(cells_x * H / W))
    g = (r.random((cells_y, cells_x)) * 255).astype('uint8')
    return np.asarray(Image.fromarray(g).resize((W, H), Image.Resampling.BICUBIC), dtype=float) / 255

# ---- sky, stars, horizon haze --------------------------------------------------------------------------------------
t = np.clip(Y / VP[1], 0, 1)
sky = np.array([5, 7, 16])[None, None, :] * (1 - t[:, :, None]) + np.array([24, 28, 44])[None, None, :] * t[:, :, None]
img = sky.copy()
stars = np.zeros((H, W))
for _ in range(900):
    sx, sy = int(r.random() * W), int(r.random() ** 1.6 * VP[1] * 0.95)
    b = r.random() ** 2
    stars[sy, sx] = 0.4 + 0.6 * b
stars = np.asarray(Image.fromarray((stars * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8)), dtype=float) / 255
img += (stars * 1.6)[:, :, None] * np.array([190, 200, 230])[None, None, :]
haze = np.exp(-((Y - VP[1]) / 150) ** 2) * (Y < VP[1] + 40)
img += haze[:, :, None] * np.array([14, 17, 24])[None, None, :]

# ---- ground and the road -------------------------------------------------------------------------------------------
ground = Y >= VP[1]
depth = np.clip((Y - VP[1]) / (H - VP[1]), 0, 1)          # 0 at the horizon, 1 at the bottom
loam = np.array([46, 40, 27])[None, None, :] * (0.7 + 0.5 * noise(90) + 0.25 * noise(400))[:, :, None]
bend = -170 * (1 - depth) ** 2                              # the road swings left into the dark
centre = VP[0] + bend
halfw = 40 + 640 * depth ** 1.15
edge = (np.abs(X - centre) - halfw) / (6 + 40 * depth)      # soft, slightly ragged edge
edge += (noise(60) - 0.5) * 1.2
road_m = np.clip(0.5 - edge, 0, 1) * ground
gravel = np.array([72, 66, 54])[None, None, :] * (0.72 + 0.45 * noise(160) + 0.3 * noise(900) * depth[:, :, None][:, :, 0])[:, :, None]
rut = 1 - 0.18 * np.exp(-((np.abs(X - centre) / np.maximum(halfw, 1) - 0.5) / 0.14) ** 2)
gravel *= rut[:, :, None]
img = np.where(ground[:, :, None], loam * (1 - road_m[:, :, None]) + gravel * road_m[:, :, None], img)
# fog with distance
fog = np.array([26, 30, 42])[None, None, :]
fogk = np.where(ground, (1 - depth) ** 2.2 * 0.9, 0)
img = img * (1 - fogk[:, :, None]) + fog * fogk[:, :, None]

base = Image.fromarray(np.clip(img, 0, 255).astype('uint8'))

# ---- trees: silhouettes, far to near, fogged by depth ------------------------------------------------------------
trees = []
for _ in range(150):
    d = r.random() ** 0.8                                     # 0 near, 1 far
    side = -1 if r.random() < 0.5 else 1
    yb = VP[1] + (H - VP[1]) * (1 - d) ** 1.1 * 1.05          # base on the ground
    dep = np.clip((yb - VP[1]) / (H - VP[1]), 0, 1)
    hw = 40 + 640 * dep ** 1.15
    cx = VP[0] - 170 * (1 - dep) ** 2 + side * (hw + 40 + r.random() * 500 * (0.3 + dep))
    trees.append((d, cx, yb, r.random() < 0.72, r.random()))
trees.sort(key=lambda t: -t[0])
layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
dr = ImageDraw.Draw(layer)
for d, cx, yb, pine, seed in trees:
    s = 0.12 + 1.6 * (1 - d) ** 1.6                           # size by distance
    f = 1 - (1 - d) ** 1.4                                    # fog mix
    col = tuple(int(a * (1 - f) + b * f) for a, b in zip((10, 9, 8), (30, 34, 46)))
    if pine:
        h = 380 * s * (0.8 + 0.5 * seed)
        wmax = 95 * s * (0.8 + 0.4 * seed)
        for k in range(6):
            yk = yb - h * (k / 6)
            wk = wmax * (1 - k / 6) * (0.75 + 0.5 * ((seed * 7 + k) % 1))
            hk = h / 6 * 1.6
            dr.polygon([(cx - wk, yk), (cx + wk, yk), (cx, yk - hk)], fill=col)
        dr.rectangle([cx - 5 * s, yb - 25 * s, cx + 5 * s, yb], fill=col)
    else:
        h = 420 * s * (0.8 + 0.5 * seed)
        tw = 7 * s * (0.7 + 0.6 * seed)
        bark = tuple(int(a * (1 - f) + b * f) for a, b in zip((58, 52, 46), (30, 34, 46)))
        dr.line([(cx, yb), (cx + 10 * s, yb - h)], fill=bark, width=max(1, int(tw * 2)))
        for k in range(4):
            y0 = yb - h * (0.45 + 0.5 * k / 4)
            ang = (-1 if k % 2 else 1) * (0.9 + 0.5 * ((seed * 13 + k) % 1))
            L = (90 - 9 * k) * s
            dr.line([(cx + 10 * s * (yb - y0) / h, y0), (cx + math.sin(ang) * L, y0 - math.cos(ang) * L * 0.9)], fill=bark, width=max(1, int(tw * 0.9)))
base = Image.alpha_composite(base.convert('RGBA'), layer)

# ---- the flashlight beam: a cone from the bottom centre, warm, falling off with distance -------------------------
arr = np.asarray(base).astype(float)[:, :, :3]
ox, oy = 960, H + 260
ang = np.arctan2(X - ox, oy - Y)
dist = np.hypot(X - ox, oy - Y)
cone = np.exp(-(np.abs(ang) / 0.27) ** 2.6) * np.exp(-dist / 1050) * (dist > 0)
cone *= 0.75 + 0.25 * noise(30)                              # dust in the air
lit = 0.5 + 1.7 * cone
arr = arr * lit[:, :, None] + (cone * 28)[:, :, None] * np.array([1.0, 0.9, 0.7])[None, None, :]

# ---- him: on the road, wings half open, eyes lit -----------------------------------------------------------------
img2 = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).convert('RGBA')
fig = Image.new('RGBA', (W, H), (0, 0, 0, 0))
fd = ImageDraw.Draw(fig)
mx, my, S = 915, 690, 0.72                                     # feet on the road, scale
ink = (8, 7, 10, 255)
def wing(sign):
    pts = []
    for i in range(0, 11):
        u = i / 10
        # upper edge: from the shoulder out and up, then the ragged lower edge back in
        # a cape of wing spread wide behind him: the upper edge lifts a little, then runs out to a pointed tip
        pts.append((mx + sign * (24 + 250 * u) * S, my - (235 + 90 * math.sin(u * math.pi) - 25 * u) * S))
    for i in range(5, -1, -1):
        u = i / 5
        scallop = 20 * (1 - abs(math.sin(u * math.pi * 2.5)))
        pts.append((mx + sign * (30 + 230 * u) * S, my - (80 + 130 * u - scallop) * S))
    fd.polygon(pts, fill=ink)
wing(-1); wing(1)
fd.ellipse([mx - 46 * S, my - 250 * S, mx + 46 * S, my - 40 * S], fill=ink)      # torso
fd.polygon([(mx - 38 * S, my - 70 * S), (mx + 38 * S, my - 70 * S), (mx + 24 * S, my), (mx - 24 * S, my)], fill=ink)  # legs
fd.ellipse([mx - 34 * S, my - 300 * S, mx + 34 * S, my - 226 * S], fill=ink)     # head, low between the shoulders
soft = fig.filter(ImageFilter.GaussianBlur(1.2))
img2 = Image.alpha_composite(img2, soft)
rim = np.asarray(fig.split()[3]).astype(float) / 255
below = np.asarray(fig.split()[3].filter(ImageFilter.GaussianBlur(5)).transform((W, H), Image.Transform.AFFINE, (1, 0, 0, 0, 1, 6))).astype(float) / 255
rimk = np.clip(rim - below, 0, 1) * np.clip((Y - (my - 240 * S)) / (160 * S), 0, 1) * 0.9
rimlayer = Image.fromarray(np.dstack([np.full((H, W), 150), np.full((H, W), 135), np.full((H, W), 105), (rimk * 255)]).astype('uint8'), 'RGBA')
img2 = Image.alpha_composite(img2, rimlayer)
# the eyes and their bloom
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for ex in (mx - 14 * S, mx + 14 * S):
    gd.ellipse([ex - 4, my - 268 * S - 4, ex + 4, my - 268 * S + 4], fill=(255, 60, 40, 255))
bloom = glow.filter(ImageFilter.GaussianBlur(14))
img2 = Image.alpha_composite(img2, Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 0)), bloom, 0.9))
img2 = Image.alpha_composite(img2, bloom.filter(ImageFilter.GaussianBlur(40)))
img2 = Image.alpha_composite(img2, glow.filter(ImageFilter.GaussianBlur(1.5)))

# ---- moths in the beam ---------------------------------------------------------------------------------------------
moth = Image.open('assets/images/moth.png').convert('RGBA')
for _ in range(26):
    d = r.random()
    px = 960 + (r.random() - 0.5) * (220 + 620 * (1 - d))
    py = 560 + 420 * (1 - d) ** 1.3 * r.random()
    sz = int(10 + 44 * (1 - d) ** 2)
    m = moth.resize((sz, sz)).rotate(r.random() * 360, resample=Image.Resampling.BICUBIC)
    a = m.split()[3].point(lambda v: int(v * (0.25 + 0.45 * (1 - d))))
    tint = Image.new('RGBA', m.size, (215, 205, 180, 0)); tint.putalpha(a)
    img2.alpha_composite(tint, (int(px - sz / 2), int(py - sz / 2)))

# ---- vignette and the title ----------------------------------------------------------------------------------------
arr = np.asarray(img2).astype(float)[:, :, :3]
vig = 1 - 0.55 * np.clip(np.hypot((X - 960) / 1100, (Y - 540) / 700) ** 2.2, 0, 1)
arr *= vig[:, :, None]
out = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).convert('RGBA')
td = ImageDraw.Draw(out)
title = ImageFont.truetype('assets/fonts/SpecialElite-Regular.ttf', 168)
sub = ImageFont.truetype('assets/fonts/SpecialElite-Regular.ttf', 38)
shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.text((962, 176), 'MOTHMAN', font=title, fill=(0, 0, 0, 230), anchor='mm')
out = Image.alpha_composite(out, shadow.filter(ImageFilter.GaussianBlur(10)))
td = ImageDraw.Draw(out)
td.text((960, 172), 'MOTHMAN', font=title, fill=(226, 214, 186, 255), anchor='mm')
td.text((960, 268), 'POINT PLEASANT, W.VA.  -  NOVEMBER 1966', font=sub, fill=(170, 165, 150, 235), anchor='mm')

out = out.convert('RGB')
p = Path('assets/Images/thumbnail.png')
out.save(p, optimize=True)
if p.stat().st_size > 1_000_000:
    out.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(p, optimize=True)
print(p, p.stat().st_size, 'bytes', out.size)

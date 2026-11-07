"""
Teaser trailer (no gameplay capture: the Explorer could not be driven from here), built from the scene's key art and
its own sounds. 1280 x 720, 24 fps, 30 s. Frames go to a scratch folder, ffmpeg assembles the video with the audio mix.
Usage: python3 scripts/build-trailer.py <frames-dir> <out.mp4>
"""
import math, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path

FRAMES = Path(sys.argv[1]); OUT = Path(sys.argv[2]); FRAMES.mkdir(parents=True, exist_ok=True)
W, H, FPS, DUR = 1280, 720, 24, 30
VP = (655, 337)
r = np.random.default_rng(1966)
Y, X = np.mgrid[0:H, 0:W].astype(float)
def noise(cells_x, cells_y=None):
    cells_y = cells_y or max(2, int(cells_x * H / W))
    g = (r.random((cells_y, cells_x)) * 255).astype('uint8')
    return np.asarray(Image.fromarray(g).resize((W, H), Image.Resampling.BICUBIC), dtype=float) / 255

# ---- the static scene: sky, road, trees (same recipe as build-thumbnail.py, at 720p) -------------------------------
t = np.clip(Y / VP[1], 0, 1)
img = np.array([5, 7, 16])[None, None, :] * (1 - t[:, :, None]) + np.array([24, 28, 44])[None, None, :] * t[:, :, None]
stars = np.zeros((H, W))
for _ in range(700):
    stars[int(r.random() ** 1.6 * VP[1] * 0.95), int(r.random() * W)] = 0.4 + 0.6 * r.random() ** 2
stars = np.asarray(Image.fromarray((stars * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.7)), dtype=float) / 255
img += (stars * 1.6)[:, :, None] * np.array([190, 200, 230])[None, None, :]
img += (np.exp(-((Y - VP[1]) / 100) ** 2) * (Y < VP[1] + 30))[:, :, None] * np.array([14, 17, 24])[None, None, :]
ground = Y >= VP[1]
depth = np.clip((Y - VP[1]) / (H - VP[1]), 0, 1)
loam = np.array([46, 40, 27])[None, None, :] * (0.7 + 0.5 * noise(60) + 0.25 * noise(260))[:, :, None]
centre = VP[0] - 115 * (1 - depth) ** 2
halfw = 27 + 430 * depth ** 1.15
edge = (np.abs(X - centre) - halfw) / (4 + 27 * depth) + (noise(40) - 0.5) * 1.2
road_m = np.clip(0.5 - edge, 0, 1) * ground
gravel = np.array([72, 66, 54])[None, None, :] * (0.72 + 0.45 * noise(110) + 0.3 * noise(600) * depth)[:, :, None]
gravel *= (1 - 0.18 * np.exp(-((np.abs(X - centre) / np.maximum(halfw, 1) - 0.5) / 0.14) ** 2))[:, :, None]
img = np.where(ground[:, :, None], loam * (1 - road_m[:, :, None]) + gravel * road_m[:, :, None], img)
fogk = np.where(ground, (1 - depth) ** 2.2 * 0.9, 0)
img = img * (1 - fogk[:, :, None]) + np.array([26, 30, 42])[None, None, :] * fogk[:, :, None]
base = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')
layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(layer)
trees = []
for _ in range(150):
    d = r.random() ** 0.8; side = -1 if r.random() < 0.5 else 1
    yb = VP[1] + (H - VP[1]) * (1 - d) ** 1.1 * 1.05
    dep = np.clip((yb - VP[1]) / (H - VP[1]), 0, 1); hw = 27 + 430 * dep ** 1.15
    cx = VP[0] - 115 * (1 - dep) ** 2 + side * (hw + 27 + r.random() * 330 * (0.3 + dep))
    trees.append((d, cx, yb, r.random() < 0.72, r.random()))
for d, cx, yb, pine, seed in sorted(trees, key=lambda q: -q[0]):
    s = (0.12 + 1.6 * (1 - d) ** 1.6) * 0.667; f = 1 - (1 - d) ** 1.4
    col = tuple(int(a * (1 - f) + b * f) for a, b in zip((10, 9, 8), (30, 34, 46)))
    if pine:
        h = 380 * s * (0.8 + 0.5 * seed); wmax = 95 * s * (0.8 + 0.4 * seed)
        for k in range(6):
            yk = yb - h * (k / 6); wk = wmax * (1 - k / 6) * (0.75 + 0.5 * ((seed * 7 + k) % 1))
            dr.polygon([(cx - wk, yk), (cx + wk, yk), (cx, yk - h / 6 * 1.6)], fill=col)
        dr.rectangle([cx - 5 * s, yb - 25 * s, cx + 5 * s, yb], fill=col)
    else:
        h = 420 * s * (0.8 + 0.5 * seed); tw = 7 * s * (0.7 + 0.6 * seed)
        bark = tuple(int(a * (1 - f) + b * f) for a, b in zip((58, 52, 46), (30, 34, 46)))
        dr.line([(cx, yb), (cx + 10 * s, yb - h)], fill=bark, width=max(1, int(tw * 2)))
        for k in range(4):
            y0 = yb - h * (0.45 + 0.5 * k / 4); ang = (-1 if k % 2 else 1) * (0.9 + 0.5 * ((seed * 13 + k) % 1)); L = (90 - 9 * k) * s
            dr.line([(cx + 10 * s * (yb - y0) / h, y0), (cx + math.sin(ang) * L, y0 - math.cos(ang) * L * 0.9)], fill=bark, width=max(1, int(tw * 0.9)))
base = np.asarray(Image.alpha_composite(base, layer)).astype(float)[:, :, :3]
dust = 0.75 + 0.25 * noise(20)
moth = Image.open('assets/images/moth.png').convert('RGBA')
title_font = ImageFont.truetype('assets/fonts/SpecialElite-Regular.ttf', 118)
cap_font = ImageFont.truetype('assets/fonts/SpecialElite-Regular.ttf', 34)
small_font = ImageFont.truetype('assets/fonts/SpecialElite-Regular.ttf', 24)

# ---- the figure -------------------------------------------------------------------------------------------------------
def figure(mx, my, S, spread, eyes):
    """Returns (silhouette RGBA, eye glow RGBA). `spread` 0..1 opens the wings."""
    fig = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fig); ink = (8, 7, 10, 255)
    for sign in (-1, 1):
        pts = []
        for i in range(11):
            u = i / 10
            pts.append((mx + sign * (24 + 250 * u * (0.25 + 0.75 * spread)) * S, my - (235 + 90 * math.sin(u * math.pi) * spread - 25 * u + 120 * u * (1 - spread)) * S))
        for i in range(5, -1, -1):
            u = i / 5; scallop = 20 * (1 - abs(math.sin(u * math.pi * 2.5)))
            pts.append((mx + sign * (30 + 230 * u * (0.25 + 0.75 * spread)) * S, my - (80 + 130 * u - scallop) * S))
        fd.polygon(pts, fill=ink)
    fd.ellipse([mx - 46 * S, my - 250 * S, mx + 46 * S, my - 40 * S], fill=ink)
    fd.polygon([(mx - 38 * S, my - 70 * S), (mx + 38 * S, my - 70 * S), (mx + 24 * S, my), (mx - 24 * S, my)], fill=ink)
    fd.ellipse([mx - 34 * S, my - 300 * S, mx + 34 * S, my - 226 * S], fill=ink)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    rad = max(1.5, 4 * S)
    for ex in (mx - 14 * S, mx + 14 * S):
        gd.ellipse([ex - rad, my - 268 * S - rad, ex + rad, my - 268 * S + rad], fill=(255, 60, 40, int(255 * eyes)))
    return fig, glow

def caption(canvas, text, alpha, y=600, font=cap_font, color=(226, 214, 186)):
    if alpha <= 0.01: return canvas
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((W / 2 + 2, y + 3), text, font=font, fill=(0, 0, 0, int(220 * alpha)), anchor='mm')
    canvas = Image.alpha_composite(canvas, sh.filter(ImageFilter.GaussianBlur(6)))
    tx = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(tx).text((W / 2, y), text, font=font, fill=color + (int(255 * alpha),), anchor='mm')
    return Image.alpha_composite(canvas, tx)

def fade(t, a, b, c, d):
    """0 before a, up to 1 by b, 1 until c, down to 0 by d."""
    if t < a or t > d: return 0.0
    if t < b: return (t - a) / max(1e-6, b - a)
    if t > c: return (d - t) / max(1e-6, d - c)
    return 1.0

# moths: a dozen orbiting the beam's middle distance
MOTHS = [(r.random() * 6.3, (2.2 + r.random() * 2.2) * (1 if r.random() < 0.5 else -1), 40 + r.random() * 90, 0.35 + r.random() * 0.65, r.random() * 6) for _ in range(12)]

BEAM_ON, BEAM_OFF = 5.0, 23.2
vig = 1 - 0.55 * np.clip(np.hypot((X - W / 2) / (W * 0.57), (Y - H / 2) / (H * 0.65)) ** 2.2, 0, 1)
done = (FRAMES / f'{FPS * DUR - 1:04d}.png').exists()  # frames already rendered: only assemble
for fi in (range(FPS * DUR) if not done else []):
    t = fi / FPS
    on = BEAM_ON <= t < BEAM_OFF
    # the flashlight: sways with the walk, stutters when he is close
    sway = 0.09 * math.sin(t * 0.9) + 0.03 * math.sin(t * 2.7)
    lift = 18 * math.sin(t * 1.8)
    ox, oy = W / 2 + 40 * math.sin(t * 0.9), H + 170 + lift
    ang = np.arctan2(X - ox, oy - Y) - sway
    dist = np.hypot(X - ox, oy - Y)
    cone = np.exp(-(np.abs(ang) / 0.27) ** 2.6) * np.exp(-dist / 700) * dust
    power = 1.0 if on else 0.0
    if on and 17.5 < t < BEAM_OFF: power *= 0.35 if (math.sin(t * 31) * math.sin(t * 7.3) > 0.45) else 1.0  # the stutter
    if on and t < BEAM_ON + 0.08: power *= 0.5
    arr = base * (0.42 + 1.7 * cone * power)[:, :, None] + (cone * 28 * power)[:, :, None] * np.array([1.0, 0.9, 0.7])[None, None, :]
    canvas = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).convert('RGBA')
    # him: far on the road from 11.5 s, close and spread from 17 s, gone when the light dies
    if 11.5 <= t < BEAM_OFF:
        if t < 17:
            k = (t - 11.5) / 5.5; S = 0.16 + 0.04 * k; mx, my = 640 - 20 * k, VP[1] + 95 + 30 * k; spread = 0.1; eyes = min(1, (t - 11.5) / 1.5)
        else:
            k = min(1, (t - 17) / 1.2); S = 0.2 + 0.32 * k; mx, my = 620, 420 + 50 * k; spread = min(1, (t - 17) / 2.0); eyes = 1.0
        fig, glow = figure(mx, my, S, spread, eyes * (0.75 + 0.25 * math.sin(t * 5)))
        canvas = Image.alpha_composite(canvas, fig.filter(ImageFilter.GaussianBlur(1.0)))
        canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(10 * S + 4)))
        canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(1.2)))
    # moths in the beam
    if on:
        show = min(1, (t - BEAM_ON - 0.6) / 2.5)
        if show > 0:
            for (th0, om, rad, dep, ph) in MOTHS:
                th = th0 + om * t
                px = W / 2 + 70 * math.sin(t * 0.9) + rad * (0.4 + 0.6 * dep) * math.cos(th) + math.sin(sway) * 300 * dep
                py = 560 - 160 * dep + rad * 0.45 * math.sin(th) + lift * dep
                sz = int(10 + 30 * dep)
                flap = max(0.15, abs(math.cos(t * 13 + ph)))
                m = moth.resize((max(2, int(sz * flap)), sz)).rotate(math.degrees(th) + 90, expand=True, resample=Image.Resampling.BICUBIC)
                a = m.split()[3].point(lambda v: int(v * 0.65 * show * (0.4 + 0.6 * dep)))
                tint = Image.new('RGBA', m.size, (215, 205, 180, 0)); tint.putalpha(a)
                canvas.alpha_composite(tint, (int(px - m.size[0] / 2), int(py - m.size[1] / 2)))
    # captions and the title
    canvas = caption(canvas, 'Point Pleasant, West Virginia.  November 1966.', fade(t, 1.5, 2.5, 4.3, 5.0))
    canvas = caption(canvas, 'Your dog went under the wire at dusk.', fade(t, 7.0, 7.8, 10.2, 11.0))
    canvas = caption(canvas, 'You have one flashlight.', fade(t, 12.5, 13.3, 15.8, 16.6))
    canvas = caption(canvas, 'Something answers it.', fade(t, 18.0, 18.8, 21.6, 22.4))
    canvas = caption(canvas, 'MOTHMAN', fade(t, 23.8, 25.0, 28.6, 30.0), y=330, font=title_font)
    canvas = caption(canvas, 'A horror scene in Decentraland', fade(t, 24.8, 25.8, 28.6, 30.0), y=425, font=small_font, color=(170, 165, 150))
    # grain, vignette, the fades
    arr = np.asarray(canvas).astype(float)[:, :, :3]
    arr = arr * vig[:, :, None] + (r.random((H, W)) - 0.5)[:, :, None] * 9
    arr *= min(1, t / 1.2) * min(1, max(0, (DUR - t) / 1.0))
    Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).save(FRAMES / f'{fi:04d}.png', compress_level=1)
    if fi % 120 == 0: print(f'frame {fi}/{FPS * DUR}', flush=True)

# ---- audio: the scene's own sounds, placed on the timeline, over the forest and the drone ---------------------------
A = Path('assets/audio')
cues = [('forest.ogg', 0, 0.9, True), ('wind.ogg', 0, 0.5, True), ('howl.ogg', 7.2, 0.9, False), ('click.ogg', 5.0, 1.0, False), ('flutter.ogg', 6.0, 0.45, True),
        ('drone.ogg', 11.5, 0.7, True), ('call.ogg', 12.0, 1.0, False), ('wingbeat.ogg', 17.0, 1.0, False), ('whine.ogg', 17.6, 0.5, True),
        ('screech.ogg', 20.6, 1.0, False), ('lunge.ogg', 22.7, 1.0, False), ('switch.ogg', 23.2, 0.9, False)]
inputs, filters, mixed = [], [], []
for i, (f, at, vol, loop) in enumerate(cues):
    inputs += (['-stream_loop', '-1'] if loop else []) + ['-i', str(A / f)]
    end = BEAM_OFF if f in ('flutter.ogg', 'whine.ogg') else DUR
    filters.append(f'[{i + 1}:a]atrim=0:{end - at:.2f},adelay={int(at * 1000)}|{int(at * 1000)},volume={vol}[a{i}]')
    mixed.append(f'[a{i}]')
filters.append(f'{"".join(mixed)}amix=inputs={len(mixed)}:normalize=0,afade=t=out:st={DUR - 1.5}:d=1.5[mix]')
cmd = ['ffmpeg', '-y', '-framerate', str(FPS), '-i', str(FRAMES / '%04d.png')] + inputs + ['-filter_complex', ';'.join(filters), '-map', '0:v', '-map', '[mix]',
       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '160k', '-t', str(DUR), str(OUT)]
subprocess.run(cmd, check=True, capture_output=True)
print('trailer written', OUT, OUT.stat().st_size // 1024, 'KiB')

# Hero renders of a Decentraland scene's own GLBs for its marketing kit (headless Blender, Cycles).
# Copy to <scene>/promote/tools/render_shots.py, then rewrite the SHOTS section for this scene.
# Needs Blender 4.2 or newer (tested on 5.1): clip mode uses the EEVEE that shipped in 4.2.
#
#   B=/Applications/Blender.app/Contents/MacOS/Blender              # macOS
#   B="C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"   # Windows (PowerShell: & $B ...)
#   B=blender                                                       # Linux, when it is on PATH
#   $B -b -P promote/tools/render_shots.py -- preview [shot ...]   # 480 px, 12 samples -> promote/images/preview/
#   $B -b -P promote/tools/render_shots.py -- final   [shot ...]   # 1600 px, 128 samples -> promote/images/renders/
#   $B -b -P promote/tools/render_shots.py -- keyart preview       # same at 1/4 size, 12 samples -> promote/images/preview/
#   $B -b -P promote/tools/render_shots.py -- keyart               # KEYART_SHOT at KEYART_SIZES -> promote/images/keyart/
#   $B -b -P promote/tools/render_shots.py -- clip preview shot    # 640x360 EEVEE camera move -> promote/images/preview/<shot>_clip.mp4
#   $B -b -P promote/tools/render_shots.py -- clip shot [shot ...] # 1920x1080 EEVEE, CLIP_SECONDS long -> promote/clips/<shot>.mp4
#
# Always run the preview modes first and look at every PNG before the final pass.
# Clips are only made on request, for a post video (see the skill's references/video-posts.md): the same
# shot, 16:9, with a slow camera move (CLIP_MOVE / CLIP_MOVES) rendered in EEVEE at CLIP_FPS. Nothing in
# the scene animates: no avatars, no runtime effects. A 6 s 1080p clip took about 2 minutes on Apple Silicon.
# Finals take 1-3 min each (whole-interior scenes are at the slow end): render them one or two shots
# per command, or in the background, so a shell timeout does not kill the batch half-way.
import bpy, math, sys, os, time
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # scene root
P = os.path.join(ROOT, 'promote')

# ------------------------------------------------------------------ per-scene settings (edit)
MODELS = os.path.join(ROOT, 'assets', 'Models')   # relative GLB paths in load() resolve here
KEYART_SHOT = 'hero'                              # the road, him on it, headroom for the wordmark
KEYART_SIZES = [(1920, 1080), (1080, 1080)]       # expanded kit: add (1080, 1350), (1080, 1920)
MONO = os.path.join(ROOT, 'assets', 'fonts', 'SpecialElite-Regular.ttf')  # the scene's own typewriter face, for the gate sign
CLIP_SECONDS = 6                                  # length of every -- clip
CLIP_FPS = 30                                     # matches the Remotion project in promote/video/
CLIP_SAMPLES = 16                                 # EEVEE TAA samples per frame; 48 looked no better and cost 3x
CLIP_MOVE = dict(dolly=-0.10, orbit=4.0, rise=0.0)   # default move: push in 10 % of dist, orbit 4 deg, no rise
CLIP_MOVES = {'hero': dict(dolly=-0.12, orbit=2.0, rise=0.0), 'dog': dict(dolly=-0.15, orbit=6.0, rise=-2.0)}

MONO_FALLBACKS = ['/System/Library/Fonts/Supplemental/Courier New Bold.ttf', r'C:\Windows\Fonts\courbd.ttf',
                  '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf']
MONO = MONO or next((f for f in MONO_FALLBACKS if os.path.exists(f)), None)

# ------------------------------------------------------------------ mode
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
MODE = argv[0] if argv else 'preview'
if MODE not in ('preview', 'final', 'keyart', 'clip'):
    sys.exit('unknown mode %r: use -- preview [shot ...], -- final [shot ...], -- keyart [preview], -- clip [preview] <shot ...>' % MODE)
DRAFT = MODE == 'preview' or (MODE in ('keyart', 'clip') and 'preview' in argv[1:])
ONLY = [KEYART_SHOT] if MODE == 'keyart' else [a for a in argv[1:] if a != 'preview']
if MODE == 'clip' and not ONLY:   # every clip costs minutes; an unnamed batch outruns shell timeouts
    sys.exit('clip mode needs shot names: -- clip hero security (each 1080p clip takes 2-3 minutes)')
OUT = os.path.join(P, 'images', 'preview') + '/' if DRAFT else (
    os.path.join(P, 'clips') + '/' if MODE == 'clip' else os.path.join(P, 'images', {'final': 'renders', 'keyart': 'keyart'}[MODE]) + '/')
os.makedirs(OUT, exist_ok=True)
RES = (360 if DRAFT else 1080) if MODE == 'clip' else (480 if DRAFT else 1600)
SAMPLES = 12 if DRAFT else (96 if MODE == 'keyart' else 64)   # night scenes denoise well; 64 keeps a final under a few minutes
CAM = {}   # the last camera() call, so clip mode can animate it


# ------------------------------------------------------------------ helpers
def reset(aspect=1.0, exposure=-0.7):
    """Empty Cycles scene, AgX High Contrast, near-black world. aspect = width / height.
    In clip mode the engine is EEVEE and the frame is always 16:9 (the aspect argument is ignored)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    if MODE == 'clip':
        aspect = 16 / 9
        try:
            scn.render.engine = 'BLENDER_EEVEE'        # Blender 5.x
        except TypeError:
            scn.render.engine = 'BLENDER_EEVEE_NEXT'   # Blender 4.2-4.5 (older Blenders are not supported)
        scn.eevee.taa_render_samples = 8 if DRAFT else CLIP_SAMPLES
        scn.eevee.use_raytracing = True
        scn.eevee.use_shadows = True
        scn.eevee.shadow_pool_size = '1024'   # a whole interior with many point lights overflows the 512 MB default
        scn.render.fps = CLIP_FPS
        scn.frame_start, scn.frame_end = 1, int(CLIP_SECONDS * CLIP_FPS)
    else:
        scn.render.engine = 'CYCLES'
        scn.cycles.samples = SAMPLES
        scn.cycles.use_denoising = True
        # GPU: the first Cycles backend that lists a device of its own kind (Apple METAL, NVIDIA OPTIX/CUDA,
        # AMD HIP, Intel ONEAPI); else CPU. Each backend is asked for its own list: prefs.devices holds every
        # backend's devices at once, so checking it would pick OPTIX on an AMD or Intel machine and render on the CPU.
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for backend in ('METAL', 'OPTIX', 'CUDA', 'HIP', 'ONEAPI'):
            try:
                devs = list(prefs.get_devices_for_type(backend))
            except Exception:   # backend not compiled into this Blender
                continue
            gpus = [d for d in devs if d.type == backend]
            if not gpus:
                continue
            prefs.compute_device_type = backend
            for d in devs:
                d.use = d.type == backend
            scn.cycles.device = 'GPU'
            print('Cycles on GPU (%s: %s)' % (backend, ', '.join(d.name for d in gpus)))
            break
        else:
            print('no GPU backend found, rendering on CPU (slower)')
    scn.render.resolution_x = int(round(RES * aspect))
    scn.render.resolution_y = RES
    scn.view_settings.view_transform = 'AgX'
    scn.view_settings.look = 'AgX - High Contrast'
    scn.view_settings.exposure = exposure
    scn.render.image_settings.file_format = 'PNG'
    world = bpy.data.worlds.new('w'); scn.world = world; world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.004, 0.004, 0.008, 1)
    return scn


def haze(density=0.04, color=(0.8, 0.78, 0.7)):
    """World volume scatter: visible light shafts. 0.02 subtle, 0.06-0.07 thick."""
    wn = bpy.context.scene.world.node_tree
    vol = wn.nodes.new('ShaderNodeVolumePrincipled')
    vol.inputs['Density'].default_value = density
    vol.inputs['Anisotropy'].default_value = 0.4
    vol.inputs['Color'].default_value = (*color, 1)
    wn.links.new(vol.outputs['Volume'], wn.nodes['World Output'].inputs['Volume'])


def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
    if not pts:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def load(path, at=(0, 0, 0), rot=0, scale=1.0, align_long_x=False, anchor='bottom'):
    """Import a GLB under an empty, normalised by its world bounding box so its footprint centre sits
    at `at` (Blender coords: X right, Y away from camera at az=0, Z up). anchor='bottom' puts the
    lowest point on at[2]; 'center' centres it vertically. align_long_x turns long pieces (walls,
    benches, counters) so their long axis runs along X before `rot` (degrees, about Z) is applied."""
    if not os.path.isabs(path):
        path = os.path.join(MODELS, path)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    # The engine strips *_collider meshes to physics; Blender renders them as white boxes. Drop them.
    for o in [o for o in new if '_collider' in o.name.lower()]:
        bpy.data.objects.remove(o, do_unlink=True)
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(os.path.basename(path) + '_root', None)
    bpy.context.scene.collection.objects.link(root)
    for o in new:
        if o.parent is None or o.parent not in new:
            o.parent = root
    bpy.context.view_layer.update()
    lo, hi = bbox(new)
    if align_long_x and (hi.y - lo.y) > (hi.x - lo.x):
        rot += 90
    root.rotation_euler = (0, 0, math.radians(rot))
    root.scale = (scale, scale, scale)
    bpy.context.view_layer.update()
    lo, hi = bbox(new)
    c = (lo + hi) / 2
    dz = lo.z if anchor == 'bottom' else c.z
    root.location = (at[0] - c.x, at[1] - c.y, at[2] - dz)
    bpy.context.view_layer.update()
    return new


def room(floor, wall=None, ceiling=None, tile=8.0, back_y=5.0, centre_wall=None, ceiling_z=6.0):
    """A 3x3 patch of the scene's floor tiles centred on the origin (tiles at -tile/0/+tile, so no seam
    runs through the middle of the shot), a back wall at y=back_y made of three pieces, and an optional
    ceiling row. Put a doorway piece in `centre_wall`; never stack it in front of a plain wall."""
    objs = []
    for x in (-tile, 0, tile):
        for y in (-tile, 0, tile):
            objs += load(floor, (x, y, 0))
    if wall:
        for x in (-tile, tile):
            objs += load(wall, (x, back_y, 0), align_long_x=True)
        objs += load(centre_wall or wall, (0, back_y, 0), align_long_x=True)
    if ceiling:
        for x in (-tile, 0, tile):
            objs += load(ceiling, (x, 0, ceiling_z))
    return objs


def light_area(loc, energy=400, color=(1.0, 0.93, 0.78), size=(4.0, 0.6), rot=(0, 0, 0)):
    """Rectangular area light. Overhead fluorescent: loc z just under the ceiling, rot (0,0,0).
    Backlight through a doorway: behind the opening, rot=(radians(90),0,0), big size, high energy."""
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    a = bpy.context.active_object.data
    a.shape = 'RECTANGLE'; a.size = size[0]; a.size_y = size[1]; a.energy = energy; a.color = color
    return bpy.context.active_object


def light_point(loc, energy=600, color=(1, 0.1, 0.06), radius=0.8):
    bpy.ops.object.light_add(type='POINT', location=loc)
    l = bpy.context.active_object.data
    l.energy = energy; l.color = color; l.shadow_soft_size = radius
    return bpy.context.active_object


def _pose(target, az, el, dist):
    az_r, el_r = math.radians(az), math.radians(el)
    d = Vector((math.cos(el_r) * math.sin(az_r), -math.cos(el_r) * math.cos(az_r), math.sin(el_r)))
    pos = Vector(target) + d * dist
    return pos, (Vector(target) - pos).to_track_quat('-Z', 'Y').to_euler()


def camera(target, az=0, el=12, dist=6.0, lens=40, fstop=4.0, focus=None):
    """Camera looking at `target`. az=0 looks along +Y from the -Y side; positive az orbits
    counter-clockwise seen from above. el in degrees above the target. DOF focused on the target.
    Clip mode animates this camera along CLIP_MOVE from the pose given here."""
    pos, rot = _pose(target, az, el, dist)
    bpy.ops.object.camera_add(location=pos)
    cam = bpy.context.active_object
    cam.rotation_euler = rot
    cam.data.lens = lens
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = focus or dist
    cam.data.dof.aperture_fstop = fstop
    bpy.context.scene.camera = cam
    CAM.update(obj=cam, target=Vector(target), az=az, el=el, dist=dist, focus=focus)
    return cam


def text(body, at, size=0.5, color=(1, 0.6, 0.1), emit=6.0, font=MONO, rot=(90, 0, 0), align='CENTER'):
    """Emissive 3D text, e.g. to fill a sign or departures board the scene fills at runtime."""
    bpy.ops.object.text_add(location=at, rotation=tuple(math.radians(r) for r in rot))
    t = bpy.context.active_object
    t.data.body = body; t.data.size = size
    if font:   # None: Blender's built-in font
        t.data.font = bpy.data.fonts.load(font)
    t.data.align_x = align; t.data.align_y = 'CENTER'
    m = bpy.data.materials.new('txt'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Emission Color'].default_value = (*color, 1)
    b.inputs['Emission Strength'].default_value = emit
    t.data.materials.append(m)
    return t


def render_clip(name):
    """Keyframe the shot's camera from its pose to pose + CLIP_MOVE and render CLIP_SECONDS of H.264."""
    scn = bpy.context.scene
    cam, mv = CAM['obj'], {**CLIP_MOVE, **CLIP_MOVES.get(name, {})}
    n = scn.frame_end
    for frame, k in ((1, 0.0), (n, 1.0)):
        dist = CAM['dist'] * (1 + mv['dolly'] * k)
        pos, rot = _pose(CAM['target'], CAM['az'] + mv['orbit'] * k, CAM['el'] + mv['rise'] * k, dist)
        cam.location, cam.rotation_euler = pos, rot
        cam.data.dof.focus_distance = (CAM['focus'] or CAM['dist']) * dist / CAM['dist']
        cam.keyframe_insert('location', frame=frame)
        cam.keyframe_insert('rotation_euler', frame=frame)
        cam.data.dof.keyframe_insert('focus_distance', frame=frame)
    scn.frame_set(1)
    if hasattr(scn.render.image_settings, 'media_type'):   # Blender 5+
        scn.render.image_settings.media_type = 'VIDEO'
    scn.render.image_settings.file_format = 'FFMPEG'
    scn.render.ffmpeg.format = 'MPEG4'
    scn.render.ffmpeg.codec = 'H264'
    scn.render.ffmpeg.constant_rate_factor = 'HIGH'
    scn.render.ffmpeg.gopsize = CLIP_FPS
    scn.render.use_file_extension = True
    suffix = '_clip' if DRAFT else ''
    scn.render.filepath = OUT + name + suffix + '.mp4'
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    # Blender may append the frame range to a movie file name; normalise to <name>.mp4.
    made = [f for f in os.listdir(OUT) if f.startswith(name + suffix) and f.endswith('.mp4')]
    for f in made:
        if f != name + suffix + '.mp4':
            os.replace(OUT + f, OUT + name + suffix + '.mp4')
    print('RENDERED %s (%.0f s, %d frames at %dx%d)' % (OUT + name + suffix + '.mp4', time.time() - t0, n,
                                                       scn.render.resolution_x, scn.render.resolution_y))


def render(name):
    scn = bpy.context.scene
    if MODE == 'clip':
        return render_clip(name)
    if MODE == 'keyart':
        for w, h in KEYART_SIZES:
            scn.render.resolution_x, scn.render.resolution_y = (w // 4, h // 4) if DRAFT else (w, h)
            scn.render.filepath = OUT + '%s_%dx%d.png' % (name, w, h)
            t0 = time.time()
            bpy.ops.render.render(write_still=True)
            print('RENDERED %s (%.0f s)' % (scn.render.filepath, time.time() - t0))
        return
    scn.render.filepath = OUT + name + '.png'
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print('RENDERED %s (%.0f s)' % (scn.render.filepath, time.time() - t0))


# ------------------------------------------------------------------ SHOTS (Mothman)
# The scene is a Creator Hub composite (assets/scene/main.composite): hundreds of placed GLBs (trees, bunkers, the dog)
# and primitive boxes/planes with materials (the cabin, the fence, paw prints, the stencils). Every shot rebuilds a
# region of the real layout from that file, so the renders are the game's own places, then adds the flashlight (a spot
# at the camera), the cabin bulb and him (assets/Models/mothman.glb, the un-rigged model) where the moment needs him.
# Axes: DCL (x, y up, z) -> Blender (-x, -z, y). The glTF importer already does glTF -> Blender, so an imported GLB
# only needs the DCL world matrix conjugated by that map.
import json
from mathutils import Matrix, Quaternion as MQ

F = Matrix(((-1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
FI = F.inverted()
F3 = F.to_3x3()
COMPOSITE = json.load(open(os.path.join(ROOT, 'assets', 'scene', 'main.composite')))
C = {c['name']: c['data'] for c in COMPOSITE['components']}
NAMES = {eid: d['json']['value'] for eid, d in C['core-schema::Name'].items()}
MOTHMAN_MODEL_SCALE = 1.0
_src = open(os.path.join(ROOT, 'src', 'npc', 'mothman', 'animations.ts')).read()
import re as _re
_m = _re.search(r'MOTHMAN_MODEL_SCALE = ([\d.]+)', _src)
if _m: MOTHMAN_MODEL_SCALE = float(_m.group(1))
# the road polyline, from the generator (pure python: it only needs math)
_gen = open(os.path.join(ROOT, 'scripts', 'gen-forest.py')).read()
_env = {'math': math, 'W': 192, 'D': 192, 'layout': {}}
exec(_gen[_gen.index('spawn = (4.0'):_gen.index('ROAD_MAT =')], _env)
road_pt = _env['road_pt']
LAYOUT = json.loads(open(os.path.join(ROOT, 'src', 'layout.ts')).read().split('export const layout = ')[1])


def dcl_local(t):
    p, r, s = t['position'], t['rotation'], t['scale']
    return Matrix.Translation((p['x'], p['y'], p['z'])) @ MQ((r['w'], r['x'], r['y'], r['z'])).to_matrix().to_4x4() @ Matrix.Diagonal((s['x'], s['y'], s['z'], 1))


_world = {}
def dcl_world(eid):
    if eid in _world:
        return _world[eid]
    t = C['core::Transform'].get(eid)
    if t is None:
        m = Matrix.Identity(4)
    else:
        parent = t['json'].get('parent', 0)
        m = (dcl_world(str(parent)) if parent else Matrix.Identity(4)) @ dcl_local(t['json'])
    _world[eid] = m
    return m


def to_blender(world_dcl):
    return F @ world_dcl @ FI


def vec(p):
    """DCL point -> Blender Vector."""
    return F3 @ Vector(p)


_glb_cache = {}
def glb_template(src):
    """Import a GLB once; keep its mesh datablocks and their matrices for cheap linked instances."""
    if src in _glb_cache:
        return _glb_cache[src]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, src))
    new = [o for o in bpy.data.objects if o not in before]
    for o in [o for o in new if '_collider' in o.name.lower()]:
        bpy.data.objects.remove(o, do_unlink=True)
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    tmpl = [(o.data, o.matrix_world.copy(), o.name) for o in new if o.type == 'MESH']
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    _glb_cache[src] = tmpl
    return tmpl


def place_glb(src, world_dcl, name='glb'):
    E = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(E)
    E.matrix_world = to_blender(world_dcl)
    objs = []
    for mesh, mw, nm in glb_template(src):
        o = bpy.data.objects.new(nm, mesh)
        bpy.context.scene.collection.objects.link(o)
        o.parent = E
        o.matrix_local = mw
        objs.append(o)
    return E, objs


_mat_cache = {}
def material_for(mat_json):
    key = json.dumps(mat_json, sort_keys=True)
    if key in _mat_cache:
        return _mat_cache[key]
    pbr = mat_json.get('material', {}).get('pbr', {}) if mat_json else {}
    m = bpy.data.materials.new('dcl'); m.use_nodes = True
    nt = m.node_tree; P = nt.nodes['Principled BSDF']
    col = pbr.get('albedoColor', {'r': 1, 'g': 1, 'b': 1, 'a': 1})
    P.inputs['Base Color'].default_value = (col['r'], col['g'], col['b'], 1)
    P.inputs['Roughness'].default_value = pbr.get('roughness', 0.9)
    P.inputs['Metallic'].default_value = pbr.get('metallic', 0)
    src = pbr.get('texture', {}).get('tex', {}).get('texture', {}).get('src')
    cutout = pbr.get('transparencyMode', 0) in (1, 2) or 'alphaTexture' in pbr or col.get('a', 1) < 1
    if src and os.path.exists(os.path.join(ROOT, src)):
        img = nt.nodes.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(os.path.join(ROOT, src), check_existing=True)
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 1
        nt.links.new(img.outputs['Color'], mix.inputs[6]); mix.inputs[7].default_value = (col['r'], col['g'], col['b'], 1)
        nt.links.new(mix.outputs[2], P.inputs['Base Color'])
        if cutout:
            nt.links.new(img.outputs['Alpha'], P.inputs['Alpha'])
            m.blend_method = 'CLIP' if pbr.get('transparencyMode', 1) != 2 else 'BLEND'
            if hasattr(m, 'surface_render_method'): m.surface_render_method = 'DITHERED'
    elif col.get('a', 1) < 1:
        P.inputs['Alpha'].default_value = col['a']; m.blend_method = 'BLEND'
        if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED'
    em = pbr.get('emissiveColor')
    if em and pbr.get('emissiveIntensity', 0) > 0:
        P.inputs['Emission Color'].default_value = (em['r'], em['g'], em['b'], 1)
        P.inputs['Emission Strength'].default_value = pbr['emissiveIntensity']
    _mat_cache[key] = m
    return m


def prim_mesh(mr):
    """Unit DCL primitive as a Blender mesh in DCL-local coordinates mapped through F."""
    kind = mr['mesh']['$case']; verts = []; faces = []; uv = []
    if kind == 'box':
        s = 0.5
        for (a, b, c, d) in [((-s,-s,-s),(s,-s,-s),(s,s,-s),(-s,s,-s)), ((-s,-s,s),(-s,s,s),(s,s,s),(s,-s,s)), ((-s,-s,-s),(-s,-s,s),(s,-s,s),(s,-s,-s)),
                             ((-s,s,-s),(s,s,-s),(s,s,s),(-s,s,s)), ((-s,-s,-s),(-s,s,-s),(-s,s,s),(-s,-s,s)), ((s,-s,-s),(s,-s,s),(s,s,s),(s,s,-s))]:
            i = len(verts); verts += [a, b, c, d]; faces.append((i, i+1, i+2, i+3)); uv += [(0,0),(1,0),(1,1),(0,1)]
    elif kind == 'plane':
        verts = [(-0.5,-0.5,0),(0.5,-0.5,0),(0.5,0.5,0),(-0.5,0.5,0)]; faces = [(0,1,2,3)]
        u = mr['mesh']['plane'].get('uvs') or []
        uv = [(u[0],u[1]),(u[2],u[3]),(u[4],u[5]),(u[6],u[7])] if len(u) >= 8 else [(0,0),(1,0),(1,1),(0,1)]
    elif kind == 'sphere':
        n, m_ = 16, 12
        for j in range(m_ + 1):
            ph = math.pi * j / m_
            for k in range(n):
                th = 2 * math.pi * k / n; verts.append((0.5*math.sin(ph)*math.cos(th), 0.5*math.cos(ph), 0.5*math.sin(ph)*math.sin(th)))
        for j in range(m_):
            for k in range(n):
                a, b = j*n + k, j*n + (k+1) % n; faces.append((a, b, b+n, a+n))
        kind = 'cylinder'  # no uv layer
    else:  # cylinder
        cy = mr['mesh'].get('cylinder', {}); rt, rb = cy.get('radiusTop', 0.5), cy.get('radiusBottom', 0.5); n = 24
        for k in range(n):
            a = k / n * 2 * math.pi
            verts += [(rb*math.cos(a), -0.5, rb*math.sin(a)), (rt*math.cos(a), 0.5, rt*math.sin(a))]
        for k in range(n):
            i, j = 2*k, 2*((k+1) % n); faces.append((i, j, j+1, i+1)); uv += [(0,0),(1,0),(1,1),(0,1)]
        faces.append(tuple(2*k for k in range(n))[::-1]); faces.append(tuple(2*k+1 for k in range(n)))
        uv += [(0,0)] * (2*n)
    me = bpy.data.meshes.new('prim')
    me.from_pydata([tuple(F3 @ Vector(v)) for v in verts], [], faces)
    if kind != 'cylinder':
        layer = me.uv_layers.new(); k = 0
        for poly in me.polygons:
            for li in poly.loop_indices:
                layer.data[li].uv = uv[k]; k += 1
    return me


def scene_region(center, radius, skip=(), only=None, avoid=None):
    """Instantiate every rendered entity of the composite within `radius` m of (x, z); the ground always.
    avoid=((x, z), r): leave out trees within r m of that point (the camera), so none stands in the lens."""
    cx, cz = center; count = 0
    for eid in C['core::Transform']:
        nm = NAMES.get(eid, '')
        if any(nm.startswith(s) for s in skip): continue
        if only is not None and not any(nm.startswith(s) for s in only): continue
        g = C['core::GltfContainer'].get(eid); mr = C['core::MeshRenderer'].get(eid)
        if g is None and mr is None: continue
        W = dcl_world(eid); p = W.to_translation()
        ground = nm == 'Forest: ground' or (g is not None and ('forest-ground' in g['json']['src'] or 'forest-tracks' in g['json']['src']))
        if not ground and math.hypot(p.x - cx, p.z - cz) > radius: continue
        if avoid is not None and nm.startswith('Forest: tree') and math.hypot(p.x - avoid[0][0], p.z - avoid[0][1]) < avoid[1]: continue
        if g is not None:
            src = g['json']['src']
            if not os.path.exists(os.path.join(ROOT, src)): continue
            place_glb(src, W, nm or 'glb')
        else:
            me = prim_mesh(mr['json'])
            mat = C['core::Material'].get(eid)
            me.materials.append(material_for(mat['json'] if mat else None))
            o = bpy.data.objects.new(nm or 'prim', me); bpy.context.scene.collection.objects.link(o); o.matrix_world = to_blender(W)
        count += 1
    print('region', center, radius, '->', count, 'entities')


def night(moon=0.12):
    """A trace of blue moonlight so the trees read against the sky, as the scene's ambient does.
    Called first in every shot, right after reset(): it also drops the caches, whose datablocks reset() removed."""
    _mat_cache.clear(); _glb_cache.clear(); _world.clear()
    bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.006, 0.008, 0.016, 1)
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
    sun = bpy.context.active_object; sun.data.energy = moon; sun.data.color = (0.55, 0.65, 1.0); sun.data.angle = math.radians(8)
    sun.rotation_euler = (math.radians(55), 0, math.radians(30))


def flashlight(pos, target, energy=1200, angle=56, color=(1.0, 0.93, 0.78)):
    """The player's beam: a spot at `pos` (DCL) aimed at `target` (DCL)."""
    p, t = vec(pos), vec(target)
    bpy.ops.object.light_add(type='SPOT', location=p)
    l = bpy.context.active_object; d = l.data
    d.energy = energy; d.spot_size = math.radians(angle); d.spot_blend = 0.4; d.color = color; d.shadow_soft_size = 0.08
    l.rotation_euler = (t - p).to_track_quat('-Z', 'Y').to_euler()
    return l


def camera_dcl(pos, target, lens=32, fstop=2.8):
    """camera() from a DCL position looking at a DCL target (clip mode keeps working: the pose is recorded)."""
    p, t = vec(pos), vec(target)
    d = p - t; dist = d.length; el = math.degrees(math.asin(d.z / dist)); az = math.degrees(math.atan2(d.x, -d.y))
    return camera(tuple(t), az=az, el=el, dist=dist, lens=lens, fstop=fstop)


def mothman(at, face, ground=True, eyes=25):
    """Him at DCL point `at` (feet), turned toward DCL point `face`, eyes lit."""
    yaw = math.atan2(face[0] - at[0], face[2] - at[2])
    W = Matrix.Translation(at) @ MQ((math.cos(yaw / 2), 0, math.sin(yaw / 2), 0)).to_matrix().to_4x4() @ Matrix.Diagonal((MOTHMAN_MODEL_SCALE,) * 3 + (1,))
    E, objs = place_glb('assets/Models/mothman.glb', W, 'mothman')
    print('mothman materials:', sorted({s.material.name for o in objs for s in o.material_slots if s.material}))
    for o in objs:
        for slot in o.material_slots:
            m = slot.material
            if m and 'eye' in m.name.lower() and m.use_nodes:
                P = m.node_tree.nodes.get('Principled BSDF')
                if P:
                    P.inputs['Emission Color'].default_value = (1, 0.05, 0.02, 1); P.inputs['Emission Strength'].default_value = eyes
    Wn = Matrix.Translation(at) @ MQ((math.cos(yaw / 2), 0, math.sin(yaw / 2), 0)).to_matrix().to_4x4()  # unscaled: the eyes sit 2.05 m up, as in src/npc/mothman/body.ts
    for side in (-0.14, 0.14):
        ep = (Wn @ Matrix.Translation((side, 2.05, 0.35))).to_translation()
        light_point(tuple(vec(ep)), energy=eyes * 1.6, color=(1, 0.12, 0.05), radius=0.035)
    return E


def gate_sign():
    """The sign as src/index.ts builds it at runtime: a post, a board and the gate text on an empty anchor."""
    eid = next(e for e, n in NAMES.items() if n == 'Forest: sign')
    W = dcl_world(eid); W = Matrix.Translation(W.to_translation()) @ W.to_quaternion().to_matrix().to_4x4()
    wood = material_for({'material': {'pbr': {'albedoColor': {'r': 0.3, 'g': 0.22, 'b': 0.14, 'a': 1}, 'roughness': 0.95, 'metallic': 0}}})
    paint = material_for({'material': {'pbr': {'albedoColor': {'r': 0.8, 'g': 0.76, 'b': 0.66, 'a': 1}, 'roughness': 0.95, 'metallic': 0}}})
    for pos, scale, mat in (((0, 1.95, -0.09), (0.16, 3.9, 0.16), wood), ((0, 2.9, 0), (1.4, 2.0, 0.08), paint)):
        me = prim_mesh({'mesh': {'$case': 'box', 'box': {}}}); me.materials.append(mat)
        o = bpy.data.objects.new('sign', me); bpy.context.scene.collection.objects.link(o)
        o.matrix_world = to_blender(W @ Matrix.Translation(pos) @ Matrix.Diagonal(scale + (1,)))
    sign = 'W.VA. ORDNANCE WORKS\nFORMER EXPLOSIVES PLANT\n1942 - 1945\nSTORAGE BUNKERS AHEAD\n\nNO TRESPASSING\nNO ENTRY AT NIGHT'
    t = text(sign, (0, 0, 0), size=0.13, color=(0.06, 0.05, 0.04), emit=0.0)
    # the DCL -> Blender map is a reflection, so the glyphs come out mirrored: flip the text's own X back
    t.matrix_world = to_blender(W @ Matrix.Translation((0, 2.9, 0.045)) @ MQ((0, 0, 1, 0)).to_matrix().to_4x4()) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Scale(-1, 4, (1, 0, 0))
    t.data.align_y = 'CENTER'


def shot_hero():
    """Key art: the plant road at night, him standing on it in the beam, eyes lit, moths' world around. Headroom above
    him for the wordmark (the target is raised, the elevation low)."""
    reset(exposure=-0.45); haze(0.006, (0.75, 0.75, 0.8)); night()
    t0 = 0.36
    cam = road_pt(t0); him = road_pt(t0 + 0.027)
    scene_region((him[0], him[2]), 34, skip=('Forest: sign',))
    mothman((him[0], 0.05, him[2]), (cam[0], 0, cam[2]))
    eye = (cam[0], 1.65, cam[2])
    flashlight(eye, (him[0], 1.3, him[2]), energy=900)
    camera_dcl(eye, (him[0], 2.3, him[2]), lens=30, fstop=2.5)
    render('hero')


def shot_gate():
    """Where you start: the chained plant gate behind you, the sign, the newspaper on the ground, the fence."""
    reset(exposure=-0.45); haze(0.005); night()
    scene_region((8, 6), 26, skip=('Forest: sign',))
    gate_sign()
    eye = (4.4, 1.6, 2.9)  # just inside the gate, the sign's face and the road beyond
    flashlight(eye, (8.2, 2.0, 6.3), energy=800)
    camera_dcl(eye, (8.6, 2.1, 7.2), lens=28, fstop=3.2)
    render('gate')


def shot_cabin():
    """The gatehouse at night, the bulb burning inside, and him at the window with his back to you."""
    reset(exposure=-0.45); haze(0.006); night()
    c = LAYOUT['cabin']; w = c['windows'][0]
    scene_region((c['x'], c['z']), 26)
    light_point(tuple(vec((c['bulb']['x'], c['bulb']['y'] - 0.1, c['bulb']['z']))), energy=900, color=(1, 0.85, 0.6), radius=0.08)
    mothman((w['x'], 0.05, w['z'] - 0.1), (c['bulb']['x'], 0, c['bulb']['z']), eyes=4)
    eye = (w['x'] + 4.5, 1.6, w['z'] - 7.5)
    flashlight(eye, (w['x'], 1.4, w['z']), energy=400)
    camera_dcl(eye, (w['x'] - 0.3, 1.6, w['z'] + 0.5), lens=30, fstop=2.8)
    render('cabin')


def shot_dog():
    """The road: a dead dog in the beam, somebody's hound, and paw prints going on past it."""
    reset(exposure=-0.45); haze(0.006); night()
    eid = next(e for e, n in NAMES.items() if n == 'Forest: dead dog'); d = dcl_world(eid).to_translation()
    scene_region((d.x, d.z), 24)
    eye = (d.x + 3.2, 1.55, d.z - 3.6)
    flashlight(eye, (d.x, 0.2, d.z), energy=650, angle=50)
    camera_dcl(eye, (d.x, 0.35, d.z + 0.6), lens=32, fstop=2.5)
    render('dog')


def shot_collars():
    """Bunker 6: nine chewed collars in a ring on the floor around a drift of dead moths, in the beam."""
    reset(exposure=-0.45); haze(0.004); night(0.05)
    b = LAYOUT['bunkers']['collars']
    scene_region((b['x'], b['z']), 20)
    # the heap src/documents.ts draws at runtime: a cone of moth planes in the middle of the ring
    heap = material_for({'material': {'pbr': {'texture': {'tex': {'texture': {'src': 'assets/images/mothheap.png'}}}, 'transparencyMode': 1, 'albedoColor': {'r': 0.95, 'g': 0.92, 'b': 0.85, 'a': 1}, 'roughness': 1}}})
    core = material_for({'material': {'pbr': {'albedoColor': {'r': 0.2, 'g': 0.18, 'b': 0.14, 'a': 1}, 'roughness': 1}}})
    at = (b['x'], 0, b['z'] + 1.0)
    me = prim_mesh({'mesh': {'$case': 'cylinder', 'cylinder': {'radiusTop': 0.05, 'radiusBottom': 0.5}}}); me.materials.append(core)
    o = bpy.data.objects.new('heap core', me); bpy.context.scene.collection.objects.link(o)
    o.matrix_world = to_blender(Matrix.Translation((at[0], 0.2, at[2])) @ Matrix.Diagonal((1.0, 0.4, 1.0, 1)))
    seed = 7
    def rnd():
        nonlocal seed; seed = (seed * 9301 + 49297) % 233280; return seed / 233280
    for i in range(18):
        k = i / 17; size = 2.2 * (1 - 0.8 * k) * (0.9 + 0.2 * rnd()); room_ = max(0, 1.0 - size / 2 - 0.1); a = rnd() * 2 * math.pi
        me = prim_mesh({'mesh': {'$case': 'plane', 'plane': {}}}); me.materials.append(heap)
        o = bpy.data.objects.new('heap', me); bpy.context.scene.collection.objects.link(o)
        yaw = rnd() * 2 * math.pi
        o.matrix_world = to_blender(Matrix.Translation((at[0] + math.cos(a) * room_ * rnd(), 0.02 + 0.42 * k, at[2] + math.sin(a) * room_ * rnd()))
                                    @ MQ((math.cos(yaw/2), 0, math.sin(yaw/2), 0)).to_matrix().to_4x4() @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Diagonal((size, size, 1, 1)))
    eye = (b['x'] + 0.3, 1.45, b['z'] - 2.6)
    flashlight(eye, (at[0], 0.1, at[2]), energy=600, angle=64)
    camera_dcl(eye, (at[0], 0.1, at[2] - 0.4), lens=24, fstop=3.0)
    render('collars')


def shot_bunker():
    """Bunker 7, the last one on the road: the headwall, the steel door hanging open, the step in the beam."""
    reset(exposure=-0.2); haze(0.006); night()
    r = LAYOUT['bunkers']['roost']; door = r['door']
    eye = (r['x'] + 3.5, 1.6, r['z'] - 15.5)
    scene_region((r['x'], r['z'] - 4), 30, avoid=((eye[0], eye[2]), 7))
    flashlight(eye, (r['x'], 1.2, r['z'] - 4.8), energy=1600, angle=56)
    camera_dcl(eye, (r['x'], 1.7, r['z'] - 4.8), lens=30, fstop=3.2)
    render('bunker')


SHOTS = {
    'hero': shot_hero,
    'gate': shot_gate,
    'cabin': shot_cabin,
    'dog': shot_dog,
    'collars': shot_collars,
    'bunker': shot_bunker,
}

for name, fn in SHOTS.items():
    if ONLY and name not in ONLY:
        continue
    print('=== shot', name)
    fn()

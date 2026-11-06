#!/usr/bin/env python3
"""Generate the Mothman woods into assets/scene/main.composite (edit mode: registers inspector::Nodes) and write
src/layout.ts with the key spots for the code. Reads scene.json parcels for bounds. Re-runnable: removes entities it
generated before (names starting "Forest:", "Document:", "Cabin:", "Bunker:"). Run with the scene CLOSED in the Creator
Hub editor (its autosave overwrites this file), then: npm run build.
"""
import json, random, math, sys, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scene = json.load(open(os.path.join(root, 'scene.json')))
parcels = [tuple(map(int, p.split(','))) for p in scene['scene']['parcels']]
bx, bz = map(int, scene['scene']['base'].split(','))
xs = [p[0]-bx for p in parcels]; zs = [p[1]-bz for p in parcels]
W = (max(xs)-min(xs)+1)*16; D = (max(zs)-min(zs)+1)*16
cp = os.path.join(root, 'assets/scene/main.composite')
comp = json.load(open(cp))
comps = {c['name']: c for c in comp['components']}
NAME_SCHEMA = {"type":"object","properties":{"value":{"type":"string","serializationType":"utf8-string"}},"serializationType":"map"}
def component(name, schema=None):
    if name not in comps:
        c = {"name": name}
        if schema is not None: c["jsonSchema"] = schema
        c["data"] = {}
        comp['components'].append(c); comps[name] = c
    return comps[name]
nodes = component('inspector::Nodes')['data']['0']['json']['value']
names = component('core-schema::Name', NAME_SCHEMA)
PREFIXES = ('Forest:', 'Document:', 'Cabin:', 'Bunker:')
old = [eid for eid, v in names['data'].items() if v['json']['value'].startswith(PREFIXES)]
for c in comp['components']:
    for eid in old: c['data'].pop(eid, None)
oldset = set(int(e) for e in old)
for n in nodes:
    n['children'] = [c for c in n['children'] if c not in oldset]
nodes[:] = [n for n in nodes if n['entity'] not in oldset]
root_node = next(n for n in nodes if n['entity'] == 0)
used = [int(e) for c in comp['components'] for e in c['data'].keys()] + [n['entity'] for n in nodes]
next_id = max([511] + used) + 1

def qmul(a, b):
    return {"x": a["w"]*b["x"] + a["x"]*b["w"] + a["y"]*b["z"] - a["z"]*b["y"],
            "y": a["w"]*b["y"] - a["x"]*b["z"] + a["y"]*b["w"] + a["z"]*b["x"],
            "z": a["w"]*b["z"] + a["x"]*b["y"] - a["y"]*b["x"] + a["z"]*b["w"],
            "w": a["w"]*b["w"] - a["x"]*b["x"] - a["y"]*b["y"] - a["z"]*b["z"]}
def quat_y(deg):
    r = math.radians(deg)/2; return {"x":0,"y":math.sin(r),"z":0,"w":math.cos(r)}
def quat_x(deg):
    r = math.radians(deg)/2; return {"x":math.sin(r),"y":0,"z":0,"w":math.cos(r)}
def quat_z(deg):
    r = math.radians(deg)/2; return {"x":0,"y":0,"z":math.sin(r),"w":math.cos(r)}
def quat_yx(yaw, pitch): return qmul(quat_y(yaw), quat_x(pitch))
CL_POINTER, CL_PHYSICS = 1, 2
def add(name, pos, scale=(1,1,1), rot=None, mesh=None, collider=None, material=None, parent=0, mask=CL_PHYSICS):
    global next_id
    eid = str(next_id); next_id += 1
    component('core::Transform')['data'][eid] = {"json": {"position": {"x":pos[0],"y":pos[1],"z":pos[2]}, "scale": {"x":scale[0],"y":scale[1],"z":scale[2]}, "rotation": rot or {"x":0,"y":0,"z":0,"w":1}, "parent": parent}}
    names['data'][eid] = {"json": {"value": name}}
    if mesh: component('core::MeshRenderer')['data'][eid] = {"json": {"mesh": mesh}}
    if collider: component('core::MeshCollider')['data'][eid] = {"json": {"collisionMask": mask, "mesh": collider}}
    if material: component('core::Material')['data'][eid] = {"json": {"material": {"$case":"pbr","pbr": material}}}
    nodes.append({"entity": int(eid), "children": []})
    (root_node if parent == 0 else next(n for n in nodes if n['entity'] == parent))['children'].append(int(eid))
    return int(eid)
def add_glb(name, src, pos, scale=(1,1,1), rot=None, vis=0, invis=0, parent=0):
    eid = add(name, pos, scale, rot, parent=parent)
    component('core::GltfContainer')['data'][str(eid)] = {"json": {"src": src, "visibleMeshesCollisionMask": vis, "invisibleMeshesCollisionMask": invis}}
    return eid
def tex(src): return {"tex": {"$case": "texture", "texture": {"src": src, "wrapMode": 0, "filterMode": 1}}}
def pbr(r,g,b, rough=1.0, emissive=None, ei=0, metallic=0, texture=None, alpha=None, cutout=None, a=1.0):
    m = {"albedoColor": {"r":r,"g":g,"b":b,"a":a}, "metallic": metallic, "roughness": rough}
    if emissive: m["emissiveColor"] = {"r":emissive[0],"g":emissive[1],"b":emissive[2]}; m["emissiveIntensity"] = ei
    if texture: m["texture"] = tex(texture)
    if cutout: m["alphaTexture"] = tex(cutout); m["transparencyMode"] = 1; m["alphaTest"] = 0.5
    if alpha is not None: m["transparencyMode"] = 2
    return m
BOX = {"$case":"box","box":{"uvs":[]}}; BOXC = {"$case":"box","box":{}}
SPH = {"$case":"sphere","sphere":{}}
PLANE = {"$case":"plane","plane":{"uvs":[]}}; PLANEC = {"$case":"plane","plane":{}}
def CYL(top, bottom): return {"$case":"cylinder","cylinder":{"radiusTop":top,"radiusBottom":bottom}}
rng = random.Random(1966)
layout = {}

# ---- ground and the plant fence ---------------------------------------------------------------------------------------
add('Forest: ground', (W/2, -0.1, D/2), (W, 0.2, D), mesh=BOX, collider=BOXC, material=pbr(0.36,0.3,0.22))
FENCE_IN = 2.0; FH = 2.6
POST = pbr(0.3, 0.3, 0.3, rough=0.7, metallic=0.4)
MESH = pbr(0.75, 0.76, 0.74, rough=0.6, metallic=0.5, texture='assets/images/chainlink.png', cutout='assets/images/chainlink.png')
def fence_side(x0, z0, x1, z1, tag, skip=()):
    L = math.hypot(x1-x0, z1-z0); yaw = math.degrees(math.atan2(x1-x0, z1-z0)); n = int(L/4)
    for i in range(n+1):
        if i in skip and i - 1 in skip: continue
        t = i/n; add(f'Forest: fence post {tag}{i}', (x0+(x1-x0)*t, FH/2, z0+(z1-z0)*t), (0.1, FH, 0.1), mesh=BOX, material=POST)
    for i in range(n):
        if i in skip: continue
        t = (i+0.5)/n; add(f'Forest: fence mesh {tag}{i}', (x0+(x1-x0)*t, FH/2, z0+(z1-z0)*t), (4.0, FH, 1), rot=quat_y(yaw+90), mesh=PLANE, material=MESH)
    # one invisible collider per side, plus a taller one so nobody jumps it
    add(f'Forest: fence collider {tag}', ((x0+x1)/2, 2.5, (z0+z1)/2), (0.3, 5, L), rot=quat_y(yaw), collider=BOXC)
fence_side(FENCE_IN, FENCE_IN, W-FENCE_IN, FENCE_IN, 'S', skip=(1,)); fence_side(W-FENCE_IN, FENCE_IN, W-FENCE_IN, D-FENCE_IN, 'E')
# the plant gate: a chained double gate in the south fence (panel S1, x 6..10), where the road leaves. You came in under
# the wire like the dog did; the gate itself does not open (owner pass 6: the narrative needs a gate you cannot cross)
GFRAME = pbr(0.28, 0.28, 0.3, rough=0.6, metallic=0.6)
for gx in (6.0, 10.0): add(f'Forest: gate post {gx:.0f}', (gx, FH/2 + 0.15, FENCE_IN), (0.18, FH + 0.3, 0.18), mesh=BOX, material=GFRAME)
for k, cx_ in enumerate((7.0, 9.0)):  # two 1.9 m leaves, hung closed, a hand's gap between them
    for n_, pos, sc in (('top', (cx_, FH - 0.15, FENCE_IN), (1.9, 0.08, 0.08)), ('bottom', (cx_, 0.25, FENCE_IN), (1.9, 0.08, 0.08)),
                        ('stile in', (cx_ + (0.93 if k == 0 else -0.93), FH/2, FENCE_IN), (0.08, FH - 0.4, 0.08)), ('stile out', (cx_ - (0.93 if k == 0 else -0.93), FH/2, FENCE_IN), (0.08, FH - 0.4, 0.08))):
        add(f'Forest: gate leaf {k} {n_}', pos, sc, mesh=BOX, material=GFRAME)
    add(f'Forest: gate leaf {k} mesh', (cx_, FH/2, FENCE_IN), (1.9, FH - 0.4, 1), mesh=PLANE, material=MESH)
add('Forest: gate chain', (8.0, 1.15, FENCE_IN + 0.12), (0.5, 0.05, 0.05), mesh=BOX, material=pbr(0.35, 0.33, 0.3, rough=0.5, metallic=0.7))
add('Forest: gate padlock', (8.0, 1.0, FENCE_IN + 0.14), (0.12, 0.16, 0.06), mesh=BOX, material=pbr(0.5, 0.42, 0.2, rough=0.4, metallic=0.8))
add('Forest: gate sign', (8.0, 1.85, FENCE_IN + 0.08), (0.9, 0.5, 1), rot=quat_y(180), mesh=PLANE, material=pbr(1, 1, 1, rough=0.9, texture='assets/images/gatesign.png'))
fence_side(W-FENCE_IN, D-FENCE_IN, FENCE_IN, D-FENCE_IN, 'N'); fence_side(FENCE_IN, D-FENCE_IN, FENCE_IN, FENCE_IN, 'W')

# ---- landmarks ------------------------------------------------------------------------------------------------------
spawn = (4.0, 4.0); layout['spawn'] = spawn
roost = (W*0.8, D*0.8)                      # bunker 7, his roost, the road's end
bunkerA = (W*0.56, D*0.42)                  # bunker 5: the count
bunkerB = (W*0.3, D*0.74)                   # bunker 6: the collars
cabin = (W*0.36, D*0.33)                    # the plant gatehouse
pond = (W*0.62, D*0.66); pr = 11.0
power = (W*0.72, D*0.9)                     # the old power house
landmarks = [(roost, 12), (bunkerA, 12), (bunkerB, 12), (cabin, 8), (pond, pr+3), (power, 8)]

# ---- the plant road: a winding polyline from the gate to bunker 7, plus spurs ------------------------------------------
def catmull(pts, per=10):
    out = []; P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P)-2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for k in range(per):
            t = k/per; t2 = t*t; t3 = t2*t
            x = 0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            z = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x, z))
    out.append(pts[-1]); return out
start = (6.0, 6.0)
door7 = (roost[0], roost[1] - 9.0)
ctrl = [(8.0, 2.6), start, (22, 30), (40, 38), (cabin[0]+16, cabin[1]-6), (bunkerA[0]-14, bunkerA[1]+4), (W*0.5, D*0.56), (bunkerB[0]+20, bunkerB[1]-2), (W*0.52, D*0.82), (W*0.66, D*0.8), door7]
road = catmull(ctrl, 8)
cum = [0.0]
for i in range(1, len(road)): cum.append(cum[-1] + math.hypot(road[i][0]-road[i-1][0], road[i][1]-road[i-1][1]))
RL = cum[-1]
def road_pt(t, side=0.0, y=0.02):
    s = t*RL
    for i in range(1, len(road)):
        if cum[i] >= s:
            f = (s-cum[i-1])/max(1e-6, cum[i]-cum[i-1]); a, b = road[i-1], road[i]
            x, z = a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f
            dx, dz = b[0]-a[0], b[1]-a[1]; l = math.hypot(dx, dz) or 1
            return (x + (-dz/l)*side, y, z + (dx/l)*side)
    return (road[-1][0], y, road[-1][1])
def road_dir(t):
    a = road_pt(max(0, t-0.01)); b = road_pt(min(1, t+0.01)); return math.degrees(math.atan2(b[0]-a[0], b[2]-a[2]))
def nearest_t(p):
    best = (1e9, 0)
    for i in range(len(road)):
        d = math.hypot(road[i][0]-p[0], road[i][1]-p[1])
        if d < best[0]: best = (d, cum[i]/RL)
    return best[1]
spurs = {}
spurs['cabin'] = catmull([road_pt(nearest_t((cabin[0], cabin[1]-10)))[::2], (cabin[0]+2, cabin[1]-12), (cabin[0], cabin[1]-6.5)], 10)
spurs['bunkerA'] = catmull([road_pt(nearest_t((bunkerA[0], bunkerA[1]-12)))[::2], (bunkerA[0]-3, bunkerA[1]-14), (bunkerA[0], bunkerA[1]-9)], 10)
spurs['bunkerB'] = catmull([road_pt(nearest_t((bunkerB[0], bunkerB[1]-12)))[::2], (bunkerB[0]+4, bunkerB[1]-15), (bunkerB[0], bunkerB[1]-9)], 10)
spurs['pond'] = catmull([road_pt(nearest_t((pond[0]-pr-6, pond[1])))[::2], (pond[0]-pr-3, pond[1]-2)], 10)
spurs['power'] = catmull([road_pt(nearest_t((power[0]-8, power[1]-8)))[::2], (power[0]-10, power[1]-2), (power[0]-6.5, power[1])], 10)
d0 = road_pt(0.2)[::2]; spurs['dead'] = catmull([d0, (d0[0]+14, d0[1]-10), (d0[0]+26, d0[1]-14)], 10)
polylines = [road] + list(spurs.values())
def near_road(x, z, r=3.0):
    for pl in polylines:
        for i in range(1, len(pl)):
            ax, az = pl[i-1]; bx_, bz_ = pl[i]; dx, dz = bx_-ax, bz_-az; l2 = dx*dx+dz*dz or 1e-6
            t = max(0, min(1, ((x-ax)*dx + (z-az)*dz)/l2))
            if math.hypot(x-(ax+dx*t), z-(az+dz*t)) < r: return True
    return False
ROAD_MAT = pbr(0.5,0.44,0.34)
seg = 0
for pl, width in [(road, 2.8)] + [(s, 2.0) for s in spurs.values()]:
    for i in range(1, len(pl)):
        a, b = pl[i-1], pl[i]; dx, dz = b[0]-a[0], b[1]-a[1]; l = math.hypot(dx, dz)
        if l < 0.05: continue
        seg += 1
        add(f'Forest: road {seg:03d}', ((a[0]+b[0])/2, 0.004, (a[1]+b[1])/2), (width, 0.008, l + width*0.4), rot=quat_y(math.degrees(math.atan2(dx, dz))), mesh=BOX, material=ROAD_MAT)

# the dog's tracks: paw prints down the road from the gate, then off toward bunker 7's spur end
PAW = pbr(1, 1, 1, texture='assets/images/paw.png', cutout='assets/images/paw.png')
def paw_trail(pts, tag, step=2.2):
    k = 0; left = True
    for i in range(1, len(pts)):
        a, b = pts[i-1], pts[i]; dx, dz = b[0]-a[0], b[1]-a[1]; l = math.hypot(dx, dz)
        if l < 0.01: continue
        n = max(1, int(l/step)); yaw = math.degrees(math.atan2(dx, dz))
        for j in range(n):
            f = (j+0.5)/n; side = (0.28 if left else -0.28) + rng.uniform(-0.1, 0.1); left = not left
            x = a[0] + dx*f + (-dz/l)*side; z = a[1] + dz*f + (dx/l)*side; k += 1
            add(f'Forest: paw {tag}{k:03d}', (x, 0.012, z), (0.22, 0.22, 1), rot=quat_yx(yaw + rng.uniform(-8, 8), 90), mesh=PLANE, material=PAW)
paw_trail([road_pt(t)[::2] for t in [i/60 for i in range(0, 25)]], 'r')          # the first ~40 % of the road
paw_trail([road_pt(t)[::2] for t in [0.94 + i/100 for i in range(0, 7)]], 'e')  # and again near the end, into bunker 7

# the dead dog on the road (not yours), removed by code once passed
dd = road_pt(0.3, 0.5, 0.0)
add_glb('Forest: dead dog', 'assets/Models/dead_dog.glb', (dd[0], 0.02, dd[2]), (1, 1, 1), rot=quat_y(road_dir(0.3) + 60))

# ---- the gatehouse cabin -------------------------------------------------------------------------------------------------
CW, CD, CH, T = 7.0, 5.0, 2.8, 0.18
cx, cz = cabin; cy = 0.0
PLANK = pbr(0.75, 0.68, 0.55, rough=0.95, texture='assets/images/planks.png')
INNER = pbr(0.62, 0.55, 0.45, rough=0.95, texture='assets/images/planks.png')
cabin_root = add('Cabin: root', (cx, cy, cz))
# CL_POINTER as well as CL_PHYSICS: a wall must stop the pointer ray, or the pages inside read through it
def cab(name, pos, scale, mat=PLANK, rot=None, collider=True, mask=CL_PHYSICS | CL_POINTER):
    return add(f'Cabin: {name}', pos, scale, rot=rot, mesh=BOX, collider=BOXC if collider else None, material=mat, parent=cabin_root, mask=mask)
# floor and roof
cab('floor', (0, 0.1, 0), (CW+0.4, 0.2, CD+0.4), pbr(0.45, 0.38, 0.28, rough=1, texture='assets/images/planks.png'))
cab('ceiling', (0, CH+0.1, 0), (CW+0.4, 0.2, CD+0.4), pbr(0.35, 0.3, 0.22, rough=1))
# pitched roof: a positive Z rotation lifts a box's +x end, so the left panel gets +24 (its ridge end is at +x) and the right -24
ROOF_L, RP = CW/2 + 1.0, math.radians(24)
RIDGE = 0.95 + math.sin(RP) * ROOF_L/2  # ridge height above the ceiling line (~1.87)
cab('roof L', (-math.cos(RP)*ROOF_L/2 + 0.1, CH+0.95, 0), (ROOF_L, 0.16, CD+1.6), pbr(0.28, 0.24, 0.2, rough=1), rot=quat_z(24), collider=False)
cab('roof R', (math.cos(RP)*ROOF_L/2 - 0.1, CH+0.95, 0), (ROOF_L, 0.16, CD+1.6), pbr(0.28, 0.24, 0.2, rough=1), rot=quat_z(-24), collider=False)
cab('ridge', (0, CH+RIDGE+0.02, 0), (0.3, 0.12, CD+1.7), pbr(0.22, 0.19, 0.16, rough=1), collider=False)
# gables: stepped plank strips that follow the roof line (a flat box stuck out above the eaves)
NSTRIP = 6
for i in range(NSTRIP):
    yc = CH + (i + 0.5) * RIDGE / NSTRIP
    w = (CW - 0.2) * (1 - (i + 0.5) / NSTRIP) + 0.2
    cab(f'gable F{i}', (0, yc, -CD/2), (w, RIDGE/NSTRIP + 0.01, T), collider=i == 0)
    cab(f'gable B{i}', (0, yc, CD/2), (w, RIDGE/NSTRIP + 0.01, T), collider=i == 0)
# front wall (-z): door gap 1.3 wide at x=+1.8, window 1.4 wide at x=-1.6 (sill 1.0, top 2.2)
def wall_with_window(tag, axis, pos_const, length, win_center, win_w, door_center=None, door_w=1.3):
    # builds wall pieces along `axis` ('x' or 'z') at constant other coordinate
    pieces = []  # (center, width, y_center, height)
    cuts = [(win_center - win_w/2, win_center + win_w/2, 'win')]
    if door_center is not None: cuts.append((door_center - door_w/2, door_center + door_w/2, 'door'))
    cuts.sort()
    cur = -length/2
    for a, b, kind in cuts:
        if a > cur: pieces.append(((cur+a)/2, a-cur, CH/2, CH))
        if kind == 'win':
            pieces.append(((a+b)/2, b-a, 0.5, 1.0)); pieces.append(((a+b)/2, b-a, 2.5, 0.6))
        else:
            pieces.append(((a+b)/2, b-a, 2.55, 0.5))
        cur = b
    if cur < length/2: pieces.append(((cur+length/2)/2, length/2-cur, CH/2, CH))
    for i, (c, w, yc, h) in enumerate(pieces):
        if axis == 'x': cab(f'wall {tag}{i}', (c, yc, pos_const), (w, h, T))
        else: cab(f'wall {tag}{i}', (pos_const, yc, c), (T, h, w))
wall_with_window('F', 'x', -CD/2, CW, -1.6, 1.4, door_center=1.8)
wall_with_window('B', 'x', CD/2, CW, 1.0, 1.4)
wall_with_window('L', 'z', -CW/2, CD, 0.3, 1.2)
wall_with_window('R', 'z', CW/2, CD, -0.3, 1.2)
GLASS = pbr(0.6, 0.7, 0.75, rough=0.1, a=0.28, alpha=True, texture='assets/images/glass.png')
for name, pos, scale in (('glass F', (-1.6, 1.6, -CD/2), (1.4, 1.2, 0.03)), ('glass B', (1.0, 1.6, CD/2), (1.4, 1.2, 0.03)),
                         ('glass L', (-CW/2, 1.6, 0.3), (0.03, 1.2, 1.2)), ('glass R', (CW/2, 1.6, -0.3), (0.03, 1.2, 1.2))):
    cab(name, pos, scale, GLASS, collider=False)
# the door: our own plank leaf (assets/Models/cabin_door.glb, 1.28 x 2.45, pivot on the hinge edge, knob on the latch side).
# The engine mirrors X on import, so with a 180 yaw the leaf runs +x from its pivot with the straps facing out (-z).
# Hinged on the left jamb (x = 1.8 - 0.65) in the wall plane; code swings it inward (-100 deg yaw).
hinge = add('Cabin: door hinge', (1.8 - 0.65, 0.2, -CD/2), parent=cabin_root)
add_glb('Cabin: door', 'assets/Models/cabin_door.glb', (0, 0, 0), (1, 1, 1), rot=quat_y(180), vis=CL_PHYSICS|CL_POINTER, invis=CL_PHYSICS, parent=hinge)
# interior: bulb, switch, stove, table with the statement and the radio, the old TV on a barrel
bulb = add('Cabin: bulb', (0, CH-0.35, 0), (0.18, 0.24, 0.18), mesh=SPH, material=pbr(0.9, 0.85, 0.7, rough=0.3, emissive=(1, 0.9, 0.7), ei=4), parent=cabin_root)
add('Cabin: bulb cord', (0, CH-0.1, 0), (0.02, 0.4, 0.02), mesh=BOX, material=pbr(0.1,0.1,0.1), parent=cabin_root)
sw = add('Cabin: switch', (1.8 + 0.9, 1.3, -CD/2 + T/2 + 0.03), (0.09, 0.14, 0.05), mesh=BOX, collider=BOXC, mask=CL_POINTER, material=pbr(0.8, 0.78, 0.7, rough=0.5), parent=cabin_root)
add('Cabin: switch plate', (1.8 + 0.9, 1.3, -CD/2 + T/2 + 0.015), (0.16, 0.22, 0.02), mesh=BOX, material=pbr(0.5, 0.48, 0.42, rough=0.6), parent=cabin_root)
add_glb('Cabin: stove', 'assets/asset-packs/salamander_stove/Stove_01/Stove_01.glb', (-CW/2 + 0.7, 0.2, CD/2 - 0.7), (1, 1, 1), rot=quat_y(135), vis=CL_PHYSICS, parent=cabin_root)
add_glb('Cabin: table', 'assets/Models/cabin_table.glb', (1.2, 0.2, 0.9), (1, 1, 1), rot=quat_y(20), vis=CL_PHYSICS, parent=cabin_root)  # plank table, top at 0.98
add_glb('Cabin: radio', 'assets/Models/radio.glb', (1.6, 0.2 + 0.78, 1.1), (0.45, 0.45, 0.45), rot=quat_y(-150), vis=0, parent=cabin_root)
add_glb('Cabin: barrel', 'assets/asset-packs/rum_barrel/Barrel_02/Barrel_02.glb', (-3.0, 0.2, -1.7), (0.9, 0.9, 0.9), vis=CL_PHYSICS, parent=cabin_root)
# a 1966 wooden console set (assets/Models/cabin_tv.glb) against the left wall under the window, facing into the room
add_glb('Cabin: tv', 'assets/Models/cabin_tv.glb', (-2.95, 0.2, -0.3), (1, 1, 1), rot=quat_y(90), vis=CL_PHYSICS, parent=cabin_root)
add_glb('Cabin: lamp outside', 'assets/Models/lamp-exterior.glb', (1.8 + 1.1, 1.9, -CD/2 - 0.2), (0.45, 0.45, 0.45), rot=quat_y(180), vis=0, parent=cabin_root)
# a deep sill shelf under each window: the beam starts half a metre ahead of the camera, so a player against the glass
# saw it go dark; the shelf keeps them a step back (owner pass 5)
for name, pos, scale in (('sill F', (-1.6, 0.47, -CD/2 + T/2 + 0.4), (1.7, 0.94, 0.8)), ('sill B', (1.0, 0.47, CD/2 - T/2 - 0.4), (1.7, 0.94, 0.8)),
                         ('sill L', (-CW/2 + T/2 + 0.4, 0.47, 0.62), (0.8, 0.94, 0.85)), ('sill R', (CW/2 - T/2 - 0.4, 0.47, -0.3), (0.8, 0.94, 1.5))):
    cab(name, pos, scale, pbr(0.36, 0.3, 0.22, rough=1))
# the cot: a low frame and a dirty mattress
cab('cot frame', (2.6, 0.35, 1.3), (0.9, 0.3, 2.0), pbr(0.3, 0.25, 0.18, rough=1)); cab('cot mattress', (2.6, 0.58, 1.3), (0.85, 0.16, 1.9), pbr(0.55, 0.52, 0.45, rough=1), collider=False)
# documents in the cabin: the typed statement on the table, the plant map on the back wall
add('Document: statement', (1.0, 0.2 + 0.79, 0.75), (0.36, 0.5, 1), rot=quat_yx(25, 90), mesh=PLANE, collider=PLANEC, mask=CL_POINTER, material=pbr(1, 1, 1, texture='assets/images/statement.png'), parent=cabin_root)
# a plane reads correctly from its -z side, which is where the player stands (inside, looking at the back wall)
add('Document: map', (-1.2, 1.7, CD/2 - T/2 - 0.03), (1.3, 0.95, 1), mesh=PLANE, collider=PLANEC, mask=CL_POINTER, material=pbr(1, 1, 1, texture='assets/images/map.png'), parent=cabin_root)
layout['cabin'] = {'x': cx, 'z': cz, 'w': CW, 'd': CD, 'h': CH, 'door': {'x': cx + 1.8, 'z': cz - CD/2}, 'bulb': {'x': cx, 'y': CH-0.35, 'z': cz},
                   'windows': [{'x': cx - 1.6, 'y': 1.6, 'z': cz - CD/2 - 1.4}, {'x': cx + 1.0, 'y': 1.6, 'z': cz + CD/2 + 1.4}, {'x': cx - CW/2 - 1.4, 'y': 1.6, 'z': cz + 0.3}, {'x': cx + CW/2 + 1.4, 'y': 1.6, 'z': cz - 0.3}]}

# ---- the storage bunkers: concrete rooms under earth mounds, a steel door gap, a stencil -------------------------------
CONC = pbr(0.5, 0.5, 0.47, rough=0.95); CONC_IN = pbr(0.42, 0.42, 0.4, rough=1); EARTH = pbr(0.26, 0.24, 0.17, rough=1)
TALLY = pbr(1, 1, 1, rough=1, texture='assets/images/tally.png')
def tiled(nx, ny):  # plane UVs (front and back faces) repeating the texture nx by ny times; tex() wraps in repeat mode
    uv = [0, 0, nx, 0, nx, ny, 0, ny]
    return {"$case": "plane", "plane": {"uvs": uv + uv}}
def bunker(tag, center, number, wall_tex=None):
    bx_, bz_ = center; RW, RD, RH = 6.0, 9.0, 3.2  # room: x width, z depth (door on -z), height
    r = add(f'Bunker: {tag} root', (bx_, 0, bz_))
    def part(n, pos, scale, mat, collider=True, rot=None, mask=CL_PHYSICS | CL_POINTER):  # walls stop the pointer ray too
        return add(f'Bunker: {tag} {n}', pos, scale, rot=rot, mesh=BOX, collider=BOXC if collider else None, material=mat, parent=r, mask=mask)
    part('floor', (0, 0.05, 0), (RW, 0.1, RD), CONC_IN)
    part('roof', (0, RH + 0.15, 0), (RW + 0.6, 0.3, RD + 0.6), CONC_IN)
    part('wall L', (-RW/2 - 0.15, RH/2, 0), (0.3, RH, RD), wall_tex or CONC_IN)
    part('wall R', (RW/2 + 0.15, RH/2, 0), (0.3, RH, RD), wall_tex or CONC_IN)
    part('wall B', (0, RH/2, RD/2 + 0.15), (RW + 0.6, RH, 0.3), CONC_IN)
    # the concrete headwall: 12 m wide with wing walls and a parapet (FH), a door gap 1.8 wide and 2.4 high
    HW, FH = 12.0, RH + 0.4
    part('facade L', (-(HW/2 + 0.9)/2, FH/2, -RD/2 - 0.3), (HW/2 - 0.9, FH, 0.6), CONC)
    part('facade R', ((HW/2 + 0.9)/2, FH/2, -RD/2 - 0.3), (HW/2 - 0.9, FH, 0.6), CONC)
    part('lintel', (0, 2.4 + (FH - 2.4)/2, -RD/2 - 0.3), (1.8, FH - 2.4, 0.6), CONC)
    part('step', (0, 0.1, -RD/2 - 1.2), (3.0, 0.2, 1.8), CONC)
    # the earth mound behind the headwall: a half-ellipsoid shell (assets/Models/mound.glb, unit radius, open at the cut),
    # its flat side flush with the back of the headwall so the doorway stays clear; it has a collider
    add_glb(f'Bunker: {tag} mound', 'assets/Models/mound.glb', (0, 0, -RD/2), (HW/2, FH - 0.1, RD/2 + 8.0), vis=CL_PHYSICS, parent=r)
    # a steel door leaf, open, hanging from the left jamb
    part('door leaf', (-0.9 - 0.08, 1.2, -RD/2 - 0.3 - 0.9), (0.08, 2.4, 1.8), pbr(0.25, 0.22, 0.2, rough=0.8, metallic=0.6), rot=quat_y(-75))
    # the stencil, right of the door on the facade
    add(f'Document: notice{number}', (2.4, 1.9, -RD/2 - 0.62), (2.0, 1.5, 1), mesh=PLANE, collider=PLANEC, mask=CL_POINTER, material=pbr(1, 1, 1, rough=1, texture=f'assets/images/notice{number}.png'), parent=r)
    return r
rA = bunker('A', bunkerA, 5)
rB = bunker('B', bunkerB, 6)
rC = bunker('C', roost, 7)
# bunker 5: the count. Tally scratches on both walls (texture) and a heap of dead moths on the floor
for i in range(9):
    add(f'Bunker: A heap {i}', (rng.uniform(-2.2, 2.2), 0.11 + i*0.004, rng.uniform(-3.5, 3.5)), (2.2, 2.2, 1), rot=quat_yx(rng.uniform(0, 360), 90), mesh=PLANE, material=pbr(1, 1, 1, texture='assets/images/mothheap.png', cutout='assets/images/mothheap.png'), parent=rA)
# the scratches: one plane over each long wall, the texture repeated at one scale (a 4 m x 2 m tile), the whole wall readable
# (custom plane UVs came out stretched in the Explorer; default UVs on 3 x 1.5 m tiles, the texture's 2:1 aspect, cannot)
n_t = 0
for sx, yaw in ((-1, -90), (1, 90)):
    for col in (-3.0, 0.0, 3.0):
        for row in (0.85, 2.35):
            n_t += 1
            add('Document: tally' + ('' if n_t == 1 else f' {n_t}'), (sx * 2.98, row, col), (3.0, 1.5, 1), rot=quat_y(yaw), mesh=PLANE, collider=PLANEC, mask=CL_POINTER, material=TALLY, parent=rA)
# bunker 6: the collars. Nine collars in a ring with their tags, and a readable tag box
def collar(name, pos, parent, color, clickable=False):
    c = add(name, pos, (1, 1, 1), parent=parent, collider=CYL(0.45, 0.45) if clickable else None, mask=CL_POINTER)
    for k in range(8):
        a = k*45
        add(f'Bunker: {name} link {k}', (math.sin(math.radians(a))*0.16, 0.02, math.cos(math.radians(a))*0.16), (0.14, 0.03, 0.04), rot=quat_y(a), mesh=BOX, material=pbr(*color, rough=0.8), parent=c)
    add(f'Bunker: {name} tag', (0.0, 0.012, -0.19), (0.05, 0.01, 0.045), mesh=BOX, material=pbr(0.75, 0.62, 0.3, rough=0.35, metallic=0.8), parent=c)
    return c
cols = [(0.3,0.17,0.09),(0.12,0.12,0.14),(0.35,0.08,0.06),(0.25,0.2,0.1),(0.1,0.2,0.3),(0.3,0.25,0.2),(0.2,0.1,0.1),(0.08,0.08,0.08),(0.33,0.2,0.12)]
for i, col in enumerate(cols):
    a = i/9*math.pi*2; collar(f'Bunker: B collar {i}', (math.cos(a)*1.4, 0.11, 1.0 + math.sin(a)*1.6), rB, col)
add('Document: tags', (0, 0.17, 1.0), (0.5, 0.14, 0.5), mesh=BOX, collider=BOXC, mask=CL_POINTER, material=pbr(0.22, 0.18, 0.12, rough=0.9), parent=rB)
# bunker 7: his roost. Duke's collar on the step, a litter of dead moths, prints up to the door
collar('Document: collar', (0.5, 0.21, -5.9), rC, (0.3, 0.17, 0.09), clickable=True)
for i in range(3):
    add(f'Bunker: C litter {i}', (rng.uniform(-1.2, 1.2), 0.21 + i*0.004, -5.9 + rng.uniform(-0.8, 0.8)), (1.6, 1.6, 1), rot=quat_yx(rng.uniform(0, 360), 90), mesh=PLANE, material=pbr(1, 1, 1, texture='assets/images/mothheap.png', cutout='assets/images/mothheap.png'), parent=rC)
layout['bunkers'] = {'count': {'x': bunkerA[0], 'z': bunkerA[1]}, 'collars': {'x': bunkerB[0], 'z': bunkerB[1]}, 'roost': {'x': roost[0], 'z': roost[1], 'door': {'x': door7[0], 'z': door7[1]}}}

# ---- pond and the old power house ---------------------------------------------------------------------------------------
add('Forest: pond', (pond[0], 0.02, pond[1]), (pr*2, 0.02, pr*1.4), mesh=CYL(1.0, 1.0), material=pbr(0.08,0.1,0.14, rough=0.05))
add('Forest: power house', (power[0], 2.0, power[1]), (9, 4, 6), mesh=BOX, collider=BOXC, material=pbr(0.42,0.4,0.36, rough=0.95))
add('Forest: power house stack', (power[0]+3, 5.5, power[1]+1.5), (1.0, 7, 1.0), mesh=CYL(0.5, 0.5), material=pbr(0.3,0.28,0.26, rough=0.95))
add('Document: notebook', (power[0] - 4.53, 1.5, power[1] - 0.5), (0.5, 0.69, 1), rot=quat_y(-90), mesh=PLANE, collider=PLANEC, mask=CL_POINTER, material=pbr(1, 1, 1, rough=1, texture='assets/images/notebook.png'))
layout['pond'] = {'x': pond[0], 'z': pond[1]}; layout['power'] = {'x': power[0], 'z': power[1]}

# ---- trees ----------------------------------------------------------------------------------------------------------------
PINE = 'assets/asset-packs/stylized_pine_tree/stylized_pine_tree/stylized_pine_tree.glb'
BIRCH = 'assets/asset-packs/green_birch_tree/green_birch_tree/green_birch_tree.glb'
ABIRCH = 'assets/asset-packs/autumn_birch_tree/autumn_birch_tree/autumn_birch_tree.glb'
count = int(W*D/68); placed = []; tries = 0
while len(placed) < count and tries < 60000:
    tries += 1
    kind = 'pine' if rng.random() < 0.4 else ('abirch' if rng.random() < 0.3 else 'birch')
    margin = FENCE_IN + (6.5 if kind == 'pine' else 3.0)
    x = rng.uniform(margin, W-margin); z = rng.uniform(margin, D-margin)
    if math.hypot(x-start[0], z-start[1]) < 9: continue
    if math.hypot(x-road_pt(0.03)[0], z-road_pt(0.03)[2]) < 7: continue
    if any(math.hypot(x-c[0], z-c[1]) < rad for c, rad in landmarks): continue
    if near_road(x, z, 3.2 if kind != 'pine' else 4.2): continue
    if any(math.hypot(x-px, z-pz) < 4.4 for px, pz, _ in placed): continue
    placed.append((x, z, kind))
for i, (x, z, kind) in enumerate(placed):
    yaw = rng.uniform(0, 360)
    if kind == 'pine': sc = rng.uniform(0.5, 0.72); src = PINE; trunk_r = 0.35
    else: sc = rng.uniform(0.9, 1.25); src = BIRCH if kind == 'birch' else ABIRCH; trunk_r = 0.22
    t = add_glb(f'Forest: tree {i+1:03d}', src, (x, 0, z), (sc, sc, sc), rot=quat_y(yaw))
    add(f'Forest: tree {i+1:03d} trunk collider', (0, 2.5/sc, 0), (trunk_r*2/sc, 5/sc, trunk_r*2/sc), collider=CYL(0.5, 0.5), parent=t)

# ---- the gate: the newspaper and the sign ------------------------------------------------------------------------------
np_ = road_pt(0.03, 1.4, 0.012)
add('Document: register', np_, (0.5, 0.75, 1), rot=quat_yx(rng.uniform(0, 360), 90), mesh=PLANE, collider=PLANEC, mask=CL_POINTER, material=pbr(1, 1, 1, rough=0.95, texture='assets/images/newspaper.png'))
sp = road_pt(0.025, -1.8)
add_glb('Forest: sign', 'assets/asset-packs/blank_post_sign/blank_post_sign/blank_post_sign.glb', (sp[0], 0, sp[2]), (2.2, 2.2, 2.2), rot=quat_y(road_dir(0.025) + 180), vis=0, invis=CL_PHYSICS)
layout['sign'] = {'x': sp[0], 'z': sp[2]}
json.dump(comp, open(cp, 'w'), indent=2); open(cp, 'a').write('\n')

# ---- textures that depend on the layout: the plant map and the three stencils ----------------------------------------------
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = '/System/Library/Fonts/Supplemental/'
def font(n, s): return ImageFont.truetype(F+n, s)
img = Image.new('RGB', (768, 560), (205, 196, 170)); d = ImageDraw.Draw(img)
d.rectangle((8, 8, 759, 551), outline=(60, 50, 40), width=3)
d.text((384, 34), 'WEST VIRGINIA ORDNANCE WORKS', font=font('Times New Roman Bold.ttf', 26), fill=(40, 32, 24), anchor='mm')
d.text((384, 62), 'T.N.T. (EXPLOSIVES) STORAGE AREA  -  PLANT MAP, 1944', font=font('Times New Roman.ttf', 17), fill=(60, 50, 40), anchor='mm')
sc_ = min(688/W, 440/D); ox, oy = 384 - W*sc_/2, 86 + 440 - (440 - D*sc_)/2  # scene x -> right, scene z -> up; fitted and centred under the title
def mp(x, z): return (ox + x*sc_, oy - z*sc_)
d.line([mp(*p) for p in road], fill=(90, 70, 50), width=4)
for s_ in spurs.values(): d.line([mp(*p) for p in s_], fill=(110, 90, 70), width=2)
for (c, n_, label) in ((bunkerA, 5, 'BUNKER 5'), (bunkerB, 6, 'BUNKER 6'), (roost, 7, 'BUNKER 7')):
    x, y = mp(*c); d.ellipse((x-16, y-16, x+16, y+16), outline=(50, 40, 30), width=3); d.text((x, y-26), label, font=font('Times New Roman Bold.ttf', 14), fill=(50, 40, 30), anchor='mm')
x, y = mp(*cabin); d.rectangle((x-10, y-7, x+10, y+7), outline=(50, 40, 30), width=2); d.text((x-16, y), 'GATEHOUSE', font=font('Times New Roman.ttf', 13), fill=(50, 40, 30), anchor='rm')
x, y = mp(*power); d.rectangle((x-12, y-8, x+12, y+8), fill=(50, 40, 30)); d.text((x-18, y), 'POWER HOUSE', font=font('Times New Roman.ttf', 13), fill=(50, 40, 30), anchor='rm')
x, y = mp(*pond); d.ellipse((x-22, y-16, x+22, y+16), outline=(40, 60, 90), width=2); d.text((x, y), 'POND', font=font('Times New Roman.ttf', 12), fill=(40, 60, 90), anchor='mm')
x, y = mp(*spawn); d.text((x+10, y-10), 'GATE', font=font('Times New Roman Bold.ttf', 14), fill=(50, 40, 30), anchor='lm')
d.text((384, 530), 'Storage bunkers: concrete rooms under earth, each held 250 tons of TNT. Kept 400 yards apart. NO OPEN LIGHT.', font=font('Times New Roman Italic.ttf', 13), fill=(60, 50, 40), anchor='mm')
# a note in blue ballpoint beside bunker 7, and a loose ring round it: a pen marking, not print (owner pass 9)
x, y = mp(*roost); ink = (26, 34, 112)
d.ellipse((x - 25, y - 23, x + 27, y + 21), outline=ink, width=2)
note = Image.new('RGBA', (230, 64), (0, 0, 0, 0)); nd = ImageDraw.Draw(note)
nd.text((4, 2), '7 - "the big one"', font=font('Bradley Hand Bold.ttf', 20), fill=ink + (235,))
nd.text((4, 30), 'lights fail here', font=font('Bradley Hand Bold.ttf', 20), fill=ink + (235,))
nd.line((6, 54, 150, 52), fill=ink + (200,), width=2)
note = note.rotate(4, resample=Image.BICUBIC, expand=True)
img.paste(note, (int(x + 24), int(y - 34)), note)
img.save(os.path.join(root, 'assets/images/map.png'))
for n_ in (5, 6, 7):
    img = Image.new('RGB', (512, 384), (122, 120, 112)); px = img.load(); r2 = random.Random(n_)
    for y in range(0, 384, 2):
        for x in range(0, 512, 2):
            k = r2.randint(-22, 22); px[x, y] = (122+k, 120+k, 112+k)
    d = ImageDraw.Draw(img); yel = (196, 170, 60)
    d.text((256, 42), f'STORAGE BUNKER No. {n_}', font=font('Impact.ttf', 44), fill=yel, anchor='mm')
    d.text((256, 92), 'WEST VIRGINIA ORDNANCE WORKS', font=font('Impact.ttf', 24), fill=yel, anchor='mm')
    d.text((256, 150), 'T.N.T.  -  HIGH EXPLOSIVE', font=font('Impact.ttf', 42), fill=yel, anchor='mm')
    d.text((256, 200), 'CAPACITY 250 TONS', font=font('Impact.ttf', 24), fill=yel, anchor='mm')
    d.text((256, 250), 'NO FLAME   NO SMOKING   NO OPEN LIGHT', font=font('Impact.ttf', 24), fill=yel, anchor='mm')
    d.text((256, 310), 'U.S. ARMY ORDNANCE DEPT.  1943', font=font('Impact.ttf', 20), fill=yel, anchor='mm')
    if n_ == 7:
        for k in range(3): d.line((150, 268+k*5, 420, 270+k*5), fill=(230,225,210), width=2)
    img.filter(ImageFilter.GaussianBlur(0.6)).save(os.path.join(root, f'assets/images/notice{n_}.png'))
# the reporter's notebook page
img = Image.new('RGB', (512, 704), (228, 224, 210)); d = ImageDraw.Draw(img)
for y in range(70, 704, 34): d.line((30, y, 482, y), fill=(170, 180, 200), width=1)
d.line((60, 0, 60, 704), fill=(210, 120, 120), width=2)
hand = font('AmericanTypewriter.ttc', 19)
lines = ['Nov 15 - M. Hyre, Messenger', '', 'Calls since Saturday: 500+.', 'TVs going dark, whine first.', 'Phones dead on Route 62.', 'Cars stalling by the plant.', '', 'EVERY sighting in a light.', 'Headlights. Porch lamp.', "Partridge's flashlight.", 'Nobody has seen it in the dark.', 'Nobody has looked.', '', 'Hal: a dog on the plant road', 'Monday - gone by the time he', 'got back with the truck.', 'Third dog this month.', '', 'The bunkers. Check the bunkers.']
for i, l in enumerate(lines): d.text((72, 44 + i*34), l, font=hand, fill=(40, 45, 70))
img.save(os.path.join(root, 'assets/images/notebook.png'))

# ---- src/layout.ts ---------------------------------------------------------------------------------------------------------
layout['size'] = {'w': W, 'd': D}
with open(os.path.join(root, 'src/layout.ts'), 'w') as f:
    f.write('// Generated by scripts/gen-forest.py. Key spots of the layout, in scene metres. Do not edit by hand.\n')
    f.write('export const layout = ' + json.dumps(layout, indent=2) + '\n')
print(f'scene {W}x{D} m, road {RL:.0f} m in {seg} segments, {len(placed)} trees, entities up to {next_id-1}')

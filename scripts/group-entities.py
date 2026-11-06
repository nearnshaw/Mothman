#!/usr/bin/env python3
"""
Tidy the Creator Hub entity tree: put the mass-generated root entities (hundreds of trees, fence pieces, bracken...)
under empty parent entities so the tree shows a dozen collapsed groups instead of a thousand rows.

The group entities sit at the origin with identity rotation and scale, so every child's position, rotation and scale
are unchanged in the world. Code that finds entities by name keeps working: names are untouched.

Usage: python3 scripts/group-entities.py [in.composite] [out.composite]   (defaults: assets/scene/main.composite, in place)
Run it with the scene CLOSED in the Creator Hub: the editor autosaves the whole composite from memory and would
overwrite the result. Re-runnable: entities already inside a group are left alone.
"""
import json, sys, os, re

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, 'assets/scene/main.composite')
dst = sys.argv[2] if len(sys.argv) > 2 else src

# (name prefix of the members, group name). First matching rule wins. Only root-level entities are moved.
RULES = [
    ('Forest: tree ', 'Forest: trees'),
    ('Forest: fence ', 'Forest: fence'),
    ('Forest: gate ', 'Forest: gate'),
    ('Forest: paw ', 'Forest: paw prints'),
    ('Environment: verge bracken', 'Environment: bracken'),
    ('Environment: woodland bracken', 'Environment: bracken'),
    ('Cabin: ', 'Cabin'),
    ('Bunker: A ', 'Bunker A'),
    ('Bunker: B ', 'Bunker B'),
    ('Bunker: C ', 'Bunker C'),
    ('Document: ', 'Documents'),
]
MIN_MEMBERS = 3  # a group with fewer members is not worth a row

comp = json.load(open(src))
comps = {c['name']: c for c in comp['components']}
names = comps['core-schema::Name']['data']; tr = comps['core::Transform']['data']
nodes = comps['inspector::Nodes']['data']['0']['json']['value']
node_of = {n['entity']: n for n in nodes}
root_node = node_of[0]
group_names = {g for _, g in RULES}

members = {}  # group name -> [entity ids]
for eid, d in names.items():
    v = d['json']['value']
    if v in group_names or eid not in tr or tr[eid]['json'].get('parent', 0) != 0: continue
    for prefix, group in RULES:
        if v.startswith(prefix): members.setdefault(group, []).append(int(eid)); break

used = [int(e) for c in comp['components'] for e in c['data'].keys()] + [n['entity'] for n in nodes]
next_id = max([511] + used) + 1
existing = {d['json']['value']: int(eid) for eid, d in names.items() if d['json']['value'] in group_names}
moved = 0
for group, ids in members.items():
    if len(ids) < MIN_MEMBERS and group not in existing: continue
    if group in existing: gid = existing[group]
    else:
        gid = next_id; next_id += 1
        tr[str(gid)] = {"json": {"position": {"x": 0, "y": 0, "z": 0}, "scale": {"x": 1, "y": 1, "z": 1}, "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}, "parent": 0}}
        names[str(gid)] = {"json": {"value": group}}
        node_of[gid] = {"entity": gid, "open": False, "children": []}; nodes.append(node_of[gid])
        # the group takes the place of its first member in the tree, so the top level keeps its order
        first = min(root_node['children'].index(i) for i in ids if i in root_node['children'])
        root_node['children'].insert(first, gid)
    idset = set(ids)
    root_node['children'] = [c for c in root_node['children'] if c not in idset]
    node_of[gid]['children'] += ids
    for i in ids: tr[str(i)]['json']['parent'] = gid
    moved += len(ids)
    print(f'{group}: {len(ids)} entities')

# leftovers: big families still at the root, for the next edit of RULES
fam = {}
for c in root_node['children']:
    v = names.get(str(c), {}).get('json', {}).get('value', '')
    fam.setdefault(re.sub(r'\s*[\d.]+[A-Za-z]?\d*\s*$', '', v).strip(), []).append(c)
big = {k: len(v) for k, v in fam.items() if len(v) >= 4 and k not in group_names}
if big: print('still at the root with 4+ members:', big)
json.dump(comp, open(dst, 'w'), indent=2)  # same formatting as the Hub writes, no trailing newline
print(f'moved {moved} entities; root now has {len(root_node["children"])} rows -> {dst}')

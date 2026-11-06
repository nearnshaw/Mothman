# Environment art source. Generates into /tmp/mothman-art; does not modify the composite.
# See design/environment-art.md for build and live-placement instructions.
import bpy, math, random, json, os
import numpy as np
from mathutils import Vector
from pathlib import Path
O=Path('/tmp/mothman-art'); ROOT=Path(os.environ.get('MOTHMAN_ROOT', os.getcwd())); rng=random.Random(1966)
def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,texture=None,color=(.3,.3,.3,1),rough=.9,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(O/texture),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
soil=mat('Forest loam','forest-floor.png'); roadmat=mat('Old gravel','old-gravel-track.png'); concrete=mat('Weathered concrete','bunker-concrete.png'); steel=mat('Oxidized steel','bunker-steel.png',rough=.68,metal=.6)
# One UV palette for fur, leather, brass and vegetation.
cols=[(.24,.16,.09,1),(.43,.29,.16,1),(.11,.095,.075,1),(.66,.52,.32,1),(.055,.05,.04,1),(.42,.35,.19,1),(.19,.23,.12,1),(.3,.33,.18,1),(.23,.08,.045,1),(.12,.17,.19,1),(.32,.27,.19,1),(.53,.52,.43,1),(.34,.39,.22,1),(.16,.14,.10,1),(.58,.42,.22,1),(.76,.65,.4,1)]
im=bpy.data.images.new('Woodland palette',64,64);pixels=[]
for y in range(64):
 for x in range(64):pixels.extend(cols[(y//16)*4+x//16])
im.pixels=pixels;im.filepath_raw=str(O/'woodland-palette.png');im.file_format='PNG';im.save()
palette=mat('Woodland palette','woodland-palette.png')
def color_obj(o,i):
 o.data.materials.clear();o.data.materials.append(palette);uv=o.data.uv_layers.active or o.data.uv_layers.new()
 for q in uv.data:q.uv=((i%4+.5)/4,(i//4+.5)/4)
 return o
def mesh(name,verts,faces,material,uvs=None):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o)
 if material:m.materials.append(material)
 if uvs:
  uv=m.uv_layers.new()
  for poly in m.polygons:
   for li in poly.loop_indices:uv.data[li].uv=uvs[m.loops[li].vertex_index]
 return o
def cube(name,p,s,material=concrete,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if material:o.data.materials.append(material)
 # World-scale box UVs, avoiding stretched detail on long walls.
 uv=o.data.uv_layers.active
 for f in o.data.polygons:
  ax=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=ax]
  for li in f.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/3,co[axes[1]]/3)
 if bevel:
  m=o.modifiers.new('Chipped arris','BEVEL');m.width=bevel;m.segments=1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 return o
def ell(name,p,s,i,segments=16,rings=10):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=p);o=bpy.context.object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);color_obj(o,i)
 for f in o.data.polygons:f.use_smooth=True
 return o
def rod(name,a,b,r,i,r2=None):
 v=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=r,radius2=r2 if r2 is not None else r,depth=v.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();color_obj(o,i);return o
def tube(name,points,r,i):
 for a,b in zip(points,points[1:]):rod(name,a,b,r,i)
def torus(name,p,major,minor,i,rot=(0,0,0),scale=(1,1,1)):
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=6,location=p,major_radius=major,minor_radius=minor,rotation=rot);o=bpy.context.object;o.name=name;o.scale=scale;return color_obj(o,i)
manifest={}
def export(name):
 # Merge by material so repeated fine detail does not cost hundreds of renderers.
 groups={}
 for o in list(bpy.context.scene.objects):
  if o.type=='MESH':groups.setdefault(tuple(m.name for m in o.data.materials),[]).append(o)
 for group in groups.values():
  bpy.ops.object.select_all(action='DESELECT')
  for o in group:o.select_set(True)
  bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join()
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];tri=0;pts=[]
 for o in meshes:
  o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles);pts += [o.matrix_world@Vector(v) for v in o.bound_box]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 manifest[name]={'triangles':tri,'dclMin':[-hi[0],lo[2],-hi[1]],'dclMax':[-lo[0],hi[2],-lo[1]],'materials':len({m.name for o in meshes for m in o.data.materials if m})}
 bpy.ops.export_scene.gltf(filepath=str(O/(name+'.glb')),export_format='GLB',export_yup=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
 print('AUDIT',name,manifest[name],flush=True)
def render(name,pos,target,ortho):
 bpy.ops.object.camera_add(location=pos);cam=bpy.context.object;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=ortho;bpy.context.scene.camera=cam
 for p,power,size in [((4,-5,9),1500,7),((-5,2,5),900,5)]:
  bpy.ops.object.light_add(type='AREA',location=p);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector(target)-l.location).to_track_quat('-Z','Y').to_euler()
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.world.color=(.2,.2,.2);sc.render.resolution_x=1100;sc.render.resolution_y=750;sc.render.resolution_percentage=100;sc.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
# Sculpted, unified canine body lying on its side: the ribcage, flank, neck and head blend rather than intersect.
clear();parts=[]
for nm,p,s in [('ribcage',(-.12,0,.24),(.52,.20,.23)),('haunch',(.36,.015,.21),(.29,.18,.19)),('neck',(-.55,.01,.21),(.24,.14,.16)),('skull',(-.75,.0,.18),(.20,.145,.15)),('muzzle',(-.94,-.035,.13),(.19,.09,.085))]:parts.append(ell(nm,p,s,1))
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object
rem=body.modifiers.new('Continuous anatomy','REMESH');rem.mode='VOXEL';rem.voxel_size=.028;bpy.ops.object.modifier_apply(modifier=rem.name)
sm=body.modifiers.new('Relax skin','SMOOTH');sm.factor=1;sm.iterations=3;bpy.ops.object.modifier_apply(modifier=sm.name)
dec=body.modifiers.new('Game mesh','DECIMATE');dec.ratio=.28;bpy.ops.object.modifier_apply(modifier=dec.name)
color_obj(body,1)
for f in body.data.polygons:f.use_smooth=True
# Color the upper back darker and muzzle lighter through the common atlas.
uv=body.data.uv_layers.active
for f in body.data.polygons:
 c=body.matrix_world@f.center;i=2 if c.y>.04 and c.x>-.55 else (3 if c.x<-.86 else 1)
 for li in f.loop_indices:uv.data[li].uv=((i%4+.5)/4,(i//4+.5)/4)
for nm,a,b,c in [('fore near',(-.38,-.09,.20),(-.44,-.34,.10),(-.70,-.51,.06)),('fore far',(-.32,.08,.18),(-.18,-.32,.08),(-.40,-.55,.055)),('hind near',(.38,-.06,.21),(.48,-.34,.12),(.18,-.53,.06)),('hind far',(.47,.06,.17),(.67,-.24,.10),(.47,-.45,.055))]:
 rod(nm,a,b,.085,1,.055);ell(nm+' joint',b,(.06,.065,.065),1);rod(nm+' shin',b,c,.048,1,.035);ell(nm+' paw',c,(.095,.055,.047),3)
# Drooping triangular ears with a folded ridge.
for x,y,z in [(-.68,-.075,.29),(-.69,.105,.25)]:
 o=mesh('Folded ear',[(x-.08,y,z),(x+.07,y+.03,z+.01),(x+.045,y-.17,z-.14),(x-.03,y-.09,z-.045)],[(0,1,3),(1,2,3),(2,0,3),(0,2,1)],palette);color_obj(o,2)
ell('Nose',(-1.085,-.04,.135),(.045,.07,.043),4)
tube('Closed eyelid',[(-.85,-.114,.245),(-.79,-.124,.25),(-.75,-.116,.242)],.008,4)
tube('Relaxed mouth',[(-1.06,-.10,.12),(-.94,-.12,.11),(-.85,-.115,.115)],.006,4)
pts=[(.53,.035,.20),(.72,.10,.14),(.87,.16,.075),(1.01,.11,.05),(1.1,.02,.045)]
for i,(a,b) in enumerate(zip(pts,pts[1:])):rod('Tail',a,b,.065-i*.013,2,.05-i*.012)
torus('Hound leather collar',(-.55,0,.21),.143,.021,8,rot=(0,math.pi/2,0),scale=(1,1,.86))
ell('Hound brass tag',(-.57,-.15,.09),(.038,.009,.045),15,16,8)
export('dead-dog-v2')
# A supple oval leather band, stitched edges, buckle, punched holes and hanging brass identification tag.
for variant,col in [('leather',0),('red',8),('blue',9)]:
 clear();verts=[];faces=[];N=64
 for k in range(N):
  a=k*2*math.pi/N
  for rad,z in [(1,.012),(1,.065),(.92,.065),(.92,.012)]:verts.append((.19*math.cos(a)*rad,.145*math.sin(a)*rad,z+.007*math.sin(a*3)))
 for k in range(N):
  if 13<=k<=17:continue # chewed-through gap, buckle still fastened
  for j in range(4):faces.append((4*k+j,4*((k+1)%N)+j,4*((k+1)%N)+(j+1)%4,4*k+(j+1)%4))
 color_obj(mesh('Bent leather band',verts,faces,palette),col)
 for z in [.024,.054]:
  for k in range(40):
   a=k*2*math.pi/40
   if 1.24<a<1.8:continue
   b=a+.055;tube('Saddle stitch',[(.192*math.cos(a),.147*math.sin(a),z),(.192*math.cos(b),.147*math.sin(b),z)],.0016,3)
 # buckle lies against front of band, readable from above
 tube('Brass buckle',[(-.045,-.155,.018),(-.045,-.205,.018),(.045,-.205,.018),(.045,-.155,.018),(-.045,-.155,.018)],.007,15)
 rod('Buckle tongue',(0,-.15,.022),(0,-.205,.022),.003,15)
 for x in [.07,.09,.11]:ell('Punched hole',(x,-.13,.064),(.004,.005,.002),4,8,4)
 torus('Tag split ring',(.045,-.17,.019),.022,.003,11)
 ell('Oval brass tag',(.05,-.215,.014),(.034,.043,.007),15,24,8)
 # engraving geometry, kept tiny and dark; reading document still uses existing clue UI.
 for x in [.035,.045,.055,.065]:rod('Stamped tag mark',(x,-.22,.021),(x,-.205,.021),.0015,4)
 export('collar-'+variant+'-v2')
 if False:render('collar-study',(.5,-.7,.8),(0,-.03,.025),.57)
# Bunker shell: preserve exact existing opening and interior envelope; bevels, seams, buttresses and vent details.
clear()
for name,p,s in [('floor',(0,0,.05),(6,9,.1)),('roof',(0,0,3.35),(6.6,9.6,.3)),('left',(3.15,0,1.6),(.3,9,3.2)),('right',(-3.15,0,1.6),(.3,9,3.2)),('rear',(0,-4.65,1.6),(6.6,.3,3.2)),('head left',(3.45,4.8,1.8),(5.1,.6,3.6)),('head right',(-3.45,4.8,1.8),(5.1,.6,3.6)),('lintel',(0,4.8,3),(1.8,.6,1.2)),('step',(0,5.7,.1),(3,1.8,.2))]:cube(name,p,s,bevel=.045)
for side in [-1,1]:
 # tapering wing walls, outside circulation
 x=side*5.8;cube('Wing retaining wall',(x,5.6,.65),(.42,2.6,1.3),bevel=.055)
 cube('Cap drip edge',(side*3.45,4.84,3.64),(5.2,.78,.14),bevel=.025)
 cube('Door steel jamb',(side*.91,5.12,1.22),(.07,.07,2.44),steel,bevel=.012)
 for z in [.35,1.2,2.1]:
  ell('Jamb bolt',(side*.91,5.17,z),(.026,.013,.026),11,10,6)
# rusty ventilation grille on left headwall, clear of the existing notice on the right (DCL x positive)
cube('Vent recess',(3.6,5.115,2.6),(1,.035,.55),steel)
for i in range(6):cube('Louver',(3.6,5.17,2.38+i*.085),(1.02,.09,.035),steel,.005)
for x in [-5.6,-1.3,1.3,5.6]:
 for z in [.7,2.85]:ell('Formwork tie',(x,5.108,z),(.035,.008,.035),13,8,6)
export('bunker-shell-v2')
# Existing earth mound gets a more irregular surface and forest-floor UVs, same envelope and open front.
clear();bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/Models/mound.glb'))
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 o.data.materials.clear();o.data.materials.append(soil);uv=o.data.uv_layers.active or o.data.uv_layers.new()
 for v in o.data.vertices:
  if v.co.z>.03:v.co.z=math.sqrt(max(0,1-abs(v.co.x)**4-abs(v.co.y)**4))*(1+.018*math.sin(v.co.x*15)*math.cos(v.co.y*13))
 for f in o.data.polygons:
  f.use_smooth=True
  for li in f.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co.x*2,co.y*4)
export('bunker-mound-v2')
# Recover the original authored road curves without executing the generator or touching the scene.
s=(ROOT/'scripts/gen-forest.py').read_text();env={'math':math,'W':192,'D':192,'layout':{}};exec(s[s.index('spawn = (4.0'):s.index('ROAD_MAT =')],env)
lines=env['polylines'];points=[]
for pl in lines:
 for a,b in zip(pl,pl[1:]):
  le=math.dist(a,b)
  for i in range(max(1,int(le/.65))):t=i/max(1,int(le/.65));points.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t))
P=np.array(points)
# Ground relief feathered to zero along the road and at clues/buildings; forest roots stay close to grade.
clear();verts=[];uvs=[];faces=[];step=1.5;N=129
landmarks=env['landmarks']
for j in range(N):
 for i in range(N):
  x=i*step;z=j*step;dist=float(np.sqrt(((P-[x,z])**2).sum(axis=1)).min());fade=max(0,min(1,(dist-3)/5))
  for (c,r) in landmarks:fade*=max(0,min(1,(math.dist((x,z),c)-r)/4))
  h=fade*(.07+.12*(.5+.5*math.sin(x*.23)*math.cos(z*.19))+.07*math.sin(x*.08+z*.12)**2)
  if min(x,z,192-x,192-z)<1:h=0
  verts.append((96-x,96-z,h));uvs.append((x/5,z/5))
for j in range(N-1):
 for i in range(N-1):a=j*N+i;faces.append((a,a+1,a+N+1,a+N))
mesh('Undulating woodland ground',verts,faces,soil,uvs);export('forest-ground-v2')
# Continuous ribbons eliminate the overlapping rectangular path tiles.
clear()
for idx,pl in enumerate(lines):
 verts=[];uvs=[];faces=[];length=0;width=3.6 if idx==0 else 2.65
 for k,(x,z) in enumerate(pl):
  a=pl[max(0,k-1)];b=pl[min(len(pl)-1,k+1)];dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz) or 1
  if k:length+=math.dist(pl[k-1],pl[k])
  half=width/2*(1+.07*math.sin(length*1.6)+.04*math.sin(length*3.1))
  for off in [-1,-.55,0,.55,1]:
   xx=x-dz/L*half*off;zz=z+dx/L*half*off
   verts.append((96-xx,96-zz,.005+idx*.00045+(.003 if abs(off)<1 else 0)));uvs.append(((off+1)/2,length/5))
 for k in range(len(pl)-1):
  for c in range(4):a=k*5+c;faces.append((a+5,a+6,a+1,a))
 mesh('Track '+str(idx),verts,faces,roadmat,uvs)
export('forest-tracks-v2')
# Shared clusters of bracken, fallen leaves and small stones: sparse, low, no blockers.
clear()
for k in range(11):
 a=rng.random()*math.tau;le=rng.uniform(.3,.8);p=(math.cos(a)*.1,math.sin(a)*.1,0);tip=(math.cos(a)*le,math.sin(a)*le,rng.uniform(.18,.42))
 rod('Bracken stem',p,tip,.006,6)
 for t in [.25,.4,.55,.7,.85]:
  c=Vector(p).lerp(Vector(tip),t);w=.24*(1-t)
  for side in [-1,1]:
   end=c+Vector((-math.sin(a)*w*side,math.cos(a)*w*side,.025));o=mesh('Fern leaflet',[c,c+Vector((math.cos(a)*.10,math.sin(a)*.10,.01)),end],[(0,1,2),(2,1,0)],palette);color_obj(o,7 if k%2 else 6)
for k in range(8):ell('Weathered stone',(rng.uniform(-.7,.7),rng.uniform(-.7,.7),.025),(rng.uniform(.04,.13),rng.uniform(.04,.10),rng.uniform(.025,.07)),10,8,5)
export('forest-floor-cluster-v2')
json.dump(manifest,open(O/'manifest.json','w'),indent=2)

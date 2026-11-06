"""Second art pass. Blender CLI; source assets unchanged, exports versioned GLBs."""
import bpy, math, json, os
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd();OUT=Path('/tmp/mothman-v3');OUT.mkdir(exist_ok=True)
# Reuse mesh and export utilities from the first art pass, without executing its scene generation.
s=(ROOT/'scripts/build-environment-art.py').read_text();exec(s[:s.index('# Sculpted, unified canine body')]);O=OUT
T=ROOT/'assets/Images/woodland-v3'
def pbr(name,base,normalmap=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.9
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(T/base));m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 if normalmap:
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(T/normalmap));t.image.colorspace_settings.name='Non-Color';nm=n.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
 return m
fur=pbr('Short weathered hound coat','hound-fur.png','hound-normal.png')
clear();parts=[]
# Lean hound anatomy: deeper chest, tucked abdomen, angular hocks, long muzzle.
for nm,p,s in [('thorax',(-.18,.01,.205),(.42,.185,.17)),('abdomen',(.15,.01,.205),(.30,.135,.15)),('hip',(.40,.03,.17),(.20,.16,.14)),('shoulder',(-.44,-.035,.20),(.19,.16,.18)),('neck',(-.59,.01,.19),(.22,.115,.13)),('cranium',(-.77,-.005,.16),(.155,.115,.12)),('cheek',(-.84,-.025,.125),(.12,.1,.09)),('muzzle',(-.985,-.025,.10),(.18,.064,.058))]:parts.append(ell(nm,p,s,1,24,16))
legs=[((-.42,-.07,.22),(-.48,-.30,.11),(-.71,-.58,.046)),((-.32,.05,.16),(-.23,-.30,.075),(-.44,-.62,.043)),((.38,-.04,.19),(.53,-.23,.12),(.30,-.42,.06)),((.44,.07,.16),(.68,-.18,.10),(.55,-.48,.045))]
for a,b,c in legs:
 parts += [rod('Upper limb',a,b,.071,1,.047),ell('Elbow or hock',b,(.047,.048,.052),1),rod('Tapered distal limb',b,c,.039,1,.023),ell('Metacarpal pad',c,(.073,.048,.033),1)]
pts=[(.50,.03,.18),(.70,.09,.12),(.87,.15,.065),(1.01,.12,.034),(1.1,.04,.027)]
for k,(a,b) in enumerate(zip(pts,pts[1:])):parts.append(rod('Relaxed tail',a,b,.05-k*.011,1,.04-k*.01))
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object
rem=body.modifiers.new('Joined skin','REMESH');rem.mode='VOXEL';rem.voxel_size=.012;bpy.ops.object.modifier_apply(modifier=rem.name)
sm=body.modifiers.new('Anatomical continuity','SMOOTH');sm.factor=.65;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name)
dec=body.modifiers.new('Game topology','DECIMATE');dec.ratio=.32;bpy.ops.object.modifier_apply(modifier=dec.name)
def coat(o):
 o.data.materials.clear();o.data.materials.append(fur);uv=o.data.uv_layers.active or o.data.uv_layers.new()
 for f in o.data.polygons:
  f.use_smooth=True
  for li in f.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((p.x+1.2)/2.4,(math.atan2(p.z-.16,p.y)/math.tau)%1)
coat(body)
# Thin pendant ears with a soft fold, avoiding the triangular cartoon ear silhouette.
for sign in [-1,1]:
 verts=[]
 for i in range(7):
  t=i/6;cx=-.73+.09*t;cy=sign*.08-.22*t;cz=.24-.18*t+.025*math.sin(t*math.pi);width=.052*math.sin(.3+t*2.6)
  for k in [-1,0,1]:verts.append((cx+width*k,cy,cz+.016*(1-k*k)))
 faces=[]
 for i in range(6):
  for k in range(2):a=i*3+k;faces.append((a,a+1,a+4,a+3))
 o=mesh('Soft folded ear',verts,faces,None);sol=o.modifiers.new('Ear thickness','SOLIDIFY');sol.thickness=.009;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sol.name)
 sub=o.modifiers.new('Ear fold smoothing','SUBSURF');sub.levels=2;bpy.ops.object.modifier_apply(modifier=sub.name);coat(o)
for a,b,c in legs:
 for k in [-1,0,1]:
  o=ell('Individual toe',(c[0]-.035,c[1]+k*.027,c[2]),(.044,.018,.025),1,16,8);coat(o)
  ell('Small worn claw',(c[0]-.073,c[1]+k*.027,c[2]-.002),(.017,.007,.008),13,10,6)
ell('Textured nose',(-1.13,-.027,.105),(.033,.052,.027),4,24,12)
for yy in [-.064,.008]:ell('Nostril',(-1.154,yy,.105),(.008,.012,.009),2,12,6)
tube('Closed eye crease',[(-.86,-.098,.204),(-.82,-.107,.208),(-.785,-.104,.201)],.0038,4)
tube('Lip line',[(-1.12,-.075,.079),(-1.01,-.087,.074),(-.91,-.10,.079),(-.85,-.10,.09)],.003,4)
torus('Worn leather collar',(-.58,0,.19),.143,.014,8,rot=(0,math.pi/2,0),scale=(1,1,.9));ell('Collar tag',(-.60,-.123,.077),(.027,.005,.032),15,20,10)
export('dead-dog-v3');render('hound-study',(0,-2.8,2.5),(-.1,-.15,.14),2.65)
# The road (forest-tracks-v3.glb) is built by scripts/build-road-v4.py: the vertex-colour alpha feathering that lived here
# is ignored by the Unity Explorer (hard stair-stepped edges), so the road now uses an opaque mesh plus a texture-alpha shoulder.
# Re-use the concrete geometry, add normal detail and subtle mineral stains.
clear();bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/Models/bunker-shell-v2.glb'));con=pbr('Damp cast concrete','concrete.png','concrete-normal.png')
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  for slot in o.material_slots:
   if slot.material and 'concrete' in slot.material.name.lower():slot.material=con
export('bunker-shell-v3')
# Close the front earth cover around the concrete shell.
clear();verts=[];faces=[];uv=[];nx=40;nz=40
# Native normalized mound: front crown tucks beneath concrete coping, rear rises gently.
for j in range(nz+1):
 z=j/nz
 for i in range(nx+1):
  x=-1+2*i/nx;h=math.sqrt(max(0,1-x**4))*math.sqrt(max(0,1-z**4))*(.74+.25*min(1,z/.24))
  verts.append((-x,-z,h));uv.append((x*2,z*4))
for j in range(nz):
 for i in range(nx):a=j*(nx+1)+i;faces.append((a,a+nx+1,a+nx+2,a+1))
# Close the exposed cut earth outside the concrete shell; leave the doorway/interior open.
for i in range(nx):
 x=-1+2*i/nx;x2=-1+2*(i+1)/nx
 if x<-.5 or x2>.5:
  a=len(verts);verts.extend([verts[i],verts[i+1],(verts[i+1][0],0,0),(verts[i][0],0,0)]);uv.extend([(x*2,1),(x2*2,1),(x2*2,0),(x*2,0)]);faces.append((a,a+1,a+2,a+3))
o=mesh('Earth-covered bunker crown',verts,faces,soil,uv)
for f in o.data.polygons:f.use_smooth=True
export('bunker-mound-v3')

json.dump(manifest,open(OUT/'manifest.json','w'),indent=2)

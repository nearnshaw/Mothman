"""Refine the existing hound skin in Blender; outputs a review GLB and still to /tmp/mothman-detail."""
import bpy, math,json
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=Path('/tmp/mothman-detail');O.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Read the tracked source so repeat runs do not compound the deformation.
import subprocess
source=O/'source/Models';source.mkdir(parents=True,exist_ok=True)
images=O/'source/Images'
if not images.exists():images.symlink_to(R/'assets/Images',target_is_directory=True)
(source/'dog.glb').write_bytes(subprocess.check_output(['git','show','HEAD:assets/Models/dead-dog-v3.glb'],cwd=R))
bpy.ops.import_scene.gltf(filepath=str(source/'dog.glb'))
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.select_set(False)
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
# Connected islands distinguish the skin from the pendant ears and toes.
adj=[[] for _ in body.data.vertices]
for e in body.data.edges:
 a,b=e.vertices;adj[a].append(b);adj[b].append(a)
seen=set();islands=[]
for i in range(len(adj)):
 if i in seen:continue
 stack=[i];seen.add(i);group=[]
 while stack:
  v=stack.pop();group.append(v)
  for n in adj[v]:
   if n not in seen:seen.add(n);stack.append(n)
 islands.append(group)
skin=max(islands,key=len);coords=np.array([body.data.vertices[i].co[:] for i in skin if body.data.vertices[i].co.y>-.135])
# Measure the original continuous skin, then replace its bulbous head cross sections
# with a long nasal bridge, restrained brow, flat jaw and narrower cheek planes.
xs=np.linspace(-1.17,-.62,65);bounds=[]
for x in xs:
 pts=coords[np.abs(coords[:,0]-x)<.019]
 if len(pts):bounds.append([pts[:,1].min(),pts[:,1].max(),pts[:,2].min(),pts[:,2].max()])
 else:bounds.append(bounds[-1] if bounds else [-.05,.05,.06,.14])
bounds=np.array(bounds)
knots=np.array([-1.17,-1.12,-1.04,-.96,-.90,-.85,-.79,-.72,-.65,-.62])
width=np.array([.036,.047,.051,.059,.067,.079,.086,.093,.103,.113])
top=np.array([.126,.143,.153,.168,.197,.225,.239,.248,.273,.288])
bottom=np.array([.078,.060,.051,.047,.043,.041,.044,.058,.069,.070])
def shape(co):
 x,y,z=co
 if x>=-.64 or y<-.14:return co
 old=[np.interp(x,xs,bounds[:,k]) for k in range(4)]
 t=max(0,min(1,(-.64-x)/.055));t=t*t*(3-2*t);t*=max(0,min(1,(y+.14)/.025))
 cy=(old[0]+old[1])/2;ry=max(.015,(old[1]-old[0])/2)
 yn=(y-cy)/ry;zn=(z-old[2])/max(.02,old[3]-old[2])
 # Superellipse keeps the cheek/jaw from reading as a ball.
 yy=-.021+np.interp(x,knots,width)*math.copysign(abs(yn)**.82,yn)
 zz=np.interp(x,knots,bottom)+zn*(np.interp(x,knots,top)-np.interp(x,knots,bottom))
 return (x,y*(1-t)+yy*t,z*(1-t)+zz*t)
for i in skin:body.data.vertices[i].co=shape(body.data.vertices[i].co)
# Eye and lip creases follow the same surface transformation. Keep nose anatomy compact.
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o!=body:
  for v in o.data.vertices:
   if v.co.x<-.65:v.co=shape(v.co)
# Let the ear lie closer to the skull rather than stand out like a toy flap.
for island in islands:
 if len(island)>100 and island!=skin:
  center=sum((body.data.vertices[i].co for i in island),Vector())/len(island)
  if center.x<-.55 and center.y>-.3 and center.z>.08:
   for i in island:
    v=body.data.vertices[i];v.co.z=max(.035,v.co.z-.018);v.co.x-=.025
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
tri=sum(len(o.data.polygons) for o in meshes);lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
print('AUDIT',tri,lo,hi,flush=True)
bpy.ops.export_scene.gltf(filepath=str(O/'dead-dog-refined.glb'),export_format='GLB',export_yup=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False)
def render(path):
 bpy.ops.object.camera_add(location=(-1.9,-2.6,1.9));c=bpy.context.object;c.rotation_euler=(Vector((-.15,-.16,.13))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=2.6;bpy.context.scene.camera=c
 for p in [(0,-3,4),(-3,1,2)]:
  bpy.ops.object.light_add(type='AREA',location=p);l=bpy.context.object;l.data.energy=180;l.data.shape='DISK';l.data.size=3;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.world.color=(.14,.14,.14);s.render.resolution_x=1000;s.render.resolution_y=700;s.render.resolution_percentage=100;s.render.filepath=path;bpy.ops.render.render(write_still=True)
render(str(O/'after.png'))

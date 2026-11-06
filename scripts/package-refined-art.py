"""Externalize maps from the versioned Blender exports and preserve shared texture files."""
from pathlib import Path
import json,struct,hashlib
R=Path.cwd();D=R/'assets/Images/woodland-v3'
for f in Path('/tmp/mothman-v3').glob('*-v3.glb'):
 b=f.read_bytes();ln=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+ln]);binary=b[28+ln:];views=j.get('bufferViews',[]);skip=set()
 for im in j.get('images',[]):
  if 'bufferView' not in im:continue
  idx=im.pop('bufferView');skip.add(idx);v=views[idx];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];name=hashlib.sha256(data).hexdigest()[:16]+'.png';(D/name).write_bytes(data);im['uri']='../Images/woodland-v3/'+name;im.pop('mimeType',None)
 for mesh in j.get('meshes',[]):
  for primitive in mesh['primitives']:
   attrs=primitive['attributes']
   if f.name=='forest-tracks-v3.glb' and 'COLOR_1' in attrs:attrs['COLOR_0']=attrs.pop('COLOR_1')
 for m in j.get('materials',[]):
  if 'Continuous gravel' in m.get('name',''):m['alphaMode']='BLEND';m['doubleSided']=False
  if m.get('name')=='Woodland palette':
   ii=len(j['images']);j['images'].append({'uri':'../Images/woodland-v2/woodland-orm.png'});ti=len(j['textures']);j['textures'].append({'source':ii});m['pbrMetallicRoughness'].update(metallicRoughnessTexture={'index':ti},metallicFactor=1,roughnessFactor=1)
 remap={};nv=[];nb=bytearray()
 for i,v in enumerate(views):
  if i in skip:continue
  nb+=b'\0'*((-len(nb))%4);off=v.get('byteOffset',0);data=binary[off:off+v['byteLength']];v['byteOffset']=len(nb);nb.extend(data);remap[i]=len(nv);nv.append(v)
 for a in j.get('accessors',[]):
  if 'bufferView'in a:a['bufferView']=remap[a['bufferView']]
 j['bufferViews']=nv;j['buffers']=[{'byteLength':len(nb)}];js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);nb+=b'\0'*((-len(nb))%4)
 (R/'assets/Models'/f.name).write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(nb))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(nb),0x004e4942)+nb)
 print(f.name)

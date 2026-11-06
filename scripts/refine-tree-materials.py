"""Preserve catalog tree silhouettes and leaf materials; improve bark maps and trunk normals."""
import json,struct,math
import numpy as np
from pathlib import Path
R=Path.cwd();dest=R/'assets/Models';mapping={}
for folder,label in [('green_birch_tree','green-birch'),('autumn_birch_tree','autumn-birch'),('stylized_pine_tree','pine')]:
 p=next((R/'assets/asset-packs'/folder).rglob('*.glb'));b=p.read_bytes();ln=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+ln]);binary=bytearray(b[28+ln:]);bark=[]
 for im in j.get('images',[]):
  if 'uri'in im:im['uri']=str((p.parent/im['uri']).relative_to(R/'assets'));im['uri']='../'+im['uri']
 kind='pine' if label=='pine' else 'birch'
 for i,m in enumerate(j.get('materials',[])):
  if 'Bark' not in m.get('name',''):continue
  bark.append(i)
  for key,filename in [('base',kind+'-bark.png'),('normal',kind+'-normal.png')]:
   ii=len(j['images']);j['images'].append({'uri':'../Images/woodland-v3/'+filename});ti=len(j['textures']);j['textures'].append({'source':ii,'sampler':0})
   if key=='base':m['pbrMetallicRoughness']['baseColorTexture']={'index':ti}
   else:m['normalTexture']={'index':ti,'scale':.8}
  m['pbrMetallicRoughness']['roughnessFactor']=.94
 # Smooth only trunk primitives across UV seams: leaf planes retain original normals.
 def arr(idx):
  a=j['accessors'][idx];v=j['bufferViews'][a['bufferView']];dim={'VEC3':3,'SCALAR':1}[a['type']];dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];return np.ndarray((a['count'],dim),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dtype).itemsize*dim),np.dtype(dtype).itemsize))
 for mesh in j['meshes']:
  for pr in mesh['primitives']:
   if pr.get('material') not in bark or 'NORMAL' not in pr['attributes']:continue
   pos=arr(pr['attributes']['POSITION']);norm=arr(pr['attributes']['NORMAL']);groups={}
   for k,v in enumerate(pos):groups.setdefault(tuple(np.round(v,5)),[]).append(k)
   for ids in groups.values():
    n=norm[ids].sum(axis=0);le=np.linalg.norm(n)
    if le>1e-5:norm[ids]=n/le
 js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary+=b'\0'*((-len(binary))%4);out=dest/(label+'-v3.glb');out.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary);mapping[str(p.relative_to(R))]=str(out.relative_to(R))
json.dump(mapping,open('/tmp/mothman-v3/tree-map.json','w'),indent=2);print(mapping)

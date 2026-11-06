# Environment art source. Generates into /tmp/mothman-art; does not modify the composite.
# See design/environment-art.md for build and live-placement instructions.
import json,struct,hashlib,pathlib,shutil
root=pathlib.Path.cwd(); out=root/'assets/Images/woodland-v2';out.mkdir(exist_ok=True)
for f in pathlib.Path('/tmp/mothman-art').glob('*.glb'):
 b=f.read_bytes();jl=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+jl]);binary=b[28+jl:];views=j.get('bufferViews',[]);imageviews=set()
 for im in j.get('images',[]):
  idx=im.pop('bufferView');imageviews.add(idx);v=views[idx];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];name=hashlib.sha256(data).hexdigest()[:16]+'.png';(out/name).write_bytes(data);im['uri']='../Images/woodland-v2/'+name;im.pop('mimeType',None)
 for material in j.get('materials',[]):
  if material.get('name')=='Woodland palette':
   imgidx=len(j.setdefault('images',[]));j['images'].append({'uri':'../Images/woodland-v2/woodland-orm.png'})
   tidx=len(j.setdefault('textures',[]));j['textures'].append({'source':imgidx})
   pbr=material['pbrMetallicRoughness'];pbr['metallicRoughnessTexture']={'index':tidx};pbr['metallicFactor']=1;pbr['roughnessFactor']=1
 remap={};newviews=[];newbin=bytearray()
 for i,v in enumerate(views):
  if i in imageviews:continue
  while len(newbin)%4:newbin.append(0)
  off=v.get('byteOffset',0);data=binary[off:off+v['byteLength']];v['byteOffset']=len(newbin);newbin.extend(data);remap[i]=len(newviews);newviews.append(v)
 for a in j.get('accessors',[]):
  if 'bufferView' in a:a['bufferView']=remap[a['bufferView']]
 j['bufferViews']=newviews;j['buffers']=[{'byteLength':len(newbin)}];js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);newbin+=b'\0'*((-len(newbin))%4)
 glb=struct.pack('<III',0x46546c67,2,28+len(js)+len(newbin))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(newbin),0x004e4942)+newbin
 (root/'assets/Models'/f.name).write_bytes(glb)
print('Packaged 9 models with shared external textures')

shutil.copyfile('/tmp/mothman-art/woodland-orm.png',out/'woodland-orm.png')
shutil.copyfile('/tmp/mothman-art/bunker-steel.png',out/'bunker-steel.png')

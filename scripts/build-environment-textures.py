# Environment art source. Generates into /tmp/mothman-art; does not modify the composite.
# See design/environment-art.md for build and live-placement instructions.
from PIL import Image,ImageDraw,ImageFilter
import numpy as np, random, math
from pathlib import Path
out=Path('/tmp/mothman-art'); out.mkdir(parents=True,exist_ok=True); rng=random.Random(1966); n=1024
r=np.random.default_rng(1966)
def noise():
 a=np.zeros((n,n))
 for sz,weight in [(8,.34),(32,.23),(128,.15),(1024,.28)]:
  im=Image.fromarray((r.random((sz,sz))*255).astype('uint8')).resize((n,n),Image.Resampling.BILINEAR)
  a+=np.asarray(im)/255*weight
 return a
soil=noise(); base=np.array([78,69,48]); a=np.clip(base[None,None,:]*(.55+soil[:,:,None]),0,255).astype('uint8'); im=Image.fromarray(a); d=ImageDraw.Draw(im)
for i in range(8200):
 x,y=rng.randrange(n),rng.randrange(n); l=rng.uniform(2,16); ang=rng.random()*6.28
 c=rng.choice([(100,80,47),(67,58,35),(128,105,64),(48,53,33),(88,87,53)])
 if i%4: d.line((x,y,x+math.cos(ang)*l,y+math.sin(ang)*l),fill=c,width=1)
 else:d.ellipse((x,y,x+rng.randint(2,7),y+rng.randint(2,5)),fill=c)
im.save(out/'forest-floor.png')
# longitudinal dirt road: ragged shoulders, two compacted ruts, occasional center growth
arr=np.array(im).astype(float); gravel=noise(); u=np.linspace(-1,1,n)[None,:]; v=np.linspace(0,6.28,n)[:,None]
edge=.83+.045*np.sin(v*3)+.025*np.sin(v*7); blend=np.clip((edge-abs(u))/.18,0,1)
ruts=np.exp(-((abs(u)-.43)/.17)**4); center=np.exp(-(u/.17)**2)*(.5+.5*np.sin(v*2)**2)
col=np.array([152,142,120])[None,None,:]*(.64+gravel[:,:,None]*.65)
col*=1-ruts[:,:,None]*.16
col=col*(1-center[:,:,None]*.36)+np.array([66,70,42])*center[:,:,None]*.36
arr=arr*(1-blend[:,:,None])+col*blend[:,:,None]; road=Image.fromarray(np.clip(arr,0,255).astype('uint8')); d=ImageDraw.Draw(road)
for i in range(10000):
 x,y=rng.randrange(100,924),rng.randrange(n); rad=rng.choice([1,1,2,3]); val=rng.randint(100,175)
 d.ellipse((x,y,x+rad*2,y+rad),fill=(val,int(val*.93),int(val*.8)))
road.save(out/'old-gravel-track.png')
# weathered concrete, fine aggregate and horizontal formwork; streaks and damp base
f=noise(); a=np.array([135,139,130])[None,None,:]*(.65+f[:,:,None]*.6)
for x in range(n):
 streak=(math.sin(x*.051)+math.sin(x*.127)+math.sin(x*.013))* .045
 a[:,x,:]*=1-streak*np.linspace(0,1,n)[:,None]
a*=1-(np.linspace(0,1,n)[:,None,None]**7)*.32
im=Image.fromarray(np.clip(a,0,255).astype('uint8'));d=ImageDraw.Draw(im)
for y in range(0,n,171):
 d.line((0,y,n,y),fill=(65,68,62),width=2);d.line((0,y+3,n,y+3),fill=(148,147,132),width=1)
for x,y in [(160,180),(710,340),(530,710),(850,850)]:
 pts=[(x,y)]
 for i in range(12):x+=rng.randint(-16,20);y+=rng.randint(4,20);pts.append((x,y))
 d.line(pts,fill=(59,62,54),width=2)
im.save(out/'bunker-concrete.png')
# rust mottling
f=noise(); a=np.array([86,55,35])[None,None,:]*(.65+f[:,:,None]);Image.fromarray(a.astype('uint8')).save(out/'bunker-steel.png')
print('four 1024px textures generated')

# glTF packed occlusion/roughness/metalness: leather and fur matte, brass and steel reflective.
orm=Image.new('RGB',(64,64));d=ImageDraw.Draw(orm)
for i in range(16):
 rough,metal=(100,205) if i==15 else ((135,180) if i==11 else (230,0))
 x,y=(i%4)*16,(3-i//4)*16
 d.rectangle((x,y,x+15,y+15),fill=(255,rough,metal))
orm.save(out/'woodland-orm.png')

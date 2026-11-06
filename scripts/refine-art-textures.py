"""Deterministic PBR maps for the second woodland art pass."""
from PIL import Image,ImageDraw,ImageFilter
import numpy as np, random
from pathlib import Path
O=Path('assets/Images/woodland-v3');O.mkdir(exist_ok=True);N=1024;r=np.random.default_rng(137);rng=random.Random(137)
def noise(s):return np.asarray(Image.fromarray((r.random((s,s))*255).astype('uint8')).resize((N,N),Image.Resampling.BICUBIC),dtype=float)/255
def save(a,name):Image.fromarray(np.uint8(np.clip(a,0,255))).save(O/name)
def normal(h,name,strength=3):
 dy,dx=np.gradient(h);a=np.stack([-dx*strength,dy*strength,np.ones_like(h)],axis=2);a/=np.linalg.norm(a,axis=2)[:,:,None];save((a*.5+.5)*255,name)
y,x=np.mgrid[0:N,0:N]/N;fine=noise(1024);cloud=noise(12);grain=noise(128)
# Old window glass, subtly: a pale cool tint like the first version (alpha 0.28) with a faint cloud, streaks and dirt
# in the corners that only read when the flashlight hits the pane. The owner found the first murky pass (alpha up to
# 0.9, strong normal map) far too much, so this stays near-clear: alpha 0.30..0.50, a gentle ripple.
streak=(np.sin(x*183+noise(16)*7)*.5+.5)*(noise(64)*.5+.5)
edge=np.exp(-np.minimum.reduce([x,1-x,y,1-y])*14)
dirt=np.clip(.25+.32*cloud+.20*streak+.45*edge,0,1)
tint=np.array([150,170,182])*(1-dirt[:,:,None])+np.array([122,120,104])*dirt[:,:,None]
a=np.empty((N,N,4));a[:,:,:3]=tint*(.9+.1*cloud[:,:,None]);a[:,:,3]=(0.30+.20*dirt)*255
save(a,'window-grime.png');normal(cloud*.8+grain*.18+streak*.10,'window-normal.png',6)
# Tree bark intentionally remains the original catalog artwork (owner preference).
# Close-up fur fibers, with a dark saddle fading into ochre flank and muzzle.
saddle=np.exp(-((y-.75)/.20)**4)*np.clip((x-.18)*4,0,1)*np.clip((.88-x)*5,0,1)
base=np.array([126,96,62])*(1-saddle[:,:,None]) + np.array([43,39,32])*saddle[:,:,None]
fur=.74+.35*cloud+.19*grain+.12*fine
im=Image.fromarray(np.uint8(np.clip(base*fur[:,:,None],0,255)));d=ImageDraw.Draw(im)
for i in range(65000):
 xx,yy=rng.randrange(N),rng.randrange(N);c=im.getpixel((xx,yy));delta=rng.randrange(-20,21);cc=tuple(max(0,min(255,v+delta)) for v in c);d.line((xx,yy,xx+rng.randrange(3,11),yy+rng.randrange(-2,3)),fill=cc,width=1)
im.save(O/'hound-fur.png');normal(np.asarray(im.convert('L'),dtype=float)/255,'hound-normal.png',1.7)
# Seamless mottled aggregate; route shoulders and ruts are controlled by mesh colors.
h=.32*noise(16)+.25*noise(64)+.43*noise(1024);save((.65+h[:,:,None]*.6)*np.array([148,136,112]),'track-aggregate.png');normal(h,'track-normal.png',1.3)
# Concrete gets damp patches, pitting and a restrained normal rather than painted flat lines.
im=Image.open('/tmp/mothman-art/bunker-concrete.png').convert('RGB');a=np.asarray(im,dtype=float);damp=np.clip((cloud-.45)*2,0,.5);a*=1-damp[:,:,None]*.6;save(a,'concrete.png');normal(np.asarray(im.convert('L'),dtype=float)/255+fine*.1,'concrete-normal.png',2.7)
print('Wrote woodland-v3 PBR maps')

"""Add fine surface relief to the existing pale bark; preserve its color and PBR sheen.
Run with Python + Pillow + NumPy. Reads tracked originals to avoid cumulative passes.
All three existing tree variants use the approved pale pine bark artwork.
Only bark maps change; foliage, UVs, geometry and reflective settings stay intact.
"""
from pathlib import Path
from io import BytesIO
import subprocess
import numpy as np
from PIL import Image, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
N=1024
rng=np.random.default_rng(196611)
def original(path):
    return Image.open(BytesIO(subprocess.check_output(['git','show','HEAD:'+str(path.relative_to(ROOT))],cwd=ROOT))).convert('RGB')
def noise(w,h):
    a=Image.fromarray(np.uint8(rng.random((h,w))*255))
    return np.asarray(a.resize((N,N),Image.Resampling.BICUBIC),dtype=float)/255-.5
y,x=np.mgrid[:N,:N]/N
cloud=noise(24,24);grain=noise(180,32);pores=noise(N,N)
# Subtle layered fibres, shallow irregular fissures, and pinprick weathering.
fibres=np.sin(x*950+cloud*8+y*35)*.5+.5
fissures=np.maximum(0,(np.sin(x*390+noise(32,48)*9)-.91)/.09)**2
fissures*=np.clip(noise(48,100)*3+.15,0,1)
pits=np.maximum(0,(pores-.35)/.15)**3
height=.22*grain+.045*pores-.12*fissures-.065*pits+.035*fibres
shade=1+grain*.055+cloud*.035-pores*.012-fissures*.085-pits*.055
for folder in ['stylized_pine_tree','green_birch_tree','autumn_birch_tree']:
    directory=ROOT/'assets/asset-packs'/folder/folder
    base=directory/('stylizedBarkWhite01_basecolor-min.png' if folder=='stylized_pine_tree' else 'bark01_basecolor.png')
    norm=directory/('stylizedBarkWhite01_normal-min.png' if folder=='stylized_pine_tree' else 'stylizedBarkWhite01_normal.png')
    # Use the approved bark for every variant; the old birch artwork has blurry bars.
    approved=ROOT/'assets/asset-packs/stylized_pine_tree/stylized_pine_tree'
    a=np.asarray(original(approved/'stylizedBarkWhite01_basecolor-min.png').resize((N,N),Image.Resampling.LANCZOS),dtype=float)
    # Keep the bright silver surface and existing dark peeled patches.
    out=np.clip(a*shade[:,:,None],0,255).astype('uint8');Image.fromarray(out).save(base)
    n=np.asarray(original(approved/'stylizedBarkWhite01_normal-min.png').resize((N,N),Image.Resampling.BILINEAR),dtype=float)/127.5-1
    dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.5
    dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.5
    n[:,:,0]-=dx*2.7;n[:,:,1]+=dy*2.7
    n/=np.maximum(np.linalg.norm(n,axis=2,keepdims=True),.001)
    Image.fromarray(np.uint8(np.clip((n*.5+.5)*255,0,255))).save(norm)
    print(base.relative_to(ROOT), 'mean luminance',round(a.mean(),1),'->',round(out.mean(),1))

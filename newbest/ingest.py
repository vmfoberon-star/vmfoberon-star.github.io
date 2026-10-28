# usage: ingest.py slug  -> converts staged files under /mnt/user-data/uploads/Photos to cand/slug, deletes originals
import sys,os,glob
from PIL import Image,ImageOps
slug=sys.argv[1]; out=f'/home/claude/travel/newbest/cand/{slug}'; os.makedirs(out,exist_ok=True)
n=0
for p in glob.glob('/mnt/user-data/uploads/Photos/'+(sys.argv[2] if len(sys.argv)>2 else '')+'**/*',recursive=True):
    if not os.path.isfile(p) or not p.lower().endswith(('.jpg','.jpeg')): continue
    rel=os.path.relpath(p,'/mnt/user-data/uploads/Photos').replace('/','__')
    try:
        im=ImageOps.exif_transpose(Image.open(p)).convert('RGB'); im.thumbnail((1920,1920),Image.LANCZOS)
        im.save(f'{out}/{rel}',quality=85); n+=1
    except Exception as e: print('ERR',p,e)
    os.remove(p)
print(slug,n,'->',len(os.listdir(out)))

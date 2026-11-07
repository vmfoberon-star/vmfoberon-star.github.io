"""proc.py sheet <slug> <srcdir...>   -> makes small previews + numbered contact sheet, list.txt
   proc.py pick <slug> 3,5,9 ...       -> writes 1600px webp + 600px thumbs to travel/israel/photos/<slug>/
   proc.py clean <srcdir>              -> deletes staged originals"""
import sys,os,glob,shutil
from PIL import Image,ImageOps,ImageDraw,ImageFont
import os as _o;W=_o.path.expanduser('~/ilwork');OUT=_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'..','israel','photos')
def imgs(dirs):
    r=[]
    for d in dirs:
        for f in sorted(os.listdir(d)):
            if f.lower().endswith(('.jpg','.jpeg','.png','.webp','.heic')): r.append(os.path.join(d,f))
    return r
cmd=sys.argv[1]
if cmd=='sheet':
    slug=sys.argv[2];files=imgs(sys.argv[3:]);os.makedirs(f'{W}/{slug}',exist_ok=True)
    lst=open(f'{W}/{slug}/list.txt','a+');lst.seek(0);old=[l.strip() for l in lst];start=len(old)
    new=[f for f in files if f not in old]
    for f in new: lst.write(f+'\n')
    lst.close();allf=old+new
    th=[]
    for i,f in enumerate(allf):
        tp=f'{W}/{slug}/p{i:03d}.jpg'
        if not os.path.exists(tp):
            im=ImageOps.exif_transpose(Image.open(f));im.draft('RGB',(800,800));im=im.convert('RGB');im.thumbnail((360,360));im.save(tp,quality=80)
        th.append(tp)
    cols=6;cw,ch=300,220;rows=(len(th)+cols-1)//cols
    per=36
    for s in range(0,len(th),per):
        part=th[s:s+per];rows=(len(part)+cols-1)//cols
        sh=Image.new('RGB',(cols*cw,rows*ch),(20,20,20));d=ImageDraw.Draw(sh)
        try:fn=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
        except:fn=None
        for j,tp in enumerate(part):
            im=Image.open(tp);im.thumbnail((cw-8,ch-8));x=(j%cols)*cw+4;y=(j//cols)*ch+4;sh.paste(im,(x,y));d.rectangle([x,y,x+46,y+28],fill=(0,0,0));d.text((x+4,y+2),str(s+j),fill=(255,220,120),font=fn)
        sh.save(f'{W}/{slug}/sheet{s//per}.jpg',quality=82);print(f'{W}/{slug}/sheet{s//per}.jpg')
    print(len(th),'images')
elif cmd=='pick':
    slug=sys.argv[2];allf=[l.strip() for l in open(f'{W}/{slug}/list.txt')]
    os.makedirs(f'{OUT}/{slug}',exist_ok=True);n=len([f for f in os.listdir(f'{OUT}/{slug}') if not f.startswith('t_')])
    for k in ','.join(sys.argv[3:]).split(','):
        f=allf[int(k)];im=ImageOps.exif_transpose(Image.open(f)).convert('RGB')
        big=im.copy();big.thumbnail((1600,1600),Image.LANCZOS);big.save(f'{OUT}/{slug}/{n:02d}.webp',quality=80,method=5)
        t=im.copy();t.thumbnail((640,640),Image.LANCZOS);t.save(f'{OUT}/{slug}/t_{n:02d}.webp',quality=74,method=5)
        print(n,os.path.basename(f));n+=1
elif cmd=='clean':
    for d in sys.argv[2:]: shutil.rmtree(d,ignore_errors=True)
if cmd=='all':
    slug=sys.argv[2];src=sys.argv[3];os.makedirs(f'{OUT}/{slug}',exist_ok=True)
    n=len([f for f in os.listdir(f'{OUT}/{slug}') if not f.startswith('t_')])
    for f in sorted(os.listdir(src)):
        if 'sheet' in f: continue
        im=ImageOps.exif_transpose(Image.open(os.path.join(src,f))).convert('RGB')
        big=im.copy();big.thumbnail((1600,1600),Image.LANCZOS);big.save(f'{OUT}/{slug}/{n:02d}.webp',quality=80,method=5)
        t=im.copy();t.thumbnail((640,640),Image.LANCZOS);t.save(f'{OUT}/{slug}/t_{n:02d}.webp',quality=74,method=5);n+=1
    print(slug,n)

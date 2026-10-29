import sys,glob,os
from PIL import Image,ImageDraw
d=sys.argv[1];out=sys.argv[2];cols=int(sys.argv[3]) if len(sys.argv)>3 else 8
fs=sorted(glob.glob(d+'/*.*'));W=240;H=180
s=Image.new('RGB',(cols*W,((len(fs)+cols-1)//cols)*(H+16)),'white');dr=ImageDraw.Draw(s)
for k,f in enumerate(fs):
    im=Image.open(f);im.thumbnail((W-4,H-4));x=(k%cols)*W;y=(k//cols)*(H+16)
    s.paste(im,(x+(W-im.width)//2,y));dr.text((x+3,y+H),os.path.basename(f).split('.')[0],fill='black')
s.save(out,quality=82);print(out,s.size)

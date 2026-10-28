import sys,os
from PIL import Image,ImageDraw
slug=sys.argv[1]; d=f'/home/claude/travel/newbest/cand/{slug}'; fs=sorted(os.listdir(d))
W=6; tw,th=320,213; rows=(len(fs)+W-1)//W
S=Image.new('RGB',(W*tw,rows*(th+18)),'white'); dr=ImageDraw.Draw(S)
for i,f in enumerate(fs):
    im=Image.open(f'{d}/{f}'); im.thumbnail((tw,th)); x,y=(i%W)*tw,(i//W)*(th+18)
    S.paste(im,(x+(tw-im.width)//2,y+(th-im.height)//2)); dr.text((x+4,y+th+3),f'{i}: {f.split("__")[-2][:22]}/{f.split("__")[-1][:12]}',fill='black')
p=f'/tmp/claude-0/-home-claude/54e62534-4242-565a-a911-0fd054055a9e/scratchpad/sheet_{slug}.jpg'; S.save(p,quality=80); print(p)
for i,f in enumerate(fs): print(i,f)

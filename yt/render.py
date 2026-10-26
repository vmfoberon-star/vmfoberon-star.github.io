# Render YouTube slideshow videos (one per chapter) from the site's photo bundles + music loops.
# usage: python3 yt/render.py <slug> [chapter_index ...]
import json, sys, os, base64, subprocess, glob, re
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT='/home/claude/travel'; OUT=f'{ROOT}/yt/out'; os.makedirs(OUT,exist_ok=True)
W,H,FPS=1280,720,25
SLIDE=5.0; XF=1.0; INTRO=4.5; OUTRO=4.5
F=lambda n,s: ImageFont.truetype(f'{ROOT}/yt/fonts/{n}.ttf',s)
GOLD=(232,176,74)

h=open(f'{ROOT}/travel.html').read(); i=h.index('const TRIPS=')+12
TRIPS={t['slug']:t for t in json.JSONDecoder().raw_decode(h[i:])[0]}
BUNDLES=json.loads(re.search(r'const BUNDLES=(\{.*?\}), PHOTOS',h).group(1))

def groups(t):
    if t.get('chapters'):
        out=[];k=0
        for c in t['chapters']: out.append((c['name'],c.get('date',''),t['slides'][k:k+c['n']])); k+=c['n']
        return out
    if t['slug']=='italy03':
        return [('Рим','август 2003',[s for s in t['slides'] if s[1].startswith('Рим')]),('Флоренция','август 2003',[s for s in t['slides'] if not s[1].startswith('Рим')])]
    return [(t['title'],t['place'].split('·')[-1].strip(),t['slides'])]

def load_photos(slug):
    P={}
    for f in BUNDLES[slug]: P.update(json.load(open(f'{ROOT}/site/{f}')))
    return P
def dec(du):
    b=np.frombuffer(base64.b64decode(du.split(',',1)[1]),np.uint8); im=cv2.imdecode(b,cv2.IMREAD_COLOR)
    if im is None: im=cv2.cvtColor(np.array(Image.open(__import__('io').BytesIO(base64.b64decode(du.split(',',1)[1]))).convert('RGB')),cv2.COLOR_RGB2BGR)
    return im

Z=1.12; CW,CH=int(W*Z),int(H*Z)
def canvas(im):
    h0,w0=im.shape[:2]; ar=w0/h0
    if ar>=1.3:   # landscape: cover
        s=max(CW/w0,CH/h0); r=cv2.resize(im,(int(w0*s+1),int(h0*s+1)),interpolation=cv2.INTER_CUBIC)
        y=(r.shape[0]-CH)//2; x=(r.shape[1]-CW)//2; return r[y:y+CH,x:x+CW]
    s=max(CW/w0,CH/h0); bg=cv2.resize(im,(int(w0*s+1),int(h0*s+1)))
    y=(bg.shape[0]-CH)//2; x=(bg.shape[1]-CW)//2; bg=bg[y:y+CH,x:x+CW]
    bg=cv2.GaussianBlur(bg,(0,0),28); bg=(bg*0.45).astype(np.uint8)
    s=CH*0.96/h0; fg=cv2.resize(im,(int(w0*s),int(h0*s)),interpolation=cv2.INTER_CUBIC)
    y=(CH-fg.shape[0])//2; x=(CW-fg.shape[1])//2; bg[y:y+fg.shape[0],x:x+fg.shape[1]]=fg; return bg

def kb(cv,p,mode):
    # p in 0..1 ; zoom in or out with a gentle pan
    z0,z1=(1.0,1/Z*1.0) if False else (1.0,1.0)
    s=(1/Z)+(1-1/Z)*(p if mode%2 else 1-p)   # fraction of canvas visible: 1/Z..1
    s=1/Z+ (1-1/Z)*0.0 + (s-1/Z)
    vw,vh=CW*s,CH*s
    dx=[(0.5,0.5),(0.3,0.6),(0.7,0.4),(0.5,0.3)][mode%4]
    cx=(CW-vw)*dx[0]+vw/2; cy=(CH-vh)*dx[1]+vh/2
    sc=W/vw; M=np.float32([[sc,0,W/2-cx*sc],[0,sc,H/2-cy*sc]])
    return cv2.warpAffine(cv,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)

def text_layer(draw_fn):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); draw_fn(im); a=np.array(im).astype(np.float32)/255
    return a[...,:3][...,::-1].copy(), a[...,3:4].copy()
def shadowed(im,xy,txt,font,fill,anchor='ls',blur=6):
    sh=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(sh); d.text((xy[0]+2,xy[1]+3),txt,font=font,fill=(0,0,0,200),anchor=anchor)
    sh=sh.filter(ImageFilter.GaussianBlur(blur)); im.alpha_composite(sh); ImageDraw.Draw(im).text(xy,txt,font=font,fill=fill,anchor=anchor)
def wrap(txt,font,maxw):
    words=txt.split(); lines=['']
    for w_ in words:
        t=(lines[-1]+' '+w_).strip()
        if font.getlength(t)<=maxw: lines[-1]=t
        else: lines.append(w_)
    return lines
def caption_layer(cap,sub):
    def f(im):
        g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
        for y in range(H-230,H): gd.line([(0,y),(W,y)],fill=(0,0,0,int(150*((y-(H-230))/230)**1.6)))
        im.alpha_composite(g)
        fn=F('cormorant-garamond-500-italic',50); lines=wrap(cap,fn,W-160)
        y=H-48-(len(lines)-1)*52
        if sub: shadowed(im,(60,y-58),sub.upper(),F('golos-text-500-normal',19),GOLD+(255,))
        for k,l in enumerate(lines): shadowed(im,(60,y+k*52),l,fn,(255,255,255,255))
    return text_layer(f)
def card_layer(lines):
    def f(im):
        g=Image.new('RGBA',(W,H),(0,0,0,150)); im.alpha_composite(g)
        y=H//2-sum(l[2] for l in lines)//2
        for txt,font,dy,fill in [(a,b,c,d) for a,b,c,d in lines]:
            y+=dy; shadowed(im,(W//2,y),txt,font,fill,anchor='ms',blur=8)
    return text_layer(f)

def render(slug,ci,G,P,total):
    name,date,slides=G[ci]; t=TRIPS[slug]
    fn=f'{OUT}/{slug}_{ci+1:02d}.mp4'
    n=len(slides); dur=INTRO+n*(SLIDE-XF)+XF+OUTRO
    cvs=[canvas(dec(P[s[0]])) for s in slides]
    caps=[caption_layer(s[2],'') for s in slides]
    multi=len(G)>1
    title=t['title']; year=t.get('year','')
    if slug=='vienna13' and 'декабря' in date and '2' not in date.split()[-1][:1]: year='2012'
    if re.search(r'\d{4}',date): year=''
    intro=card_layer([('ОЛЬГА И ВЛАДИМИР ФРОНТОН',F('golos-text-500-normal',20),0,GOLD+(255,)),
                      (title,F('cormorant-garamond-500-italic',76),90,(255,255,255,255)),
                      ((f'Глава {ci+1} из {len(G)} · ' if multi else '')+(name if multi else t['place']),F('golos-text-400-normal',30),70,(235,235,235,255)),
                      ((date+(' '+year if year and year not in date else '')) if multi else '',F('golos-text-400-normal',24),46,(200,200,200,255))])
    nxt=G[ci+1][0] if ci+1<len(G) else None
    outro=card_layer([('Сами ездим, сами снимаем, сами монтируем',F('cormorant-garamond-500-italic',46),0,(255,255,255,255)),
                      ('ОЛЬГА И ВЛАДИМИР ФРОНТОН',F('golos-text-500-normal',22),70,GOLD+(255,)),
                      (('Дальше: '+nxt) if nxt else '',F('golos-text-400-normal',26),70,(220,220,220,255))])
    bgI=cv2.GaussianBlur(cvs[0],(0,0),30); bgI=cv2.resize(bgI,(W,H)); bgO=cv2.resize(cv2.GaussianBlur(cvs[-1],(0,0),30),(W,H))
    aud=f'{ROOT}/music/{t["music"]}_loop.wav'
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-stream_loop','-1','-i',aud,'-filter_complex',f'[1:a]atrim=0:{dur:.2f},afade=t=in:d=1.5,afade=t=out:st={dur-3.5:.2f}:d=3.5[a]',
         '-map','0:v','-map','[a]','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',f'{dur:.2f}',fn]
    pr=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    NF=int(dur*FPS); s0=INTRO
    def blend(base,layer,a):
        rgb,al=layer; al=al*a; return (base*(1-al)+rgb*255*al)
    def slide_frame(k,tt):  # tt seconds since slide start
        p=tt/SLIDE; fr=kb(cvs[k],min(max(p,0),1),k).astype(np.float32)
        ca=np.clip((tt-0.6)/0.6,0,1)*np.clip((SLIDE-0.4-tt)/0.5,0,1)
        if ca>0: fr=blend(fr,caps[k],ca)
        return fr
    for f in range(NF):
        tm=f/FPS
        if tm<INTRO:
            a=min(1,tm/0.8); fr=bgI.astype(np.float32)*min(1,tm/1.0); fr=blend(fr,intro,a*min(1,(INTRO-tm)/0.7))
            if tm>INTRO-XF: x=(tm-(INTRO-XF))/XF; fr=fr*(1-x)+slide_frame(0,tm-(INTRO-XF))*x
        elif tm< s0+n*(SLIDE-XF)+XF:
            r=tm-s0; k=min(int(r//(SLIDE-XF)),n-1); tt=r-k*(SLIDE-XF)
            fr=slide_frame(k,tt+XF if k==0 and False else tt)
            if k+1<n and tt>SLIDE-XF: x=(tt-(SLIDE-XF))/XF; fr=fr*(1-x)+slide_frame(k+1,tt-(SLIDE-XF))*x
        else:
            r=tm-(s0+n*(SLIDE-XF)+XF); fr=blend(bgO.astype(np.float32)*max(0,1-max(0,r-(OUTRO-1.2))/1.2),outro,min(1,r/0.8)*max(0,min(1,(OUTRO-r)/0.8)))
            if r<XF: fr=fr*(r/XF)+slide_frame(n-1,SLIDE-0.01)*(1-r/XF)
        pr.stdin.write(np.clip(fr,0,255).astype(np.uint8).tobytes())
    pr.stdin.close(); pr.wait(); return fn,dur

if __name__=='__main__':
    slug=sys.argv[1]; t=TRIPS[slug]; G=groups(t); P=load_photos(slug)
    idx=[int(x) for x in sys.argv[2:]] or range(len(G))
    for ci in idx:
        fn,dur=render(slug,ci,G,P,len(G)); print('done',fn,round(dur,1),flush=True)

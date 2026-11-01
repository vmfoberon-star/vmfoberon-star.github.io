"""Builds ../site/israel/ from data_il.py (+ gal/<id>.txt photo lists if present)."""
import os,json,sys,shutil,glob
D=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,D)
import importlib,data_il;importlib.reload(data_il)
OUT=os.path.join(D,'..','site','israel');os.makedirs(OUT,exist_ok=True)
trips=[]
for t in data_il.TRIPS:
    t=dict(t);g=[]
    pdir=os.path.join(D,'photos',t['id'])
    capf=os.path.join(D,'gal',t['id']+'.txt')
    if os.path.isdir(pdir):
        caps={}
        if os.path.exists(capf):
            for line in open(capf,encoding='utf8'):
                if '|' in line: k,c=line.rstrip('\n').split('|',1);caps[k]=c
        for f in sorted(os.listdir(pdir)):
            if f.endswith('.webp') and not f.startswith('t_'):
                k=f[:-5];g.append([f'photos/{t["id"]}/t_{f}',caps.get(k,''),f'photos/{t["id"]}/{f}'])
        if g and not t.get('cover'): t['cover']=g[t.get('ci',0)][2]
    t['g']=g; trips.append(t)
if os.path.isdir(os.path.join(D,'photos')):
    shutil.copytree(os.path.join(D,'photos'),os.path.join(OUT,'photos'),dirs_exist_ok=True)
hero=[t['cover'] for t in trips if t.get('cover') and t.get('hero')]
# best photos: data_il.BEST ('tripid/NN' list) if present, else each photo trip's cover frame
best=[]
byid={t['id']:t for t in trips}
picks=getattr(data_il,'BEST',None) or [f"{t['id']}/{t.get('ci',0):02d}" for t in sorted(trips,key=lambda t:t['s'],reverse=True) if t['g']]
for k in picks:
    tid,n=k.split('/');t=byid.get(tid)
    if not t: continue
    for g in t['g']:
        if g[2].endswith(f'/{n}.webp'): best.append([g[0],g[1],g[2],tid,t['t']+' · '+t['y']]);break
# slideshow music
mdir=os.path.join(D,'..','music');os.makedirs(os.path.join(OUT,'music'),exist_ok=True)
for src,dst in [('israel_loop.webm','israel_loop.webm'),('israel_loop.m4a','israel_loop.mp4')]:
    shutil.copy(os.path.join(mdir,src),os.path.join(OUT,'music',dst))
data=dict(regions=data_il.REGIONS,trips=trips,concerts=sorted(data_il.CONCERTS,key=lambda c:c[2],reverse=True),hero=hero,best=best)
html=open(os.path.join(D,'template_il.html'),encoding='utf8').read()
og='<meta property="og:image" content="https://vmfoberon-star.github.io/israel/'+hero[0]+'">' if hero else ''
html=html.replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__OG__',og)
open(os.path.join(OUT,'index.html'),'w',encoding='utf8').write(html)
print('israel:',len(trips),'trips,',sum(len(t['g']) for t in trips),'photos,',len(data_il.CONCERTS),'concerts,',len(best),'best')

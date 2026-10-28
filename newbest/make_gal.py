import os,glob,json
from PIL import Image,ImageOps
MUS={'denmark14':'benelux','norway17':'benelux','france18':'paris','barcelona':'spain','china19':'vienna','apulia21':'italia','azores22':'spain','portugal22':'spain','napoli23':'italia','spain23':'spain','rome25':'italia','prague25':'vienna','austria25':'vienna','toscana26':'italia','italy16':'italia'}
GAL={};EN={}
for f in sorted(glob.glob('newbest/gal/*.txt')):
    s=os.path.basename(f)[:-4]; d='portugal22' if s=='azores22' else s
    files=os.listdir(f'newbest/cand/{d}'); os.makedirs(f'photosgal/{s}',exist_ok=True); sl=[]
    for i,line in enumerate(l.strip() for l in open(f) if l.strip()):
        key,c,cap,ce,cape=line.split('|'); m=[x for x in files if x[:-4].endswith(key)]; assert len(m)==1,(s,key,m); m=m[0]
        pid=f'g{s[:3]}{s[-2:]}{i:02d}'; out=f'photosgal/{s}/{pid}.webp'
        if not os.path.exists(out):
            im=ImageOps.exif_transpose(Image.open(f'newbest/cand/{d}/{m}')).convert('RGB'); im.thumbnail((1280,1280)); im.save(out,'WEBP',quality=72,method=4)
        sl.append([pid,c,cap]); EN[c]=ce; EN[cap]=cape
    GAL[s]={'music':MUS[s],'slides':sl}
open('gallery.py','w').write('# Photo slideshows for trips 2014–2026 (photos in photosgal/<slug>/<id>.webp)\nGAL='+json.dumps(GAL,ensure_ascii=False,indent=0)+'\n')
t=open('en/tr_auto.py').read(); mark='\n# trip photo galleries (generated)\n'
if mark in t: t=t[:t.index(mark)]
EN.update({'Лизьё':'Lisieux','Ванн':'Vannes'})
open('en/tr_auto.py','w').write(t.rstrip('\n')+mark+''.join(f'D[{json.dumps(k,ensure_ascii=False)}]={json.dumps(v,ensure_ascii=False)}\n' for k,v in EN.items()))
print({k:len(v['slides']) for k,v in GAL.items()})

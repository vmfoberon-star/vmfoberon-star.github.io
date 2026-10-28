# pick2.py listing.json base regex N cand_slug [maxMB]  -> evenly spread new files per folder, excluding already staged
import json,sys,re,os
d=json.load(open(sys.argv[1])); base=sys.argv[2]; rx=re.compile(sys.argv[3]); N=int(sys.argv[4]); slug=sys.argv[5]; lim=float(sys.argv[6]) if len(sys.argv)>6 else 85
have=set(f.split('__')[-1] for f in os.listdir(f'cand/{slug}')) if os.path.isdir(f'cand/{slug}') else set()
fold={}
for e in d['entries']:
    n=e['name']
    if e['type']!='file' or not n.lower().endswith(('.jpg','.jpeg')) or 'WhatsApp' in n or 'IMG-' in n or '~' in n: continue
    k=n.rsplit('/',1)[0] if '/' in n else '.'
    if rx.search(k) and n.rsplit('/',1)[-1] not in have: fold.setdefault(k,[]).append(e)
tot=sum(len(v) for v in fold.values()); sel=[]
for k,fs in sorted(fold.items()):
    fs.sort(key=lambda e:e['name']); per=max(1,round(N*len(fs)/tot)); m=len(fs)
    sel+=[fs[i] for i in sorted(set(int((j+0.5)*m/per) for j in range(min(per,m))))]
chunks=[];cur=[];s=0
for e in sel:
    if cur and (s+e['size']/1e6>lim or len(cur)>=20): chunks.append(cur);cur=[];s=0
    cur.append(base+'\\'+e['name'].replace('/','\\')); s+=e['size']/1e6
if cur: chunks.append(cur)
print(len(sel),'files',len(chunks),'chunks',file=sys.stderr)
for c in chunks: print(json.dumps(c,ensure_ascii=False))

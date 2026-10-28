# pick.py listing.json base_device_path per_folder folder_regex [maxMB]
import json,sys,re
d=json.load(open(sys.argv[1])); base=sys.argv[2]; per=int(sys.argv[3]); rx=re.compile(sys.argv[4]); lim=float(sys.argv[5]) if len(sys.argv)>5 else 85
fold={}
for e in d['entries']:
    n=e['name']
    if e['type']!='file' or not n.lower().endswith(('.jpg','.jpeg')) or 'WhatsApp' in n or 'IMG-' in n: continue
    k=n.rsplit('/',1)[0] if '/' in n else '.'
    if rx.search(k): fold.setdefault(k,[]).append(e)
sel=[]
for k,fs in sorted(fold.items()):
    fs.sort(key=lambda e:e['name']); m=len(fs)
    idx=sorted(set(int((i+0.5)*m/per) for i in range(min(per,m))))
    sel+= [fs[i] for i in idx]
chunks=[];cur=[];s=0
for e in sel:
    if cur and s+e['size']/1e6>lim: chunks.append(cur);cur=[];s=0
    cur.append(base+'\\'+e['name'].replace('/','\\')); s+=e['size']/1e6
if cur: chunks.append(cur)
print(len(sel),'files',len(chunks),'chunks')
for c in chunks: print(json.dumps(c,ensure_ascii=False))

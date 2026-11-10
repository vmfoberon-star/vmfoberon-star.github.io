import sys,os,re
slug,idx=sys.argv[1],int(sys.argv[2]);d=f'israel/photos/{slug}'
n=len([f for f in os.listdir(d) if re.fullmatch(r'\d\d\.webp',f)])
for p in ('','t_'):
    os.remove(f'{d}/{p}{idx:02d}.webp')
    for i in range(idx+1,n): os.rename(f'{d}/{p}{i:02d}.webp',f'{d}/{p}{i-1:02d}.webp')
g=f'israel/gal/{slug}.txt';out=[]
for l in open(g).read().splitlines():
    k,c=l.split('|',1);k=int(k)
    if k==idx: continue
    out.append(f'{k-1 if k>idx else k:02d}|{c}')
open(g,'w').write('\n'.join(out)+'\n');print('removed',slug,idx,'now',n-1)

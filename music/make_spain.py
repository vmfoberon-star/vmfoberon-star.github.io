# Original Spanish-guitar piece in A minor (Andalusian cadence Am–G–F–E), plucked nylon guitars (Karplus–Strong) + soft cajón.
import numpy as np, wave
from scipy.signal import lfilter
SR=44100; BPM=104; BEAT=60/BPM; BAR=4*BEAT
rng=np.random.default_rng(7); np.random.seed(7)
def m2f(m): return 440*2**((m-69)/12)
N={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def note(s): acc=1 if '#' in s else (-1 if (len(s)>2 and s[1]=='b') else 0); return 12*(int(s[-1])+1)+N[s[0]]+acc
def pluck(freq,dur,vel,bright=0.5):
    n=int(SR*dur); p=int(SR/freq); buf=rng.uniform(-1,1,p)
    buf=lfilter([bright,1-bright],[1],buf)   # soften the excitation (nylon)
    y=np.zeros(n); b=buf.copy(); idx=0
    out=np.empty(n)
    # vectorised KS by periods
    k=0
    while k<n:
        m=min(p,n-k); out[k:k+m]=b[:m]
        nb=0.5*(b+np.roll(b,-1))*0.9965; b=nb; k+=m
    t=np.arange(n)/SR
    body=lfilter([1,-0.6],[1,-1.55,0.7],out)*0.25+out
    env=np.minimum(1,t/0.002)*np.minimum(1,np.maximum(0,dur-t)/0.08)
    y=body*env; return vel*y/(np.abs(y).max()+1e-9)
def cajon(kind,vel):
    n=int(SR*0.25); t=np.arange(n)/SR
    if kind=='b': y=np.sin(2*np.pi*80*t*np.exp(-t*6))*np.exp(-t*22)
    else: y=lfilter([1,-0.9],[1],rng.normal(0,1,n))*np.exp(-t*35)*0.5+np.sin(2*np.pi*220*t)*np.exp(-t*40)*0.3
    return vel*y/np.abs(y).max()
CH={'Am':['A2','E3','A3','C4','E4'],'G':['G2','D3','G3','B3','D4'],'F':['F2','C3','F3','A3','C4'],'E':['E2','B2','E3','G#3','B3'],
    'Dm':['D3','A3','D4','F4','A3'],'C':['C3','G3','C4','E4','G3'],'E7':['E2','B2','D3','G#3','B3']}
chords=['Am','G','F','E', 'Am','G','F','E', 'Dm','Am','E7','Am', 'F','G','F','E',
        'Am','G','F','E', 'Am','G','F','E', 'Dm','Am','F','E7', 'Dm','E','Am','E']
# melody: list per bar of (note, beats); None = rest
mel=[[('E5',1.5),('F5',0.5),('E5',1),('D5',1)],[('D5',1.5),('E5',0.5),('D5',1),('C5',1)],[('C5',1),('D5',0.5),('C5',0.5),('B4',1),('A4',1)],[('G#4',3),(None,1)],
     [('A4',0.5),('C5',0.5),('E5',1),('A5',1),('G5',1)],[('G5',0.5),('F5',0.5),('E5',1),('D5',2)],[('F5',1),('E5',0.5),('D5',0.5),('C5',1),('B4',1)],[('B4',2),('G#4',2)],
     [('F5',1.5),('E5',0.5),('D5',1),('A4',1)],[('E5',1.5),('D5',0.5),('C5',1),('A4',1)],[('B4',1),('D5',1),('G#4',1),('B4',1)],[('A4',3),(None,1)],
     [('A5',1),('G5',0.5),('F5',0.5),('E5',1),('C5',1)],[('D5',1),('E5',0.5),('F5',0.5),('G5',1),('B4',1)],[('C5',1),('A4',1),('F4',1),('A4',1)],[('G#4',2),('B4',1),('E5',1)],
     [('A5',1.5),('G5',0.5),('E5',1),('C5',1)],[('B4',1.5),('D5',0.5),('G5',2)],[('A5',1),('G5',0.5),('F5',0.5),('E5',1),('C5',1)],[('E5',3),(None,1)],
     [('C6',1.5),('B5',0.5),('A5',1),('E5',1)],[('D5',0.5),('E5',0.5),('F5',0.5),('G5',0.5),('B5',2)],[('A5',1),('F5',1),('C5',1),('A4',1)],[('G#4',1),('B4',1),('E5',2)],
     [('F5',1),('A5',1),('D5',1),('F5',1)],[('E5',1),('C5',1),('A4',1),('C5',1)],[('A4',1),('C5',1),('F5',1),('A5',1)],[('G#5',2),('E5',1),('D5',1)],
     [('D5',1),('F5',1),('A5',1),('F5',1)],[('E5',1),('G#4',1),('B4',1),('D5',1)],[('C5',1),('B4',0.5),('A4',2.5)],[('G#4',2),('B4',1),('E5',1)]]
L=len(chords)*BAR; total=int(SR*(L+3)); out=np.zeros((total,2))
def add(y,t0,pan):
    i=max(0,int(t0*SR)); j=min(total,i+len(y)); s=y[:j-i]; out[i:j,0]+=s*(1-pan)*0.7; out[i:j,1]+=s*(1+pan)*0.7
for b,c in enumerate(chords):
    t0=b*BAR; ns=CH[c]
    # rhythm guitar: bass on 1 & 3, arpeggio in eighths
    add(pluck(m2f(note(ns[0])),BAR*0.9,0.42,0.35),t0,-0.25)
    add(pluck(m2f(note(ns[1])),BEAT*2,0.25,0.4),t0+2*BEAT,-0.25)
    pat=[2,3,4,3,2,3,4,3]
    for k,pi in enumerate(pat):
        if k==0: continue
        add(pluck(m2f(note(ns[pi])),BEAT*1.2,0.16+0.04*(k%2==0),0.45),t0+k*BEAT/2+rng.normal(0,0.004),-0.35)
    # cajón: bass on 1, slap on 2 and 4, ghost on & of 3
    add(cajon('b',0.30),t0,0); add(cajon('s',0.18),t0+BEAT,0.05); add(cajon('s',0.07),t0+2.5*BEAT,0.05); add(cajon('s',0.18),t0+3*BEAT,0.05)
    # lead guitar
    tt=t0
    for nm,beats in mel[b]:
        d=beats*BEAT
        if nm:
            add(pluck(m2f(note(nm)),max(d*1.4,0.5),0.40,0.6),tt+rng.normal(0,0.003),0.3)
        tt+=d
loop=out[:int(SR*L)].copy(); tail=out[int(SR*L):]; loop[:len(tail)]+=tail
ir_n=int(SR*1.6); t=np.arange(ir_n)/SR
def circ(x,ir):
    n=len(x); return np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(np.pad(ir,(0,n-len(ir)))),n=n)
irs=[np.random.randn(ir_n)*np.exp(-t*3.2) for _ in range(2)]; irs=[ir/np.sqrt((ir**2).sum()) for ir in irs]
mix=loop*0.85+np.stack([circ(loop[:,0],irs[0]),circ(loop[:,1],irs[1])],1)*0.22
for ch in range(2): mix[:,ch]=lfilter([0.75],[1,-0.25],mix[:,ch])
mix/=np.abs(mix).max(); mix=np.tanh(mix*2.2)/np.tanh(2.2); mix/=np.abs(mix).max()*1.1
with wave.open('music/spain_loop.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('loop',L)

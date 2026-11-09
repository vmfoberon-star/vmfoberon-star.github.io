# Original light piece in D major — fingerpicked guitar (Karplus–Strong), soft mandolin-like lead and celesta bells. No drums. ~100 BPM.
import numpy as np, wave
from scipy.signal import lfilter
SR=44100; BPM=100; BEAT=60/BPM; BAR=4*BEAT
rng=np.random.default_rng(21); np.random.seed(21)
def m2f(m): return 440*2**((m-69)/12)
N={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def note(s): acc=1 if '#' in s else (-1 if (len(s)>2 and s[1]=='b') else 0); return 12*(int(s[-1])+1)+N[s[0]]+acc
def pluck(freq,dur,vel,bright=0.5,decay=0.997):
    n=int(SR*dur); p=int(SR/freq); b=lfilter([bright,1-bright],[1],rng.uniform(-1,1,p)); out=np.empty(n); k=0
    while k<n:
        m=min(p,n-k); out[k:k+m]=b[:m]; b=0.5*(b+np.roll(b,-1))*decay; k+=m
    t=np.arange(n)/SR; body=lfilter([1,-0.4],[1,-1.3,0.55],out)*0.25+out
    y=body*np.minimum(1,t/0.002)*np.minimum(1,np.maximum(0,dur-t)/0.08); return vel*y/(np.abs(y).max()+1e-9)
def bell(freq,dur,vel):
    n=int(SR*dur); t=np.arange(n)/SR
    y=(np.sin(2*np.pi*freq*t)+0.35*np.sin(2*np.pi*freq*2.0*t)*np.exp(-t*3)+0.15*np.sin(2*np.pi*freq*3.0*t)*np.exp(-t*6))*np.exp(-t*2.2)
    y*=np.minimum(1,t/0.003); return vel*y/np.abs(y).max()
CH={'D':['D2','A2','D3','F#3','A3','D4'],'A':['A1','E2','A2','C#3','E3','A3'],'Bm':['B1','F#2','B2','D3','F#3','B3'],
    'G':['G1','D2','G2','B2','D3','G3'],'Em':['E2','B2','E3','G3','B3','E4'],'F#m':['F#2','C#3','F#3','A3','C#4','F#4']}
chords=['D','A','Bm','G', 'D','G','A','A', 'D','A','Bm','F#m', 'G','D','Em','A',
        'G','A','F#m','Bm', 'G','D','Em','A', 'D','A','Bm','G', 'D','G','A','D']
mel=[[('F#5',1),('A5',1),('D6',1.5),('C#6',0.5)],[('B5',1),('A5',1),('E5',2)],[('F#5',1),('D5',1),('B4',1),('D5',1)],[('E5',3),(None,1)],
     [('F#5',1),('A5',1),('B5',1),('A5',1)],[('G5',1),('B5',1),('D6',2)],[('C#6',1),('B5',0.5),('A5',0.5),('E5',1),('C#5',1)],[('A5',3),(None,1)],
     [('A5',1),('F#5',1),('A5',1),('D6',1)],[('C#6',1.5),('B5',0.5),('A5',2)],[('B5',1),('D6',1),('F#6',1),('D6',1)],[('C#6',3),(None,1)],
     [('B5',1),('G5',1),('D5',1),('G5',1)],[('A5',1),('F#5',1),('D5',2)],[('E5',1),('G5',1),('B5',1),('G5',1)],[('A5',3),(None,1)],
     [('D6',1),('B5',1),('G5',1),('B5',1)],[('C#6',1),('A5',1),('E5',2)],[('A5',1),('C#6',1),('F#6',1.5),('E6',0.5)],[('D6',3),(None,1)],
     [('B5',1),('D6',1),('G6',1),('D6',1)],[('F#6',1),('E6',0.5),('D6',0.5),('A5',2)],[('G5',1),('B5',1),('E6',1),('D6',1)],[('C#6',3),(None,1)],
     [('F#5',1),('A5',1),('D6',1.5),('C#6',0.5)],[('B5',1),('A5',1),('E5',2)],[('F#5',1),('B5',1),('D6',1),('B5',1)],[('A5',1),('G5',1),('B5',2)],
     [('A5',1),('F#5',0.5),('A5',0.5),('D6',2)],[('B5',1),('D6',1),('G6',2)],[('E6',1),('C#6',1),('A5',1),('C#6',1)],[('D6',4)]]
L=len(chords)*BAR; total=int(SR*(L+3)); out=np.zeros((total,2))
def add(y,t0,pan):
    i=max(0,int(t0*SR)); j=min(total,i+len(y)); s=y[:j-i]; out[i:j,0]+=s*(1-pan)*0.7; out[i:j,1]+=s*(1+pan)*0.7
for b,c in enumerate(chords):
    t0=b*BAR; ns=CH[c]
    add(pluck(m2f(note(ns[0])),BAR*0.95,0.30,0.3),t0,-0.15)
    for k,pi in enumerate([2,4,3,5,2,4,3,4]):   # gentle travis-like arpeggio in eighths
        add(pluck(m2f(note(ns[pi])),BEAT*1.4,0.11+0.025*(k%2==0),0.5),t0+k*BEAT/2+rng.normal(0,0.004),-0.3)
    tt=t0
    for nm,beats in mel[b]:
        d=beats*BEAT
        if nm:
            add(pluck(m2f(note(nm)),max(d*1.4,0.5),0.34,0.75,0.9955),tt+rng.normal(0,0.003),0.3)
            if b%8 in (0,2,4,6) and beats>=1: add(bell(m2f(note(nm)+12),1.2,0.07),tt,0.45)
        tt+=d
loop=out[:int(SR*L)].copy(); tail=out[int(SR*L):]; loop[:len(tail)]+=tail
ir_n=int(SR*1.8); t=np.arange(ir_n)/SR
def circ(x,ir):
    n=len(x); return np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(np.pad(ir,(0,n-len(ir)))),n=n)
irs=[np.random.randn(ir_n)*np.exp(-t*2.8) for _ in range(2)]; irs=[ir/np.sqrt((ir**2).sum()) for ir in irs]
mix=loop*0.82+np.stack([circ(loop[:,0],irs[0]),circ(loop[:,1],irs[1])],1)*0.28
for ch in range(2): mix[:,ch]=lfilter([0.8],[1,-0.2],mix[:,ch])
mix/=np.abs(mix).max(); mix=np.tanh(mix*1.8)/np.tanh(1.8); mix/=np.abs(mix).max()*1.12
with wave.open('music/israel_loop.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('loop',L)

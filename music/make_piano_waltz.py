# Original calm piano waltz in F major, 3/4 at ~80 BPM. Same piano synthesis as make_israel_piano.py.
import numpy as np, wave
from scipy.signal import lfilter
SR=44100; BPM=80; BEAT=60/BPM; BAR=3*BEAT
rng=np.random.default_rng(9); np.random.seed(9)
def m2f(m): return 440*2**((m-69)/12)
N={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def note(s): acc=1 if '#' in s else (-1 if (len(s)>2 and s[1]=='b') else 0); return 12*(int(s[-1])+1)+N[s[0]]+acc
def piano(freq,dur,vel):
    n=int(SR*(dur+1.2)); t=np.arange(n)/SR; y=np.zeros(n); B=0.0004
    for k in range(1,9):
        fk=freq*k*np.sqrt(1+B*k*k)
        if fk>16000: break
        amp=(1/k**1.3)*(0.6+0.4*vel)
        dec=1.1+0.55*k+freq/700
        det=1+rng.normal(0,0.0004)
        y+=amp*(np.sin(2*np.pi*fk*t)+0.5*np.sin(2*np.pi*fk*det*t))*np.exp(-t*dec*(0.7 if k==1 else 1))
    y+=0.03*rng.normal(0,1,n)*np.exp(-t*90)     # hammer
    rel=np.ones(n); i=int(SR*dur); rel[i:]=np.exp(-(t[i:]-dur)*6)
    y*=rel*np.minimum(1,t/0.004)
    return vel*y/(np.abs(y).max()+1e-9)
CH={'F':['F2','C3','F3','A3'],'C':['C2','G2','C3','E3'],'Dm':['D2','A2','D3','F3'],'Bb':['Bb1','F2','Bb2','D3'],
    'Gm':['G2','D3','G3','Bb3'],'Am':['A1','E2','A2','C3'],'C7':['C2','G2','Bb2','E3']}
chords=['F','C','Dm','Bb', 'F','Gm','C','C7', 'F','Am','Bb','F', 'Gm','C','F','F',
        'Dm','Am','Bb','F', 'Gm','F','C','C7', 'F','C','Dm','Bb', 'Gm','C7','F','F']
mel=[[('C5',2),('A4',1)],[('G4',2),('C5',1)],[('A4',1.5),('D5',0.5),('F5',1)],[('D5',3)],
     [('C5',1),('F5',1),('A5',1)],[('G5',2),('D5',1)],[('E5',1),('G5',1),('C5',1)],[('E5',2),(None,1)],
     [('F5',2),('C5',1)],[('E5',2),('A4',1)],[('D5',1),('F5',1),('Bb5',1)],[('A5',3)],
     [('G5',1.5),('F5',0.5),('D5',1)],[('E5',1),('G5',1),('C6',1)],[('A5',2),('F5',1)],[('F5',2),(None,1)],
     [('F5',1),('A5',1),('D6',1)],[('C6',2),('E5',1)],[('D5',1),('F5',1),('Bb5',1)],[('A5',2),(None,1)],
     [('Bb5',1.5),('A5',0.5),('G5',1)],[('A5',1),('F5',1),('C5',1)],[('E5',1),('G5',1),('C6',1)],[('Bb5',2),(None,1)],
     [('A5',2),('F5',1)],[('G5',2),('E5',1)],[('F5',1),('D5',1),('A4',1)],[('Bb4',2),('D5',1)],
     [('G5',1),('Bb5',1),('D5',1)],[('E5',2),('G5',1)],[('F5',3)],[('F5',2),(None,1)]]
L=len(chords)*BAR; total=int(SR*(L+4)); out=np.zeros((total,2))
def add(y,t0,pan):
    i=max(0,int(t0*SR)); j=min(total,i+len(y)); s=y[:j-i]; out[i:j,0]+=s*(1-pan)*0.7; out[i:j,1]+=s*(1+pan)*0.7
for b,c in enumerate(chords):
    t0=b*BAR; ns=CH[c]
    add(piano(m2f(note(ns[0])),BAR*0.95,0.24),t0+rng.normal(0,0.005),-0.25)      # bass on 1
    for k in (1,2):                                                              # soft chord on 2 and 3
        for pi in (2,3): add(piano(m2f(note(ns[pi])),BEAT*0.9,0.11),t0+k*BEAT+rng.normal(0,0.006),-0.05)
    tt=t0
    for nm,beats in mel[b]:
        d=beats*BEAT
        if nm: add(piano(m2f(note(nm)),d*1.1,0.36),tt+rng.normal(0,0.006),0.2)
        tt+=d
loop=out[:int(SR*L)].copy(); tail=out[int(SR*L):]; loop[:len(tail)]+=tail
ir_n=int(SR*2.4); t=np.arange(ir_n)/SR
def circ(x,ir):
    n=len(x); return np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(np.pad(ir,(0,n-len(ir)))),n=n)
irs=[np.random.randn(ir_n)*np.exp(-t*2.2) for _ in range(2)]; irs=[ir/np.sqrt((ir**2).sum()) for ir in irs]
mix=loop*0.8+np.stack([circ(loop[:,0],irs[0]),circ(loop[:,1],irs[1])],1)*0.32
for ch in range(2): mix[:,ch]=lfilter([0.7],[1,-0.3],mix[:,ch])
mix/=np.abs(mix).max(); mix=np.tanh(mix*1.4)/np.tanh(1.4); mix/=np.abs(mix).max()*1.15
with wave.open('music/piano_waltz.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('loop',L)

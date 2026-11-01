# Original piece in D Freygish (Ahava Raba: D Eb F# G A Bb C) — plucked oud-like lead and guitar (Karplus–Strong) with soft darbuka. Calm, warm, ~92 BPM.
import numpy as np, wave
from scipy.signal import lfilter
SR=44100; BPM=92; BEAT=60/BPM; BAR=4*BEAT
rng=np.random.default_rng(11); np.random.seed(11)
def m2f(m): return 440*2**((m-69)/12)
N={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def note(s): acc=1 if '#' in s else (-1 if (len(s)>2 and s[1]=='b') else 0); return 12*(int(s[-1])+1)+N[s[0]]+acc
def pluck(freq,dur,vel,bright=0.5,decay=0.9965):
    n=int(SR*dur); p=int(SR/freq); b=lfilter([bright,1-bright],[1],rng.uniform(-1,1,p)); out=np.empty(n); k=0
    while k<n:
        m=min(p,n-k); out[k:k+m]=b[:m]; b=0.5*(b+np.roll(b,-1))*decay; k+=m
    t=np.arange(n)/SR; body=lfilter([1,-0.5],[1,-1.45,0.62],out)*0.3+out
    y=body*np.minimum(1,t/0.002)*np.minimum(1,np.maximum(0,dur-t)/0.08); return vel*y/(np.abs(y).max()+1e-9)
def drum(kind,vel):
    n=int(SR*0.3); t=np.arange(n)/SR
    if kind=='dum': y=np.sin(2*np.pi*95*t*np.exp(-t*5))*np.exp(-t*14)
    elif kind=='tek': y=lfilter([1,-0.95],[1],rng.normal(0,1,n))*np.exp(-t*60)*0.6+np.sin(2*np.pi*620*t)*np.exp(-t*45)*0.4
    else: y=lfilter([1,-0.9],[1],rng.normal(0,1,n))*np.exp(-t*80)*0.35
    return vel*y/np.abs(y).max()
CH={'D':['D2','A2','D3','F#3','A3'],'Cm':['C2','G2','C3','Eb3','G3'],'Gm':['G2','D3','G3','Bb3','D4'],'Eb':['Eb2','Bb2','Eb3','G3','Bb3'],'Bb':['Bb1','F2','Bb2','D3','F3']}
chords=['D','D','Cm','D', 'Gm','Cm','D','D', 'D','Eb','D','Cm', 'Gm','Eb','D','D',
        'Gm','Gm','Cm','D', 'Bb','Cm','D','D', 'Gm','Eb','D','Cm', 'Gm','Eb','D','D']
mel=[[('D5',1),('Eb5',0.5),('F#5',0.5),('G5',2)],[('F#5',1),('Eb5',1),('D5',2)],[('C5',1),('Eb5',1),('G5',1),('F#5',1)],[('D5',3),(None,1)],
     [('G5',1),('A5',0.5),('Bb5',0.5),('A5',1),('G5',1)],[('G5',1),('F#5',0.5),('Eb5',0.5),('C5',2)],[('Eb5',1),('F#5',1),('Eb5',1),('D5',1)],[('D5',3),(None,1)],
     [('A5',1.5),('Bb5',0.5),('A5',1),('G5',1)],[('G5',1),('F#5',0.5),('G5',0.5),('Eb5',2)],[('F#5',1),('G5',0.5),('F#5',0.5),('Eb5',1),('D5',1)],[('C5',1),('Eb5',1),('D5',1),('C5',1)],
     [('Bb4',1),('D5',1),('G5',1),('A5',1)],[('Bb5',1.5),('A5',0.5),('G5',2)],[('F#5',1),('Eb5',1),('D5',1),('Eb5',1)],[('D5',3),(None,1)],
     [('D6',1.5),('C6',0.5),('Bb5',1),('A5',1)],[('Bb5',1),('A5',0.5),('G5',0.5),('D5',2)],[('C6',1),('Bb5',0.5),('A5',0.5),('G5',1),('Eb5',1)],[('F#5',3),(None,1)],
     [('F5',1),('Bb5',1),('A5',1),('G5',1)],[('G5',1),('Eb5',1),('C5',1),('Eb5',1)],[('D5',1),('F#5',1),('A5',1),('F#5',1)],[('D5',3),(None,1)],
     [('G5',0.5),('A5',0.5),('Bb5',1),('A5',1),('G5',1)],[('G5',1),('Bb5',1),('Eb5',2)],[('F#5',0.5),('G5',0.5),('A5',1),('G5',1),('F#5',1)],[('Eb5',1),('D5',1),('C5',2)],
     [('Bb4',1),('C5',0.5),('D5',0.5),('G5',2)],[('G5',1),('F#5',0.5),('Eb5',0.5),('C5',2)],[('Eb5',1),('F#5',1),('Eb5',1),('C5',1)],[('D5',4)]]
L=len(chords)*BAR; total=int(SR*(L+3)); out=np.zeros((total,2))
def add(y,t0,pan):
    i=max(0,int(t0*SR)); j=min(total,i+len(y)); s=y[:j-i]; out[i:j,0]+=s*(1-pan)*0.7; out[i:j,1]+=s*(1+pan)*0.7
for b,c in enumerate(chords):
    t0=b*BAR; ns=CH[c]
    add(pluck(m2f(note(ns[0])),BAR*0.9,0.40,0.35),t0,-0.2)
    add(pluck(m2f(note(ns[1])),BEAT*2,0.22,0.4),t0+2*BEAT,-0.2)
    for k,pi in enumerate([2,3,4,3,2,4,3,4]):
        if k==0: continue
        add(pluck(m2f(note(ns[pi])),BEAT*1.2,0.13+0.03*(k%2==0),0.45),t0+k*BEAT/2+rng.normal(0,0.004),-0.35)
    # maqsum-like darbuka: dum tek . tek dum . tek .
    for pos,kind,v in [(0,'dum',0.30),(1,'tek',0.15),(1.5,'ka',0.08),(2,'dum',0.22),(2.5,'ka',0.07),(3,'tek',0.15),(3.5,'ka',0.08)]:
        add(drum(kind,v),t0+pos*BEAT+rng.normal(0,0.003),0.05)
    tt=t0
    for nm,beats in mel[b]:
        d=beats*BEAT
        if nm: add(pluck(m2f(note(nm)),max(d*1.3,0.45),0.42,0.7,0.9945),tt+rng.normal(0,0.003),0.3)
        tt+=d
loop=out[:int(SR*L)].copy(); tail=out[int(SR*L):]; loop[:len(tail)]+=tail
ir_n=int(SR*1.6); t=np.arange(ir_n)/SR
def circ(x,ir):
    n=len(x); return np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(np.pad(ir,(0,n-len(ir)))),n=n)
irs=[np.random.randn(ir_n)*np.exp(-t*3.2) for _ in range(2)]; irs=[ir/np.sqrt((ir**2).sum()) for ir in irs]
mix=loop*0.85+np.stack([circ(loop[:,0],irs[0]),circ(loop[:,1],irs[1])],1)*0.24
for ch in range(2): mix[:,ch]=lfilter([0.75],[1,-0.25],mix[:,ch])
mix/=np.abs(mix).max(); mix=np.tanh(mix*2.2)/np.tanh(2.2); mix/=np.abs(mix).max()*1.1
with wave.open('music/israel_loop.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('loop',L)

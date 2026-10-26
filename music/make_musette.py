# Original musette-style waltz in D minor: accordion (two detuned reeds + vibrato) over oom-pah-pah.
import numpy as np, wave
from scipy.signal import lfilter
SR=44100; BPM=150; BEAT=60/BPM; BAR=3*BEAT
rng=np.random.default_rng(7); np.random.seed(7)
def m2f(m): return 440*2**((m-69)/12)
N={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def note(s): acc=1 if '#' in s else (-1 if (len(s)>2 and s[1]=='b') else 0); return 12*(int(s[-1])+1)+N[s[0]]+acc
def reed(freq,dur,vel):
    n=int(SR*dur); t=np.arange(n)/SR; vib=1+0.004*np.sin(2*np.pi*5.5*t)
    y=np.zeros(n)
    for det in (-0.0035,0.0,0.0035):
        ph=2*np.pi*np.cumsum(freq*(1+det)*vib)/SR
        for h in range(1,9): y+=np.sin(h*ph)/(h**1.3)*(0.9 if h%2 else 0.6)
    env=np.minimum(1,t/0.03)*np.minimum(1,np.maximum(0,(dur-t))/0.06)
    return vel*y*env/np.abs(y).max()
def pluck(freq,dur,vel,decay=4.0):
    n=int(SR*dur); t=np.arange(n)/SR; y=np.zeros(n)
    for h in range(1,8): y+=np.sin(2*np.pi*freq*h*t)/(h**1.4)*np.exp(-t*decay*(1+0.4*(h-1)))
    return vel*y*np.minimum(1,t/0.004)/np.abs(y).max()
chords=['Dm','Dm','A7','A7','A7','A7','Dm','Dm','Gm','Gm','Dm','Dm','E7','A7','Dm','Dm']
CH={'Dm':('D2',['D3','F3','A3']),'A7':('A1',['C#3','E3','G3']),'Gm':('G1',['D3','G3','Bb3']),'E7':('E2',['D3','G#3','B3'])}
mel=[[('A4',1),('D5',1),('F5',1)],[('E5',2),('D5',1)],[('C#5',1),('E5',1),('G5',1)],[('F5',2),('E5',1)],
     [('E5',1),('C#5',1),('A4',1)],[('G4',2),('A4',1)],[('F4',1),('A4',1),('D5',1)],[('D5',3)],
     [('D5',1),('G5',1),('Bb5',1)],[('A5',2),('G5',1)],[('F5',1),('E5',1),('D5',1)],[('A4',2),('D5',1)],
     [('B4',1),('D5',1),('G#5',1)],[('G5',1),('E5',1),('C#5',1)],[('D5',2),('A4',1)],[('D5',3)]]
chords=chords*2; mel=mel+mel
L=len(chords)*BAR; total=int(SR*(L+3)); out=np.zeros((total,2))
def add(y,t0,pan):
    i=max(0,int(t0*SR)); j=min(total,i+len(y)); s=y[:j-i]; out[i:j,0]+=s*(1-pan)*0.7; out[i:j,1]+=s*(1+pan)*0.7
for b,c in enumerate(chords):
    t0=b*BAR; bass,tri=CH[c]
    add(pluck(m2f(note(bass)),BEAT*1.2,0.5,3.0),t0,-0.15)
    for k in (1,2):
        for nn in tri: add(pluck(m2f(note(nn)),BEAT*0.8,0.13,7.0),t0+k*BEAT+rng.normal(0,0.004),-0.3)
    tt=t0
    for nm,beats in mel[b]:
        d=beats*BEAT; sh=12 if b>=16 and b<30 else 0
        add(reed(m2f(note(nm)+sh),d*0.96,0.22 if sh else 0.26),tt,0.25)
        if sh: add(reed(m2f(note(nm)),d*0.96,0.10),tt,0.1)
        tt+=d
loop=out[:int(SR*L)].copy(); tail=out[int(SR*L):]; loop[:len(tail)]+=tail
ir_n=int(SR*1.5); t=np.arange(ir_n)/SR
def circ(x,ir):
    n=len(x); return np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(np.pad(ir,(0,n-len(ir)))),n=n)
irs=[np.random.randn(ir_n)*np.exp(-t*3.8) for _ in range(2)]; irs=[ir/np.sqrt((ir**2).sum()) for ir in irs]
mix=loop*0.85+np.stack([circ(loop[:,0],irs[0]),circ(loop[:,1],irs[1])],1)*0.22
for ch in range(2): mix[:,ch]=lfilter([0.7],[1,-0.3],mix[:,ch])
mix/=np.abs(mix).max()*1.12
with wave.open('music/paris_loop.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('loop',L)

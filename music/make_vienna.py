# Original Viennese-style waltz in F major: strings (bowed, slow attack) + piano oom-pah-pah with the Viennese "early second beat".
import numpy as np, wave
from scipy.signal import lfilter
SR=44100; BPM=168; BEAT=60/BPM; BAR=3*BEAT
rng=np.random.default_rng(13); np.random.seed(13)
def m2f(m): return 440*2**((m-69)/12)
N={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def note(s): acc=1 if '#' in s else (-1 if (len(s)>2 and s[1]=='b') else 0); return 12*(int(s[-1])+1)+N[s[0]]+acc
def string(freq,dur,vel):
    n=int(SR*dur); t=np.arange(n)/SR; vib=1+0.005*np.sin(2*np.pi*5.2*t+rng.uniform(0,6))*np.minimum(1,t/0.3)
    y=np.zeros(n)
    for det in (-0.004,0.0,0.004):
        ph=2*np.pi*np.cumsum(freq*(1+det)*vib)/SR
        for h in range(1,10): y+=np.sin(h*ph+rng.uniform(0,6))/h**1.1
    y=lfilter([0.5],[1,-0.5],y)
    env=np.minimum(1,t/0.09)*np.minimum(1,np.maximum(0,(dur-t))/0.12)
    return vel*y*env/np.abs(y).max()
def piano(freq,dur,vel,decay=3.5):
    n=int(SR*dur); t=np.arange(n)/SR; y=np.zeros(n)
    for h in range(1,9): y+=np.sin(2*np.pi*freq*h*(1+0.0004*h*h)*t)/(h**1.5)*np.exp(-t*decay*(1+0.5*(h-1)))
    env=np.minimum(1,t/0.003)*np.minimum(1,np.maximum(0,dur-t)/0.05)
    return vel*y*env/np.abs(y).max()
CH={'F':('F2',['A3','C4','F4']),'C7':('C2',['Bb3','C4','E4']),'Bb':('Bb1',['Bb3','D4','F4']),'Gm':('G2',['Bb3','D4','G4']),
    'D7':('D2',['C4','F#4','A4']),'G7':('G2',['B3','D4','F4']),'Dm':('D2',['A3','D4','F4'])}
chords=['F','F','F','C7','C7','C7','C7','F', 'F','F','Bb','Bb','F','D7','G7','C7',
        'Bb','Bb','F','F','C7','C7','F','F', 'Gm','Gm','F','Dm','G7','C7','F','F']
mel=[[('C5',3)],[('A5',2),('G5',1)],[('F5',2),('A5',1)],[('G5',3)],[('E5',2),('G5',1)],[('Bb5',2),('A5',1)],[('G5',2),('E5',1)],[('F5',3)],
     [('C5',3)],[('A5',2),('C6',1)],[('D6',2),('C6',1)],[('Bb5',3)],[('A5',2),('F5',1)],[('F#5',2),('A5',1)],[('B5',2),('G5',1)],[('E5',2),('C5',1)],
     [('D6',3)],[('D6',2),('C6',1)],[('C6',2),('A5',1)],[('F5',3)],[('G5',2),('A5',1)],[('Bb5',2),('G5',1)],[('A5',2),('C6',1)],[('F6',3)],
     [('D6',2),('Bb5',1)],[('G5',2),('Bb5',1)],[('A5',2),('F5',1)],[('D5',2),('F5',1)],[('G5',2),('B5',1)],[('E5',2),('G5',1)],[('F5',3)],[('F5',3)]]
L=len(chords)*BAR; total=int(SR*(L+3)); out=np.zeros((total,2))
def add(y,t0,pan):
    i=max(0,int(t0*SR)); j=min(total,i+len(y)); s=y[:j-i]; out[i:j,0]+=s*(1-pan)*0.7; out[i:j,1]+=s*(1+pan)*0.7
for b,c in enumerate(chords):
    t0=b*BAR; bass,tri=CH[c]
    add(piano(m2f(note(bass)),BEAT*1.3,0.45,2.5),t0,-0.2)
    for off in (0.88,1.98):          # Viennese lilt: 2nd beat early
        for nn in tri: add(piano(m2f(note(nn)),BEAT*0.9,0.11,6.0),t0+off*BEAT+rng.normal(0,0.003),-0.3)
    tt=t0
    for nm,beats in mel[b]:
        d=beats*BEAT
        add(string(m2f(note(nm)),d*1.02,0.24),tt,0.25)
        add(string(m2f(note(nm)-12),d*1.02,0.10),tt,0.0)
        tt+=d
loop=out[:int(SR*L)].copy(); tail=out[int(SR*L):]; loop[:len(tail)]+=tail
ir_n=int(SR*2.2); t=np.arange(ir_n)/SR
def circ(x,ir):
    n=len(x); return np.fft.irfft(np.fft.rfft(x)*np.fft.rfft(np.pad(ir,(0,n-len(ir)))),n=n)
irs=[np.random.randn(ir_n)*np.exp(-t*2.6) for _ in range(2)]; irs=[ir/np.sqrt((ir**2).sum()) for ir in irs]
mix=loop*0.8+np.stack([circ(loop[:,0],irs[0]),circ(loop[:,1],irs[1])],1)*0.3
for ch in range(2): mix[:,ch]=lfilter([0.7],[1,-0.3],mix[:,ch])
mix/=np.abs(mix).max()*1.12
with wave.open('music/vienna_loop.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('loop',L)

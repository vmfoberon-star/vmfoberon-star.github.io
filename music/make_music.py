# Original short waltz in A minor: plucked guitar arpeggios, mandolin-like tremolo melody, soft bass. Renders a seamless loop.
import numpy as np, subprocess, wave
SR=44100; BPM=84; BEAT=60/BPM; BAR=3*BEAT
def m2f(m): return 440*2**((m-69)/12)
def pluck(freq,dur,vel=0.5,bright=1.0,decay=2.2):
    n=int(SR*dur); t=np.arange(n)/SR; y=np.zeros(n)
    for h in range(1,12):
        if freq*h>SR/2.3: break
        amp=(1/h**1.15)*(bright**(h-1))
        y+=amp*np.sin(2*np.pi*freq*h*t+np.random.rand()*6.28)*np.exp(-t*decay*(1+0.35*(h-1)))
    att=np.minimum(1,t/0.004); y*=att
    nz=np.random.randn(n)*np.exp(-t*90)*0.15; y+=nz
    return vel*y/ max(1e-9,np.abs(y).max())
N={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def note(s):  # 'G#4'
    acc=1 if '#' in s else (-1 if 'b' in s[1:] else 0); return 12*(int(s[-1])+1)+N[s[0]]+acc
chords=['Am','Am','Dm','Dm','G','G','C','E','Am','Am','Dm','Dm','F','E','Am','Am']
CH={'Am':['A2','E3','A3','C4','E4'],'Dm':['D3','A3','D4','F4','A4'],'G':['G2','D3','G3','B3','D4'],
    'C':['C3','G3','C4','E4','G4'],'E':['E2','B2','E3','G#3','B3'],'F':['F2','C3','F3','A3','C4']}
mel=[[('E5',2),('C5',1)],[('A4',2),('B4',1)],[('C5',1),('D5',1),('F5',1)],[('E5',2),('D5',1)],
     [('D5',2),('B4',1)],[('G4',2),('A4',1)],[('B4',1),('C5',1),('E5',1)],[('G#4',2),('B4',1)],
     [('A4',2),('C5',1)],[('E5',2),('A5',1)],[('A5',2),('F5',1)],[('D5',2),('F5',1)],
     [('E5',1),('D5',1),('C5',1)],[('B4',2),('G#4',1)],[('A4',3)],[('A4',2),('E4',1)]]
L=len(chords)*BAR; total=int(SR*(L+4)); out=np.zeros((total,2))
def add(y,t0,pan=0.0):
    i=max(0,int(t0*SR)); j=min(total,i+len(y)); seg=y[:j-i]
    out[i:j,0]+=seg*(1-pan)*0.5*2**0.5*0.71; out[i:j,1]+=seg*(1+pan)*0.5*2**0.5*0.71
rng=np.random.default_rng(3); np.random.seed(3)
for b,c in enumerate(chords):
    t0=b*BAR; v=CH[c]
    add(pluck(m2f(note(v[0])),BAR*1.4,0.55,0.55,1.3),t0,-0.1)          # bass on 1
    pat=[1,2,3,4,3,2]
    for k,idx in enumerate(pat):                                         # eighth-note arpeggio
        sw=rng.normal(0,0.006)
        add(pluck(m2f(note(v[idx])),1.6,0.22+0.04*(k==0),0.75,2.0),t0+k*BEAT/2+sw,-0.35)
    tt=t0
    for nm,beats in mel[b]:                                              # tremolo melody
        f=m2f(note(nm)); d=beats*BEAT; step=BEAT/4; k=0
        while k*step<d-0.02:
            vel=0.20*(1.0 if k==0 else 0.62+0.1*rng.random())
            add(pluck(f*(1+rng.normal(0,0.0008)),0.45,vel,0.85,7.0),tt+k*step+rng.normal(0,0.004),0.35)
            k+=1
        add(pluck(f,d+0.6,0.10,0.6,1.6),tt,0.35)
        tt+=d
# wrap tail for seamless loop
loop=out[:int(SR*L)].copy(); tail=out[int(SR*L):]; loop[:len(tail)]+=tail
# reverb: exponentially decaying noise IR
ir_n=int(SR*1.9); t=np.arange(ir_n)/SR
irL=np.random.randn(ir_n)*np.exp(-t*3.2); irR=np.random.randn(ir_n)*np.exp(-t*3.2)
irL/=np.sqrt((irL**2).sum()); irR/=np.sqrt((irR**2).sum())
def circ_conv(x,ir):
    n=len(x); X=np.fft.rfft(x,n=n); H=np.fft.rfft(np.pad(ir,(0,max(0,n-len(ir))))[:n],n=n); return np.fft.irfft(X*H,n=n)
wet=np.stack([circ_conv(loop[:,0],irL),circ_conv(loop[:,1],irR)],1)
mix=loop*0.82+wet*0.30
# gentle lowpass / warmth via one-pole
a=0.35
for ch in range(2):
    y=mix[:,ch]; z=np.empty_like(y); s=0.0
    from scipy.signal import lfilter
    mix[:,ch]=lfilter([1-a],[1,-a],y)
mix/=np.abs(mix).max()*1.12
pcm=(mix*32767).astype(np.int16)
with wave.open('music/italia_loop.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('loop seconds',L)

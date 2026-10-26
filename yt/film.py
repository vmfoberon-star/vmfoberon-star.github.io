# Short Full HD films from the trip's own video clips: crossfaded segments, natural sound + soft music, title/outro cards.
import sys, os, subprocess, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT='/home/claude/travel'; OUT=f'{ROOT}/yt/out_hd'; os.makedirs(OUT,exist_ok=True)
W,H=1920,1080; K=1.5; GOLD=(232,176,74)
F=lambda n,s: ImageFont.truetype(f'{ROOT}/yt/fonts/{n}.ttf',round(s*K))
SP='/mnt/user-data/uploads/Videos/Spain 2013/'
M=SP+'2013-09_Madrid day1/'; A=SP+'2013-09_Avila/'
FILMS=[
 ('Гран-Виа и площадь Испании','Мадрид из окна автобуса · 28 августа',[(M+'00397.MTS',0,40),(M+'00397.MTS',44,104)]),
 ('Сибелес и «Метрополис»','Мадрид из окна автобуса',[(M+'00402.MTS',10,40),(M+'00402.MTS',72,128),(M+'00406.MTS',0,26)]),
 ('Площадь Колумба и Кастельяна','Мадрид из окна автобуса',[(M+'00395.MTS',8,58),(M+'00400.MTS',0,30),(M+'00401.MTS',80,108)]),
 ('Стены Авилы','Авила · 2 сентября',[(A+'avila1.MTS',6,32),(A+'avila1.MTS',64,142)]),
]
TRIP='Испания 2013'; MUSIC=f'{ROOT}/music/spain_loop.wav'; XF=0.8; TI=4.0; TO=4.0

def shadowed(im,xy,txt,font,fill):
    sh=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(sh); d.text((xy[0]+3,xy[1]+4),txt,font=font,fill=(0,0,0,210),anchor='ms')
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); ImageDraw.Draw(im).text(xy,txt,font=font,fill=fill,anchor='ms')
def card(path,lines):
    im=Image.new('RGBA',(W,H),(0,0,0,150)); y=H//2-sum(l[2] for l in lines)*K//2
    for t,f,dy,c in lines: y+=dy*K; shadowed(im,(W//2,y),t,f,c)
    im.save(path)

def make(i,title,sub,segs):
    fn=f'{OUT}/spain13_video_{i+1:02d}.mp4'; tmp=f'/tmp/film{i}'; os.makedirs(tmp,exist_ok=True)
    total=sum(b-a for _,a,b in segs)-XF*(len(segs)-1)
    card(f'{tmp}/in.png',[('ОЛЬГА И ВЛАДИМИР ФРОНТОН',F('golos-text-500-normal',20),0,GOLD+(255,)),(TRIP+' · видео',F('cormorant-garamond-500-italic',76),90,(255,255,255,255)),
        (title,F('golos-text-400-normal',34),72,(240,240,240,255)),(sub,F('golos-text-400-normal',24),48,(205,205,205,255))])
    card(f'{tmp}/out.png',[('Сами ездим, сами снимаем, сами монтируем',F('cormorant-garamond-500-italic',46),0,(255,255,255,255)),('ОЛЬГА И ВЛАДИМИР ФРОНТОН',F('golos-text-500-normal',22),70,GOLD+(255,))])
    args=['ffmpeg','-y','-loglevel','error']
    for p,a,b in segs: args+=['-ss',str(a),'-t',str(b-a),'-i',p]
    n=len(segs); args+=['-loop','1','-i',f'{tmp}/in.png','-loop','1','-i',f'{tmp}/out.png','-stream_loop','-1','-i',MUSIC]
    fc=[]
    for k in range(n):
        fc.append(f'[{k}:v:0]yadif=0:-1:1,scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6,fps=25,format=yuv420p,setsar=1[v{k}]')
        fc.append(f'[{k}:a:0]aresample=48000,aformat=channel_layouts=stereo,volume=0.45[a{k}]')
    v='v0'; a='a0'; off=0
    for k in range(1,n):
        off+=segs[k-1][2]-segs[k-1][1]-XF
        fc.append(f'[{v}][v{k}]xfade=transition=fade:duration={XF}:offset={off:.3f}[vx{k}]'); v=f'vx{k}'
        fc.append(f'[{a}][a{k}]acrossfade=d={XF}[ax{k}]'); a=f'ax{k}'
    fc.append(f'[{n}:v]format=rgba,trim=0:{TI},fade=t=in:st=0:d=0.8:alpha=1,fade=t=out:st={TI-0.8}:d=0.8:alpha=1,setpts=PTS-STARTPTS[ci]')
    fc.append(f'[{n+1}:v]format=rgba,trim=0:{TO},fade=t=in:st=0:d=0.8:alpha=1,setpts=PTS-STARTPTS+{total-TO:.3f}/TB[co]')
    fc.append(f'[{v}]fade=t=in:st=0:d=1,fade=t=out:st={total-1.2:.3f}:d=1.2[vf]')
    fc.append(f'[vf][ci]overlay=eof_action=pass[vo1]'); fc.append(f'[vo1][co]overlay=eof_action=pass,format=yuv420p[vout]')
    fc.append(f'[{n+2}:a]atrim=0:{total:.3f},volume=0.55[mu]')
    fc.append(f'[{a}][mu]amix=inputs=2:duration=first:normalize=0,afade=t=in:d=1.5,afade=t=out:st={total-3:.3f}:d=3[aout]')
    br=min(6000,int(26.5*8000/total)-200)
    args+=['-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-t',f'{total:.3f}',
           '-c:v','libx264','-preset','slow','-b:v',f'{br}k','-maxrate',f'{br+300}k','-bufsize','6000k','-pix_fmt','yuv420p',
           '-c:a','aac','-b:a','160k','-movflags','+faststart',fn]
    subprocess.run(args,check=True); print('done',fn,round(total,1),os.path.getsize(fn)//1000000,'MB',flush=True)

if __name__=='__main__':
    idx=[int(x) for x in sys.argv[1:]] or range(len(FILMS))
    for i in idx: make(i,*FILMS[i])

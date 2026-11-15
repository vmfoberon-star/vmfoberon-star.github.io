"""Builds ../site/israel/ from data_il.py (+ gal/<id>.txt photo lists if present)."""
import os,json,sys,shutil,glob
D=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,D)
import importlib,data_il;importlib.reload(data_il)
OUT=os.path.join(D,'..','site','israel');os.makedirs(OUT,exist_ok=True)
trips=[]
for t in data_il.TRIPS:
    t=dict(t);g=[]
    pdir=os.path.join(D,'photos',t['id'])
    capf=os.path.join(D,'gal',t['id']+'.txt')
    if os.path.isdir(pdir):
        caps={}
        if os.path.exists(capf):
            for line in open(capf,encoding='utf8'):
                if '|' in line: k,c=line.rstrip('\n').split('|',1);caps[k]=c
        for f in sorted(os.listdir(pdir)):
            if f.endswith('.webp') and not f.startswith('t_'):
                k=f[:-5];g.append([f'photos/{t["id"]}/t_{f}',caps.get(k,''),f'photos/{t["id"]}/{f}'])
        if g and not t.get('cover'): t['cover']=g[t.get('ci',0)][2]
    t['g']=g; trips.append(t)
if os.path.isdir(os.path.join(D,'photos')):
    shutil.copytree(os.path.join(D,'photos'),os.path.join(OUT,'photos'),dirs_exist_ok=True)
hero=[t['cover'] for t in trips if t.get('cover') and t.get('hero')]
# best photos: data_il.BEST ('tripid/NN' list) if present, else each photo trip's cover frame
best=[]
byid={t['id']:t for t in trips}
picks=getattr(data_il,'BEST',None) or [f"{t['id']}/{t.get('ci',0):02d}" for t in sorted(trips,key=lambda t:t['s'],reverse=True) if t['g']]
for k in picks:
    tid,n=k.split('/');t=byid.get(tid)
    if not t: continue
    for g in t['g']:
        if g[2].endswith(f'/{n}.webp'): best.append([g[0],g[1],g[2],tid,t['t']+' · '+t['y']]);break
# slideshow music
mdir=os.path.join(D,'..','music');os.makedirs(os.path.join(OUT,'music'),exist_ok=True)
for src,dst in [('israel_loop.webm','israel_loop.webm'),('israel_loop.m4a','israel_loop.mp4')]:
    shutil.copy(os.path.join(mdir,src),os.path.join(OUT,'music',dst))
data=dict(regions=data_il.REGIONS,trips=trips,concerts=sorted(data_il.CONCERTS,key=lambda c:c[2],reverse=True),hero=hero,best=best)
html=open(os.path.join(D,'template_il.html'),encoding='utf8').read()
og='<meta property="og:image" content="https://vmfoberon-star.github.io/israel/'+hero[0]+'">' if hero else ''
html=html.replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__OG__',og)
open(os.path.join(OUT,'index.html'),'w',encoding='utf8').write(html)
print('israel:',len(trips),'trips,',sum(len(t['g']) for t in trips),'photos,',len(data_il.CONCERTS),'concerts,',len(best),'best')

# ---- English version: site/israel/en/index.html (strings from tr_il.py) ----
import re,copy,tr_il;importlib.reload(tr_il)
T=tr_il.D;miss=[]
cyr=re.compile('[А-Яа-яЁё]')
def tr(x):
    if not x or not cyr.search(x): return x
    if x not in T: miss.append(x); return x
    return T[x]
pp=lambda u:'../'+u
ed=copy.deepcopy(data)
ed['regions']=[(k,tr(n)) for k,n in ed['regions']]
for t in ed['trips']:
    for k in ('t','p','b'): t[k]=tr(t.get(k))
    t['y']=t['y'].replace('около ','c. ')
    t['v']=[[v[0],tr(v[1])]+list(v[2:]) for v in t.get('v',[])]
    t['g']=[[pp(g[0]),tr(g[1]),pp(g[2])] for g in t['g']]
    if t.get('cover'): t['cover']=pp(t['cover'])
ed['concerts']=[tuple(tr(x) if isinstance(x,str) else x for x in c) for c in ed['concerts']]
ed['hero']=[pp(h) for h in ed['hero']]
enby={t['id']:t for t in ed['trips']}
ed['best']=[[pp(b[0]),tr(b[1]),pp(b[2]),b[3],enby[b[3]]['t']+' · '+enby[b[3]]['y']] for b in ed['best']]
if miss: raise SystemExit('israel EN: add translations to israel/tr_il.py for:\n'+'\n'.join(sorted(set(miss))))
UI=[('<html lang="ru">','<html lang="en">'),
 ('<title>Наш Израиль</title>','<title>Our Israel</title>'),('content="Наш Израиль"','content="Our Israel"'),
 ('Поездки, прогулки и концерты Ольги и Владимира Фронтон','Trips, walks and concerts of Olga and Vladimir Fronton'),
 ('href="../favicon.png"','href="../../favicon.png"'),('href="../apple-touch-icon.png"','href="../../apple-touch-icon.png"'),
 ('<a class="brand" href="#">Наш Израиль</a>','<a class="brand" href="#">Our Israel</a>'),
 ('aria-label="Разделы"','aria-label="Sections"'),('<a href="#trips">Поездки</a>','<a href="#trips">Trips</a>'),
 ('<a href="#best">Лучшие фото</a>','<a href="#best">Best photos</a>'),('<a href="#mapSec">Карта</a>','<a href="#mapSec">Map</a>'),
 ('<a href="#concerts">Концерты</a>','<a href="#concerts">Concerts</a>'),('<a href="../">Путешествия по миру</a>','<a href="../../en/">World travels</a>'),
 ('title="Получать новости сайта">НОВОСТИ</a>','title="Get site news">NEWS</a>'),
 ('id="langLink" href="en/" hreflang="en" lang="en" title="English version">EN</a>','id="langLink" href="../" hreflang="ru" lang="ru" title="Русская версия">RU</a>'),
 ('Ольга и Владимир · 25 лет в Израиле','Olga and Vladimir · 25 years in Israel'),('<h1>Наш Израиль</h1>','<h1>Our Israel</h1>'),
 ('Страна, где мы живём: поездки от Голан до Эйлата, прогулки по Иерусалиму и Модиину, концерты и музыкальные вечера.','The country we live in: trips from the Golan to Eilat, walks in Jerusalem and Modi\'in, concerts and musical evenings.'),
 ('<h2>Лучшие фото</h2>','<h2>Best photos</h2>'),('▶&nbsp; Слайд-шоу с музыкой','▶&nbsp; Slideshow with music'),
 ('<span class="eyebrow">Карта</span><h2>Где мы побывали</h2>','<span class="eyebrow">Map</span><h2>Where we have been</h2>'),
 ('aria-label="Карта поездок"','aria-label="Map of trips"'),
 ('<span class="eyebrow">Концерты и выходы</span><h2>Наша музыкальная жизнь</h2>','<span class="eyebrow">Concerts and evenings out</span><h2>Our musical life</h2>'),
 ('Новости сайта','Site news'),('Оставьте почту или WhatsApp, и мы напишем, когда появятся новые поездки, фото и концерты.','Leave your e-mail or WhatsApp and we will write when new trips, photos and concerts appear.'),
 ('>Получать новости</a>','>Get the news</a>'),
 ('Ольга и Владимир Фронтон · <a href="../">Наши путешествия по миру</a>','Olga and Vladimir Fronton · <a href="../../en/">Our travels around the world</a>'),
 ('← Назад','← Back'),('aria-label="Фото"','aria-label="Photo"'),('aria-label="Предыдущее фото"','aria-label="Previous photo"'),
 ('aria-label="Следующее фото"','aria-label="Next photo"'),('aria-label="Закрыть"','aria-label="Close"'),('aria-label="Слайд-шоу"','aria-label="Slideshow"'),
 ('aria-label="Предыдущее"','aria-label="Previous"'),('aria-label="Пауза"','aria-label="Pause"'),('aria-label="Следующее"','aria-label="Next"'),('aria-label="Музыка"','aria-label="Music"'),
 ("'поездок'],[nv,'фильмов'],[D.concerts.length,'концертов']","'trips'],[nv,'films'],[D.concerts.length,'concerts']"),("[[np,'фото']]","[[np,'photos']]"),
 ("{jer:'Иерусалим',ta:'Тель-Авив и Яффо',north:'Север',center:'Центр',south:'Юг',guests:'С гостями'}","{jer:'Jerusalem',ta:'Tel Aviv & Jaffa',north:'North',center:'Centre',south:'South',guests:'With guests'}"),
 ("(ts.length==1?'поездка':ts.length<5?'поездки':'поездок')","(ts.length==1?'trip':'trips')"),
 ("f.title='Видео'","f.title='Video'"),("'▶  Смотреть'","'▶  Watch'"),
 ("'▶  Слайд-шоу с музыкой · '+G.length+' фото'","'▶  Slideshow with music · '+G.length+' photos'"),
 ("p:'Концерт'","p:'Concert'"),("textContent='Концерты и выходы'","textContent='Concerts and evenings out'"),
 ("sPlay?'Пауза':'Продолжить'","sPlay?'Pause':'Resume'"),("' кадров из наших поездок'","' shots from our trips'"),
 ("'music/israel_loop.webm':'music/israel_loop.mp4'","'../music/israel_loop.webm':'../music/israel_loop.mp4'"),
 ('aria-label="Районы"','aria-label="Regions"'),("'Районы'","'Regions'")]
eh=open(os.path.join(D,'template_il.html'),encoding='utf8').read()
for a,b in UI:
    if a not in eh:
        if 'Районы' in a: continue
        raise SystemExit('israel EN: UI string not found in template: '+a)
    eh=eh.replace(a,b)
eh=eh.replace('__DATA__',json.dumps(ed,ensure_ascii=False)).replace('__OG__',og)
left=sorted(set(re.findall(r'[А-Яа-яЁё][А-Яа-яЁё \-]*',eh))-{'Русская версия'})
if left: print('israel EN: untranslated fragments:',left[:30])
os.makedirs(os.path.join(OUT,'en'),exist_ok=True)
open(os.path.join(OUT,'en','index.html'),'w',encoding='utf8').write(eh)
print('israel EN: ok')

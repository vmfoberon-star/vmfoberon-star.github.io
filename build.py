import json, data
from blurbs import BLURBS
o=json.load(open('imgs.json'))
C={"toscana26":["Италия"],"uk26":["Великобритания","Ирландия"],"prague25":["Чехия"],"austria25":["Австрия"],"rome25":["Италия"],
"spain23":["Испания"],"napoli23":["Италия"],"azores22":["Португалия"],"portugal22":["Португалия"],"apulia21":["Италия"],"china19":["Китай"],
"france18":["Франция"],"greece18":["Греция"],"norway17":["Норвегия"],"italy16":["Италия"],"swiss16":["Швейцария","Франция"],"denmark14":["Дания"],"barcelona":["Испания"]}
cover_override={"denmark14":"46-W33OMB-E"}
trips=[]
for slug,code,title,place,year,lst,cover,eps in data.TRIPS:
    cover=cover_override.get(slug,cover)
    trips.append(dict(slug=slug,title=title,place=place or C[slug][0],year=year,list=lst,cover=cover,eps=eps,
        country=" и ".join(C[slug]),countries=C[slug]))
for t in trips: t["blurb"]=BLURBS[t["slug"]]
import base64,io,os
from PIL import Image
from photos2003 import SLIDES as S03
from photos2006 import SLIDES as S06
import shutil
shutil.rmtree('site',ignore_errors=True); os.makedirs('site/data'); os.makedirs('site/music')
def enc(path,maxs=1280,q=62):
    im=Image.open(path).convert('RGB'); im.thumbnail((maxs,maxs)); b=io.BytesIO(); im.save(b,'WEBP',quality=q,method=6)
    return 'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
PHOTO_SETS={}   # slug -> {id: dataurl}
PHOTO_SETS['italy03']={k:enc(f'photos2003/{k}.webp') for k,_,_ in S03}
PHOTO_SETS['paris06']={k:enc(f'photos2006/{k}.webp',1200,60) for k,_,_ in S06}
EXTRA_TRIPS=[]
if os.path.exists('trip2008.py'):
    import trip2008
    PHOTO_SETS['alps08']=trip2008.photos(enc); EXTRA_TRIPS.append(trip2008.TRIP)
HAVE12=os.path.exists('photos2012') and len(os.listdir('photos2012'))>=150
if HAVE12:
    import trip2012
    PHOTO_SETS['benelux12']=trip2012.photos(enc)
HAVE11=os.path.exists('photos2011') and len(os.listdir('photos2011'))>=100
if HAVE11:
    import trip2011
    PHOTO_SETS['uk11']=trip2011.photos(enc)
HAVE13ES=os.path.exists('photos2013es')
if HAVE13ES:
    import trip2013es
    PHOTO_SETS['spain13']=trip2013es.photos(enc)
HAVE13=os.path.exists('photos2013')
if HAVE13:
    import trip2013
    PHOTO_SETS['vienna13']=trip2013.photos(enc)
COVERS_EXTRA={'p:italy03':enc('photos2003/rome_02.webp',1280,66),'p:paris06':enc('photos2006/paris_06.webp',1280,66)}
if EXTRA_TRIPS: COVERS_EXTRA['p:alps08']=enc(trip2008.COVER,1280,66)
if HAVE13ES: COVERS_EXTRA['p:spain13']=enc(trip2013es.COVER,1280,66)
if HAVE13: COVERS_EXTRA['p:vienna13']=enc(trip2013.COVER,1280,66)
if HAVE11: COVERS_EXTRA['p:uk11']=enc(trip2011.COVER,1280,66)
if HAVE12: COVERS_EXTRA['p:benelux12']=enc(trip2012.COVER,1280,66)
def mus(name):
    shutil.copy(f'music/{name}.webm',f'site/music/{name}.webm'); shutil.copy(f'music/{name}.m4a',f'site/music/{name}.mp4')
    return {'webm':f'music/{name}.webm','m4a':f'music/{name}.mp4'}
MUSIC={'italia':mus('italia_loop'),'paris':mus('paris_loop')}
if os.path.exists('music/alps_loop.webm'): MUSIC['alps']=mus('alps_loop')
if os.path.exists('music/london_loop.webm'): MUSIC['london']=mus('london_loop')
if os.path.exists('music/benelux_loop.webm'): MUSIC['benelux']=mus('benelux_loop')
if os.path.exists('music/vienna_loop.webm'): MUSIC['vienna']=mus('vienna_loop')
if os.path.exists('music/spain_loop.webm'): MUSIC['spain']=mus('spain_loop')
italy03=dict(slug='italy03',title='Рим и Флоренция',place='Италия · август 2003',year='2003',list='',cover='p:italy03',eps=[],
  country='Италия',countries=['Италия'],slides=[list(x) for x in S03],music='italia',
  chapters=[dict(name='Рим',date='август 2003',n=51,note='Купол собора Святого Петра и Ватиканские сады, площадь Навона, Пантеон, фонтан Треви, Капитолий, Форум и Колизей.'),
            dict(name='Флоренция',date='август 2003',n=13,note='Собор Санта-Мария-дель-Фьоре, Баптистерий, Палаццо Веккьо и площадь Синьории.')],
  blurb='С этой поездки всё началось. Рим от купола собора Святого Петра и Ватиканских садов через площадь Навона, Пантеон и фонтан Треви к Капитолию, Форуму и Колизею, а потом Флоренция: собор Санта-Мария-дель-Фьоре, Баптистерий, Палаццо Веккьо и площадь Синьории.')
paris06=dict(slug='paris06',title='Париж',place='Франция · 11–16 октября 2006',year='2006',list='',cover='p:paris06',eps=[],
  country='Франция',countries=['Франция'],slides=[list(x) for x in S06],music='paris',
  blurb='Октябрьская неделя в Париже. Триумфальная арка днём и вечером, мост Александра III и Дом инвалидов, Нотр-Дам, Лувр с Никой Самофракийской, Тюильри и музей Орсе. А ещё Латинский квартал и Сорбонна, Люксембургский сад, художники Монмартра и в конце Опера Гарнье.')
bi=[i for i,t in enumerate(trips) if t['slug']=='barcelona'][0]
trips.insert(bi,paris06); trips.insert(bi+1,italy03)
for et in EXTRA_TRIPS:
    j=[i for i,t in enumerate(trips) if t['slug']=='paris06'][0]; trips.insert(j,et)
if HAVE13:
    j=[i for i,t in enumerate(trips) if t['slug']=='denmark14'][0]; trips.insert(j+1,trip2013.TRIP)
if HAVE13ES:
    j=[i for i,t in enumerate(trips) if t['slug']=='denmark14'][0]; trips.insert(j+1,trip2013es.TRIP)
if HAVE12:
    j=[i for i,t in enumerate(trips) if t['slug']=='denmark14'][0]; trips.insert(j+1,trip2012.TRIP)
if HAVE11:
    j=[i for i,t in enumerate(trips) if t['slug']=='denmark14'][0]; trips.insert(j+1,trip2011.TRIP)
_ord=['spain13','vienna13','benelux12','uk11']
_sub=[t for t in trips if t['slug'] in _ord]; _sub.sort(key=lambda t:_ord.index(t['slug']))
_j=[i for i,t in enumerate(trips) if t['slug']=='denmark14'][0]
trips=[t for t in trips if t['slug'] not in _ord]; trips[_j+1:_j+1]=_sub
os.makedirs('site/photos',exist_ok=True)
PHOTOS={}  # slug -> list of bundle files
for slug,ph in PHOTO_SETS.items():
    chunks=[{}];size=0
    for k,du in ph.items():
        if size>3_000_000: chunks.append({});size=0
        chunks[-1][k]=du; size+=len(du)
    PHOTOS[slug]=[]
    for ci,c in enumerate(chunks):
        fn=f'photos/{slug}-{ci}.json'; json.dump(c,open('site/'+fn,'w'),separators=(',',':')); PHOTOS[slug].append(fn)
covers={t["cover"]:o["covers"][t["cover"]] for t in trips if t["cover"] in o["covers"]}
covers.update(COVERS_EXTRA)
for v in ["sRH4EahgCnA","cIyQY-rwktE","nGdI9Q1nAy8","fym5_-XKHbY","G-meRAm9ffE"]: covers[v]=o["covers"][v]
NEWC={'azores22':'covers_new/azores22.webp','portugal22':'covers_new/portugal22.webp','greece18':'covers_new/greece18.webp'}
for t in trips:
    if t['slug'] in NEWC: k='n:'+t['slug']; covers[k]=enc(NEWC[t['slug']],1280,70); t['cover']=k
GEO={'toscana26':[43.32,11.33],'uk26':[53.6,-3.5],'prague25':[50.08,14.42],'austria25':[47.7,13.6],'rome25':[41.9,12.5],
 'spain23':[37.39,-5.98],'napoli23':[40.85,14.27],'azores22':[37.78,-25.5],'portugal22':[40.2,-8.4],'apulia21':[40.78,17.24],
 'china19':[39.9,116.4],'france18':[48.85,-1.6],'greece18':[37.98,23.73],'norway17':[60.9,6.8],'italy16':[45.44,10.99],
 'swiss16':[46.45,6.6],'denmark14':[55.68,12.57],'barcelona':[41.39,2.17],'vienna13':[48.21,16.37],'benelux12':[50.95,4.2],
 'uk11':[51.51,-0.13],'spain13':[40.42,-3.70],'alps08':[47.4,9.6],'paris06':[48.86,2.35],'italy03':[42.6,11.9]}
for t in trips: t['geo']=GEO[t['slug']]
from routes import ROUTES
for t in trips:
    if t['slug'] in ROUTES: t['route']=ROUTES[t['slug']]
# YouTube playlists for the photo trips (Full HD slideshow videos) + the Spain 2013 video films
PL5={'italy03':'PLbBMuoRQC-y4','paris06':'PLb-leMkKoPAo','alps08':'PLGR_8S6ZuCoA','uk11':'PLNz4zoSzDyh8',
     'benelux12':'PLITF_0o2LqJw','spain13':'PLMKGApVJIDDc','vienna13':'PLNrcg5RxD_TI'}
SP13FILMS=[['pMQgKpoxU5w','Гран-Виа и площадь Испании','1:40'],['BkHdwLjpabs','Сибелес и «Метрополис»','1:51'],
           ['KAy6eww_o0c','Площадь Колумба и Кастельяна','1:47'],['s0EL6mjh3mc','Стены Авилы','1:44']]
for t in trips:
    if t['slug'] in PL5: t['list']=PL5[t['slug']]
    if t['slug']=='spain13': t['eps']=SP13FILMS
import re as _re
os.makedirs('site/img/c',exist_ok=True)
CPATH={}
for k,du in covers.items():
    fn='img/c/'+_re.sub(r'[^A-Za-z0-9_-]','_',k)+'.webp'; open('site/'+fn,'wb').write(base64.b64decode(du.split(',',1)[1])); CPATH[k]=fn
covers_data=covers; covers=CPATH
thumbs={k:v for k,v in o["eps"].items() if v}
for i,e in enumerate(SP13FILMS): thumbs[e[0]]='data:image/webp;base64,'+base64.b64encode(open(f'vid13thumbs/{i+1}.webp','rb').read()).decode()
json.dump(thumbs,open('site/data/thumbs.json','w'))
html=open('template2.html').read()
html=html.replace('__DATA__',json.dumps(trips,ensure_ascii=False)).replace('__COVERS__',json.dumps(covers)).replace('__MUSIC__',json.dumps(MUSIC)).replace('__PHOTOS__',json.dumps(PHOTOS))
html=html.replace("const countries=new Set(TRIPS.map(t=>t.country)).size;","const countries=new Set(TRIPS.flatMap(t=>t.countries)).size;")
open('travel.html','w').write(html)
import webextra; webextra.make(trips,covers_data,html)
print(len(html)/1e6,'MB page');import subprocess;print(subprocess.run(['du','-sh','site'],capture_output=True,text=True).stdout)
import runpy; runpy.run_path('en/build_en.py')

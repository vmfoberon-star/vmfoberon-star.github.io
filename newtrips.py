# Photo trips built from Google Photos albums (slides = gallery photos in photosgal/<slug>/)
from gallery import GAL
META={
 'budapest17':dict(title='Будапешт',place='Венгрия · апрель–май 2017',year='2017',country='Венгрия',countries=['Венгрия'],
   blurb='Весенний Будапешт. Буда с Рыбацким бастионом и церковью Матьяша, Королевский дворец и виды на Дунай, Парламент и Цепной мост, а вечером прогулка на кораблике по реке среди огней.',cover=8),
 'rhodes19':dict(title='Родос и Сими',place='Греция · апрель 2019',year='2019',country='Греция',countries=['Греция'],
   blurb='Апрель на Родосе. Дворец великих магистров и улица Рыцарей, старый город и гавань Мандраки, день на разноцветном острове Сими, а потом на машине вокруг острова: бухта Энтони Куина, Цамбика, белый Линдос и замок Монолитос.',cover=26),
 'sf10':dict(title='Ольга в Сан-Франциско',place='США · декабрь 2010',year='2010',country='США',countries=['США'],
   blurb='Декабрь 2010 года: Ольга в Сан-Франциско. Мост Золотые Ворота, «Расписные леди» и канатный трамвай, тропа над Тихим океаном и гигантские секвойи в лесу Мьюир-Вудс.',cover=0),
}
TRIPS=[]
for s,m in META.items():
    g=GAL[s]; sl=[list(x) for x in g['slides']]
    TRIPS.append(dict(slug=s,title=m['title'],place=m['place'],year=m['year'],list='',cover='p:'+s,eps=[],country=m['country'],
        countries=m['countries'],slides=sl,music=g['music'],blurb=m['blurb']))
def photos(enc,s): return {x[0]:enc(f'photosgal/{s}/{x[0]}.webp',1280,66) for x in GAL[s]['slides']}
def cover(s): return f"photosgal/{s}/{GAL[s]['slides'][META[s]['cover']][0]}.webp"

# English version of the site: translate trip data + interface, write site/en/index.html and site/en/t/<slug>/ share pages.
import json, re, os, sys, html as H
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = {}
for m in ['tr1', 'tr2', 'tr3']: D.update(__import__(m).D)
if os.path.exists(os.path.join(os.path.dirname(__file__), 'tr_auto.py')): D.update(__import__('tr_auto').D)
import webextra

def tr(s):
    if not s: return s
    if s not in D: raise KeyError(s)
    return D[s]

page = open('travel.html').read()
i = page.index('const TRIPS=') + 12
trips, end = json.JSONDecoder().raw_decode(page[i:])
for t in trips:
    for k in ['title', 'place', 'country', 'blurb']:
        if t.get(k): t[k] = tr(t[k])
    t['eps'] = [[e[0], tr(e[1]), e[2]] for e in t['eps']]
    for c in t.get('chapters') or []:
        for k in ['name', 'date', 'note']:
            if c.get(k): c[k] = tr(c[k])
    if t.get('slides'): t['slides'] = [[s[0], tr(s[1]), tr(s[2])] + list(s[3:]) for s in t['slides']]
page = page[:i] + json.dumps(trips, ensure_ascii=False) + page[i + end:]

j = page.index('const BEST=') + 11
best, bend = json.JSONDecoder().raw_decode(page[j:])
best['title'] = 'Best shots'
best['place'] = 'The best photos from our trips, 2003–2026'
best['slides'] = [[s[0], tr(s[1]), tr(s[2])] + list(s[3:]) for s in best['slides']]
page = page[:j] + json.dumps(best, ensure_ascii=False) + page[j + bend:]
# assets live one level up
page = re.sub(r'"(img/c/|photos/|music/)', r'"../\1', page)
page = page.replace("fetch('data/thumbs.json')", "fetch('../data/thumbs.json')")

UI = [
 ('<title>Наши путешествия</title>', '<title>Our Travels</title>'),
 ('const RT_LANG=0;', 'const RT_LANG=1;'),
 ('aria-label="На главную страницу">← На главную</button>', 'aria-label="Back to the home page">← Home</button>'),
 ('aria-label="Назад на 10 секунд" title="Назад на 10 секунд"', 'aria-label="Back 10 seconds" title="Back 10 seconds"'),
 ('aria-label="Вперёд на 10 секунд" title="Вперёд на 10 секунд"', 'aria-label="Forward 10 seconds" title="Forward 10 seconds"'),
 ('aria-label="Перемотка"', 'aria-label="Seek"'),
 ('`${fmtT(sIdx*SLIDE_MS)} из ${fmtT(n*SLIDE_MS)}`', '`${fmtT(sIdx*SLIDE_MS)} of ${fmtT(n*SLIDE_MS)}`'),
 ('title="Отправить ссылку на «Лучшие кадры»">⤴ Отправить<', 'title="Send a link to the best shots">⤴ Send<'),
 ('<div class="eyebrow">Отправить ссылку</div>\n    <h2 id="spT">Лучшие кадры</h2>', '<div class="eyebrow">Send a link</div>\n    <h2 id="spT">Best shots</h2>'),
 ('Получатель откроет ссылку и нажмёт «Смотреть» — слайд-шоу пойдёт с музыкой.', 'They open the link and press “Watch” — the slideshow plays with music.'),
 ('id="spCopy">Скопировать<', 'id="spCopy">Copy<'), ('id="spMail">Почта<', 'id="spMail">Email<'), ('id="spMore" hidden>Другое…<', 'id="spMore" hidden>More…<'),
 ('aria-label="Поделиться" title="Поделиться"', 'aria-label="Share" title="Share"'), ('id="showEndShare" hidden>Поделиться<', 'id="showEndShare" hidden>Share<'),
 ('<div class="eyebrow">Ольга и Владимир Фронтон</div><h2 id="bestSplashT">Лучшие кадры</h2>', '<div class="eyebrow">Olga and Vladimir Fronton</div><h2 id="bestSplashT">Best shots</h2>'),
 ('>▶ Смотреть</button><a class="btn ghost" href="#" id="bestSplashSite">Весь сайт</a>', '>▶ Watch</button><a class="btn ghost" href="#" id="bestSplashSite">The whole site</a>'),
 ("BEST.slides.length+' фото'", "BEST.slides.length+' photos'"),
 ('>★ Лучшие кадры<', '>★ Best shots<'), ("toast('Не удалось загрузить фото')", "toast('Could not load the photos')"),
 ('/полный фильм|вариант|Короткий клип|фрагмент/i', '/full film|alternate cut|short clip|excerpt/i'),
 ('<h2 id="statsTitle">Наши путешествия в цифрах</h2>', '<h2 id="statsTitle">Our travels in numbers</h2>'),
 ('Расстояния по прямой между городами, с перелётами из дома', 'Straight-line distances between places, including flights from home'),
 ('Все маршруты на одной карте. Нажмите на линию или точку, чтобы узнать поездку.', 'All the routes on one map. Tap a line or a dot to see the trip.'),
 ('<h2 id="tlTitle">Лента времени</h2>', '<h2 id="tlTitle">Timeline</h2>'),
 ("toLocaleString('ru-RU')", "toLocaleString('en-GB')"),
 ("[nf(km),'километров','≈ '+earth.toFixed(1).replace('.',',')+' раза вокруг Земли']", "[nf(km),'kilometres','≈ '+earth.toFixed(1)+' times around the Earth']"),
 ("[nf(Math.round(route)),'км по маршрутам','на машине, автобусе, поезде']", "[nf(Math.round(route)),'km along the routes','by car, coach and train']"),
 ("`с ${y0} по ${y1} год`", "`from ${y0} to ${y1}`"),
 ("W(cities.size,'город и место','города и места','городов и мест'),'отмечено на маршрутах'", "W(cities.size,'town or place','towns and places','towns and places'),'marked on the routes'"),
 ("'вместе со слайд-шоу'", "'including the slideshows'"), ("[photos,'фото','в слайд-шоу']", "[photos,'photos','in the slideshows']"),
 ("'видео: '+fmt(filmsSec)+' фильмов'", "'of video: '+fmt(filmsSec)+' of films'"),
 (">Открыть →</a>`", ">Open →</a>`"), ("bindTooltip('Модиин')", "bindTooltip('Modiin')"),
 ("${y-prev-1===1?'год':pl(y-prev-1,'год','года','лет')} без больших поездок на сайте", "${y-prev-1===1?'A year':pl(y-prev-1,'year','years','years')} without big trips on the site"),
 ('<a href="#stats">Цифры</a><a href="#timeline">Лента</a>', '<a href="#stats">Numbers</a><a href="#timeline">Timeline</a>'),

 ('📺 На телевизоре', '📺 On the TV'), ('<div class="eyebrow">Режим для телевизора</div>', '<div class="eyebrow">TV mode</div>'),
 ('<h2 id="tvH">Смотреть всё подряд</h2>', '<h2 id="tvH">Watch everything</h2>'),
 ('Все слайд-шоу и фильмы по очереди, на весь экран, с заставкой перед каждой поездкой. Удобно включить на телевизоре или большом мониторе и смотреть всей семьёй.',
  'All the slideshows and films one after another, full screen, with a title card before each trip. Put it on the TV or a big monitor and watch together with the family.'),
 ('aria-label="Что показывать"', 'aria-label="What to show"'), ('aria-label="Порядок"', 'aria-label="Order"'),
 ('<span>Всё<small', '<span>Everything<small'), ('<span>Только слайд-шоу<small', '<span>Slideshows only<small'), ('<span>Только фильмы<small', '<span>Films only<small'),
 ('<span>С 2003 года</span>', '<span>From 2003</span>'), ('<span>С новых поездок</span>', '<span>Newest first</span>'),
 ('>▶ Начать показ<', '>▶ Start the show<'),
 ('Во время показа: <b>→</b> — дальше, <b>Esc</b> — выход. С телефона можно вывести на телевизор через «Повтор экрана» (AirPlay) или Chromecast.',
  'During the show: <b>→</b> skips ahead, <b>Esc</b> exits. From a phone you can put it on the TV with Screen Mirroring (AirPlay) or Chromecast.'),
 ("`${it.t.slides.length} фото`", "`${it.t.slides.length} photos`"), ("toast('Показ закончен')", "toast('The show is over')"),
 ("return h?`${h} ч ${m} мин`:`${m} мин`};\n  $('#tvAllInfo')", "return h?`${h} h ${m} min`:`${m} min`};\n  $('#tvAllInfo')"),

 ("Маршрут · ${uniq.length} ${W(uniq.length,'место','места','мест')}", "Route · ${uniq.length} ${W(uniq.length,'place','places','places')}"),
 ("r.order===false?'Где мы были':'Наш маршрут'", "r.order===false?'Where we went':'Our route'"),
 ('<a class="brand" href="#top">Наши путешествия</a>', '<a class="brand" href="#top">Our Travels</a>'),
 ('aria-label="Годы"', 'aria-label="Years"'),
 ('<a class="lang" id="langLink" href="en/" hreflang="en" lang="en" title="English version">EN</a>',
  '<a class="lang" id="langLink" href="../" hreflang="ru" lang="ru" title="Русская версия">RU</a>'),
 ('Ольга и Владимир Фронтон · путешествия с 2003 года', 'Olga and Vladimir Fronton · travelling since 2003'),
 ('<h1>Наши путешествия</h1>', '<h1>Our Travels</h1>'),
 ('Фильмы и фотографии из наших поездок: соборы и рынки, горы и фьорды, концерты и уличные праздники.',
  'Films and photos from our trips: cathedrals and markets, mountains and fjords, concerts and street festivals.'),
 ('>Смотреть Тоскану<', '>Watch Tuscany<'),
 ('>Все поездки<', '>All trips<'),
 ('<a class="btn ghost" href="#about">О нас</a>', '<a class="btn ghost" href="#about">About us</a>'),
 ('alt="Ольга и Владимир Фронтон на холме над Афинами"><figcaption>Афины, 2018</figcaption>',
  'alt="Olga and Vladimir Fronton on a hill above Athens"><figcaption>Athens, 2018</figcaption>'),
 ('<div class="eyebrow">О нас</div>', '<div class="eyebrow">About us</div>'),
 ('<h2 id="aboutTitle">Ольга и Владимир Фронтон</h2>', '<h2 id="aboutTitle">Olga and Vladimir Fronton</h2>'),
 ('Мы вместе уже 50 лет: двадцать пять из них прожили в России, двадцать пять в Израиле. У нас двое детей и пятеро внуков.',
  'We have been together for 50 years: twenty-five of them in Russia and twenty-five in Israel. We have two children and five grandchildren.'),
 ('Путешествуем сами, сами снимаем и сами монтируем каждый фильм. Этот сайт собирает их в одном месте.',
  'We travel on our own, and we shoot and edit every film ourselves. This site brings them all together in one place.'),
 ('<dd>лет вместе</dd>', '<dd>years together</dd>'), ('<dd>детей</dd>', '<dd>children</dd>'), ('<dd>внуков</dd>', '<dd>grandchildren</dd>'),
 ('aria-label="Последнее путешествие"', 'aria-label="Latest trip"'),
 ('>Карта поездок<', '>Map of our trips<'), ('>Нажмите на точку, чтобы открыть поездку<', '>Tap a dot to open a trip<'),
 ('>Загружаем карту…<', '>Loading the map…<'),
 ('></i>фильмы</span>', '></i>films</span>'), ('></i>слайд-шоу с фото</span>', '></i>photo slideshows</span>'), ('></i>дом, Модиин</span>', '></i>home, Modiin</span>'),
 ('Фильмы снимают и монтируют Ольга и Владимир Фронтон. Видео хранятся на YouTube.', 'Films shot and edited by Olga and Vladimir Fronton. Videos are hosted on YouTube.'),
 ('aria-label="Закрыть"', 'aria-label="Close"'), ('aria-label="Слайд-шоу"', 'aria-label="Slideshow"'),
 ('aria-label="Предыдущее фото"', 'aria-label="Previous photo"'), ('aria-label="Пауза"', 'aria-label="Pause"'),
 ('aria-label="Следующее фото"', 'aria-label="Next photo"'), ('aria-label="Выключить музыку"', 'aria-label="Mute music"'),
 ('aria-label="Закрыть слайд-шоу"', 'aria-label="Close slideshow"'), ('<div class="eyebrow">Конец</div>', '<div class="eyebrow">The end</div>'),
 ('>Смотреть ещё раз<', '>Watch again<'), ('aria-label="Закрыть видео"', 'aria-label="Close video"'),
 ('>‹ Предыдущий<', '>‹ Previous<'), ('>Следующий ›<', '>Next ›<'), ('>Открыть на YouTube<', '>Open on YouTube<'),
 ("return h?`${h} ч ${m} мин`:`${m} мин`", "return h?`${h} h ${m} min`:`${m} min`"),
 ("const pl=(n,a,b,c)=>{const t=n%10,h=n%100;return n+' '+(t==1&&h!=11?a:t>=2&&t<=4&&(h<10||h>=20)?b:c)};", "const pl=(n,a,b,c)=>n+' '+(n==1?a:c);"),
 ("'фильм','фильма','фильмов'", "'film','films','films'"), ("'поездка','поездки','поездок'", "'trip','trips','trips'"),
 ("'страна','страны','стран'", "'country','countries','countries'"), ("'глава','главы','глав'", "'chapter','chapters','chapters'"),
 ("'час','часа','часов'", "'hour','hours','hours'"),
 ("фото · слайд-шоу с музыкой", "photos · slideshow with music"),
 ("s[1].startsWith('Рим')", "s[1].startsWith('Rome')"),
 ("<b>${photos}</b>фото</span>", "<b>${photos}</b>photos</span>"), ("· ${photos} фото`", "· ${photos} photos`"),
 ('aria-label="Открыть: ${esc(latest.title)}"', 'aria-label="Open: ${esc(latest.title)}"'),
 ('<div class="eyebrow">Последнее путешествие · ${latest.year}</div>', '<div class="eyebrow">Latest trip · ${latest.year}</div>'),
 ('>Открыть фильмы</a>', '>Open the films</a>'), ("t.year||'Без даты'", "t.year||'Undated'"),
 ('<a href="#map">Карта</a>', '<a href="#map">Map</a>'), ('<em>Смотреть →</em>', '<em>Watch →</em>'),
 ('>▶ Смотреть подряд</button>', '>▶ Play all</button>'), ('>Плейлист на YouTube</a>', '>YouTube playlist</a>'),
 ('data-share>Поделиться</button>', 'data-share>Share</button>'), ('${t.title} — наши путешествия', '${t.title} — Our Travels'),
 ("toast('Ссылка скопирована')", "toast('Link copied')"), ("prompt('Скопируйте ссылку:',url)", "prompt('Copy the link:',url)"),
 ('aria-label="Слайд-шоу с фото: ${esc(sl[2])}"', 'aria-label="Photo slideshow: ${esc(sl[2])}"'),
 ("join(' · ')} · фотографии</div>", "join(' · ')} · photos</div>"),
 ("<span><b>${t.slides.length}</b>фото</span>", "<span><b>${t.slides.length}</b>photos</span>"),
 ("</b>мин с музыкой</span>", "</b>min with music</span>"),
 (">▶ Смотреть ${nCh?'всё подряд':'слайд-шоу'}</button>", ">▶ ${nCh?'Play everything':'Play slideshow'}</button>"),
 ('<div class="eyebrow">Глава ${ci+1} · ${esc(c.date)}</div>', '<div class="eyebrow">Chapter ${ci+1} · ${esc(c.date)}</div>'),
 ('>▶ Смотреть главу · ${c.n} фото</button>', '>▶ Play chapter · ${c.n} photos</button>'),
 ('<div class="eyebrow">Видео · ', '<div class="eyebrow">Video · '), ('<h3>Снято на видеокамеру</h3><p>Короткие фильмы из наших видеозаписей этой поездки.</p>', '<h3>Shot on video</h3><p>Short films made from our video footage of this trip.</p>'),
 ('>▶ Смотреть фильмы</button>', '>▶ Play the films</button>'),
 ("p?'Пауза':'Продолжить'", "p?'Pause':'Play'"),
 ("'<div class=\"map-msg\">Карта сейчас недоступна</div>'", "'<div class=\"map-msg\">The map is unavailable right now</div>'"),
 ("'Карта: страны, где мы были'", "'Map: the countries we have visited'"), (".text('Модиин')", ".text('Modiin')"),
 ("p.t.slides?'слайд-шоу':", "p.t.slides?'slideshow':"), ('>Открыть →</button>', '>Open →</button>'),
 ("`${visited.size} стран · ${TRIPS.length} поездок. ${coarse?'Нажмите':'Наведите'} на точку`", "`${visited.size} countries · ${TRIPS.length} trips. ${coarse?'Tap':'Hover over'} a dot`"),
]
for a, b in UI:
    n = page.count(a)
    if n == 0: print('UI MISSING:', a[:90])
    page = page.replace(a, b)
# share links from the English page point at English share pages
page = page.replace('`${location.origin}/t/${slug}/`', '`${location.origin}/en/t/${slug}/`')
left = sorted(set(re.findall(r'[А-Яа-яЁё][А-Яа-яЁё ,.:!?«»—-]*', page[:page.index('const TRIPS=')] + page[page.index('</script>', page.index('const TRIPS=')):])))
print('Cyrillic left outside data:', left[:40])
page = page.replace('<html lang="ru">', '<html lang="en">')

# standalone page + share pages (re-using the Russian site's head builder)
B = webextra.BASE
HEAD = webextra.HEAD.replace('lang="ru"', 'lang="en"').replace('content="ru_RU"', 'content="en_GB"').replace('content="Наши путешествия"', 'content="Our Travels"')
alt = '<link rel="alternate" hreflang="ru" href="{b}/{p}">\n<link rel="alternate" hreflang="en" href="{b}/en/{p}">\n'
os.makedirs('site/en', exist_ok=True)
# English share-preview images
from PIL import Image as _I
os.makedirs('site/og/en', exist_ok=True)
_ci = page.index('COVERS=') + 7
COV, _ = json.JSONDecoder().raw_decode(page[_ci:])
def _cov(k):
    p = COV.get(k)
    return _I.open('site/' + p.replace('../', '', 1)).convert('RGB') if p else None
EN_LABEL = 'OLGA AND VLADIMIR FRONTON'
webextra.og_image(_cov('sRH4EahgCnA'), 'Our Travels', f'{len(trips)} trips since 2003 · films and slideshows', 'site/og/en/site.jpg', EN_LABEL)
for t in trips:
    im = _cov(t['cover'])
    if im: webextra.og_image(im, t['title'], t['place'], f"site/og/en/{t['slug']}.jpg", EN_LABEL)

body = page.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
k = body.index('</style>') + len('</style>')
head = HEAD.format(desc=H.escape('Films and photo slideshows from our trips since 2003. We travel, film and edit everything ourselves.'),
                   title='Our Travels — Olga and Vladimir Fronton', url=B + '/en/', img=B + '/og/en/site.jpg', root='../') + alt.format(b=B, p='')
open('site/en/index.html', 'w').write(head + body[:k] + '\n</head>\n<body>\n' + body[k:] + '\n</body>\n</html>\n')
for t in trips:
    slug = t['slug']; os.makedirs(f'site/en/t/{slug}', exist_ok=True)
    desc = t['blurb'][:180].rsplit(' ', 1)[0] + '…' if len(t['blurb']) > 180 else t['blurb']
    img = f'{B}/og/en/{slug}.jpg' if os.path.exists(f'site/og/en/{slug}.jpg') else B + '/og/en/site.jpg'
    hd = HEAD.format(desc=H.escape(desc), title=H.escape(f"{t['title']} — Our Travels"), url=f'{B}/en/t/{slug}/', img=img, root='../../../')
    open(f'site/en/t/{slug}/index.html', 'w').write(hd + f'''<title>{H.escape(t['title'])} — Our Travels</title>
<meta http-equiv="refresh" content="0; url=../../#{slug}">
<script>location.replace('../../#{slug}')</script>
<style>body{{background:#0D0E10;color:#EEEAE2;font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#E2B04A}}</style>
</head><body><p><a href="../../#{slug}">{H.escape(t['title'])} →</a></p></body></html>
''')
print('en pages:', len(trips))

# share page for the best-shots slideshow (English)
from PIL import Image as _I2
os.makedirs('site/en/t/best', exist_ok=True)
_bimg = 'site/' + COV['p:best'].replace('../', '', 1)
webextra.og_image(_I2.open(_bimg).convert('RGB'), 'Best shots', best['place'], 'site/og/en/best.jpg', EN_LABEL)
_hd = HEAD.format(desc=H.escape(best['place']), title='Best shots — Our Travels', url=f'{B}/en/t/best/', img=f'{B}/og/en/best.jpg', root='../../../')
open('site/en/t/best/index.html', 'w').write(_hd + '''<title>Best shots — Our Travels</title>
<meta http-equiv="refresh" content="0; url=../../#best">
<script>location.replace('../../#best')</script>
<style>body{background:#0D0E10;color:#EEEAE2;font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0}a{color:#E2B04A}</style>
</head><body><p><a href="../../#best">Best shots →</a></p></body></html>
''')

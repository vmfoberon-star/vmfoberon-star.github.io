# Extras for the public website: standalone index.html, share previews (og images + /t/<slug>/ pages), icons.
import os, io, base64, html as H
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = 'https://vmfoberon-star.github.io'
FONTS = '/home/claude/travel/yt/fonts'
F = lambda n, s: ImageFont.truetype(f'{FONTS}/{n}.ttf', s)
GOLD = (226, 176, 74)
SITE_TITLE = 'Наши путешествия — Ольга и Владимир Фронтон'
SITE_DESC = 'Фильмы и слайд-шоу о наших поездках с 2003 года. Сами ездим, сами снимаем и сами монтируем.'


def _img(du):
    return Image.open(io.BytesIO(base64.b64decode(du.split(',', 1)[1]))).convert('RGB')


def _cover_crop(im, W=1200, Hh=630):
    s = max(W / im.width, Hh / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - W) // 2; y = (im.height - Hh) // 2
    return im.crop((x, y, x + W, y + Hh))


def _wrap(d, txt, font, maxw):
    words, lines = txt.split(), ['']
    for w in words:
        t = (lines[-1] + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: lines[-1] = t
        else: lines.append(w)
    return lines


def og_image(im, title, sub, out, label='ОЛЬГА И ВЛАДИМИР ФРОНТОН'):
    im = _cover_crop(im)
    shade = Image.new('L', im.size, 0); sd = ImageDraw.Draw(shade)
    for y in range(im.height):
        k = max(0, (y - im.height * 0.35) / (im.height * 0.65)); sd.line([(0, y), (im.width, y)], fill=int(215 * k ** 1.3))
    im = Image.composite(Image.new('RGB', im.size, (13, 14, 16)), im, shade)
    d = ImageDraw.Draw(im)
    ft = F('cormorant-garamond-500-italic', 84 if len(title) < 22 else 66)
    lines = _wrap(d, title, ft, 1080)[:2]
    y = im.height - 70 - len(lines) * (ft.size + 4)
    d.text((60, y - 46), label, font=F('golos-text-500-normal', 24), fill=GOLD)
    for i, l in enumerate(lines):
        d.text((60, y + i * (ft.size + 4)), l, font=ft, fill=(240, 236, 228))
    d.text((60, im.height - 56), sub, font=F('golos-text-400-normal', 26), fill=(205, 200, 190))
    im.save(out, 'JPEG', quality=84, optimize=True, progressive=True)


def icons():
    for size, name in [(64, 'favicon.png'), (180, 'apple-touch-icon.png'), (512, 'icon-512.png')]:
        S = size * 4
        im = Image.new('RGB', (S, S), (13, 14, 16)); d = ImageDraw.Draw(im)
        d.ellipse((S * .08, S * .08, S * .92, S * .92), outline=GOLD, width=max(4, S // 28))
        f = F('cormorant-garamond-500-italic', int(S * .62))
        d.text((S / 2, S / 2 + S * .02), 'Ф', font=f, fill=GOLD, anchor='mm')
        im.resize((size, size), Image.LANCZOS).save(f'site/{name}')


HEAD = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0D0E10">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Наши путешествия">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{root}favicon.png">
<link rel="apple-touch-icon" href="{root}apple-touch-icon.png">
<link rel="canonical" href="{url}">
'''


def make(trips, covers, page):
    os.makedirs('site/og', exist_ok=True)
    icons()
    # site-wide preview: the hero frame
    og_image(_img(covers['sRH4EahgCnA']), 'Наши путешествия', f'{len(trips)} поездок с 2003 года · фильмы и слайд-шоу', 'site/og/site.jpg')
    # standalone index
    body = page.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    i = body.index('</style>') + len('</style>')
    head = HEAD.format(desc=H.escape(SITE_DESC), title=H.escape(SITE_TITLE), url=BASE + '/', img=BASE + '/og/site.jpg', root='')
    open('site/index.html', 'w').write(head + body[:i] + '\n</head>\n<body>\n' + body[i:] + '\n</body>\n</html>\n')
    # one share page per trip: rich preview, then straight into the trip
    for t in trips:
        slug = t['slug']; os.makedirs(f'site/t/{slug}', exist_ok=True)
        c = covers.get(t['cover'])
        if c: og_image(_img(c), t['title'], t['place'], f'site/og/{slug}.jpg')
        desc = t['blurb'][:180].rsplit(' ', 1)[0] + '…' if len(t['blurb']) > 180 else t['blurb']
        hd = HEAD.format(desc=H.escape(desc), title=H.escape(f"{t['title']} — наши путешествия"), url=f'{BASE}/t/{slug}/',
                         img=f'{BASE}/og/{slug}.jpg' if c else BASE + '/og/site.jpg', root='../../')
        open(f'site/t/{slug}/index.html', 'w').write(hd + f'''<title>{H.escape(t['title'])} — наши путешествия</title>
<meta http-equiv="refresh" content="0; url=../../#{slug}">
<script>location.replace('../../#{slug}')</script>
<style>body{{background:#0D0E10;color:#EEEAE2;font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#E2B04A}}</style>
</head><body><p><a href="../../#{slug}">{H.escape(t['title'])} →</a></p></body></html>
''')

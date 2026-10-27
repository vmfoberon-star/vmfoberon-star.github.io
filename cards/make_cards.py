# Printable 10x15 cm postcards (1800x1200 px @300dpi) with a photo collage and a QR code to the site.
import json, segno, io
from PIL import Image, ImageDraw, ImageFont, ImageOps
items = json.load(open('/tmp/claude-0/-home-claude/54e62534-4242-565a-a911-0fd054055a9e/scratchpad/best_items.json'))
F = lambda n, s: ImageFont.truetype(f'yt/fonts/{n}.ttf', s)
GOLD = (226, 176, 74); INK = (13, 14, 16); PAPER = (238, 234, 226)
W, H = 1800, 1200
def tile(path, w, h):
    im = Image.open(path).convert('RGB'); return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.45))
def qr_img(url, size):
    q = segno.make(url, error='m'); b = io.BytesIO(); q.save(b, kind='png', scale=12, border=2, dark='#0D0E10', light='#FFFFFF')
    return Image.open(io.BytesIO(b.getvalue())).convert('RGB').resize((size, size), Image.NEAREST)
def card(out, url, lines, photos):
    im = Image.new('RGB', (W, H), INK); d = ImageDraw.Draw(im)
    LW = 1050; g = 8; tw, th = (LW - g) // 2, (H - g) // 2
    for k, i in enumerate(photos):
        im.paste(tile(items[i][2], tw, th), ((k % 2) * (tw + g), (k // 2) * (th + g)))
    x0 = LW + 70; y = 120
    d.text((x0, y), lines['eyebrow'], font=F('golos-text-500-normal', 30), fill=GOLD); y += 70
    for l in lines['title']:
        d.text((x0, y), l, font=F('cormorant-garamond-500-italic', 104), fill=PAPER); y += 108
    y += 16
    d.text((x0, y), lines['sub'], font=F('golos-text-400-normal', 31), fill=(205, 200, 190)); y += 72
    q = qr_img(url, 380); pad = 22
    d.rounded_rectangle([x0 - pad, y - pad, x0 + 380 + pad, y + 380 + pad], radius=26, fill=(255, 255, 255))
    im.paste(q, (x0, y)); y += 380 + pad + 40
    d.text((x0, y), lines['hint'], font=F('golos-text-500-normal', 30), fill=PAPER); y += 46
    d.text((x0, y), lines['url'], font=F('golos-text-400-normal', 26), fill=(170, 165, 155))
    im.save(out, quality=95, dpi=(300, 300)); print(out)
P = [0, 216, 521, 721]
card('cards/otkrytka_sajt_ru.jpg', 'https://vmfoberon-star.github.io/',
     dict(eyebrow='ОЛЬГА И ВЛАДИМИР ФРОНТОН', title=['Наши', 'путешествия'], sub='25 поездок · 18 стран · с 2003 года',
          hint='Наведите камеру телефона', url='vmfoberon-star.github.io'), P)
card('cards/postcard_site_en.jpg', 'https://vmfoberon-star.github.io/en/',
     dict(eyebrow='OLGA AND VLADIMIR FRONTON', title=['Our', 'Travels'], sub='25 trips · 18 countries · since 2003',
          hint='Point your phone camera here', url='vmfoberon-star.github.io/en'), P)
card('cards/otkrytka_luchshie_kadry_ru.jpg', 'https://vmfoberon-star.github.io/t/best/',
     dict(eyebrow='ОЛЬГА И ВЛАДИМИР ФРОНТОН', title=['Лучшие', 'кадры'], sub='87 фото из наших поездок · с музыкой',
          hint='Наведите камеру телефона', url='vmfoberon-star.github.io/t/best'), [216, 296, 584, 739])

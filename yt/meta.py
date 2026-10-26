import json,re,sys
sys.path.insert(0,'/home/claude/travel/yt')
from render import TRIPS, groups
PL={'italy03':'5 · 2003 Рим и Флоренция','paris06':'5 · 2006 Париж','alps08':'5 · 2008 Вокруг Альп','uk11':'5 · 2011 Лондон, Виндзор и Оксфорд','benelux12':'5 · 2012 Бельгия, Нидерланды, Люксембург','vienna13':'5 · 2013 Новый год в Вене','spain13':'5 · 2013 Испания'}
out=[]
for slug,pl in PL.items():
    t=TRIPS[slug]; G=groups(t); notes={c['name']:c.get('note','') for c in (t.get('chapters') or [])}
    yr='2003' if slug=='italy03' else t['year']
    base={'uk11':'Лондон 2011','benelux12':'Бенилюкс 2012'}.get(slug) or (t['title'] if yr in t['title'] else f"{t['title']} {yr}")
    for ci,(name,date,sl) in enumerate(G):
        title=f"{base} · {ci+1:02d}. {name}" if len(G)>1 else f"{base} · слайд-шоу"
        title=title.replace('«','').replace('»','')
        fname=re.sub(r'[\\/:*?"<>|]','',title)+'.mp4'
        desc=((f"Глава {ci+1} из {len(G)}: {name}" + (f" ({date})" if date else '') + '.\n' + (notes.get(name,'')+'\n' if notes.get(name) else '') + '\n') if len(G)>1 else '') \
            + t['blurb'] + '\n\nФотографии: ' + ', '.join(s[2] for s in sl[:12]) + ('…' if len(sl)>12 else ('' if sl[min(len(sl),12)-1][2][-1] in '!?.' else '.')) \
            + '\n\nОльга и Владимир Фронтон. Сами ездим, сами снимаем и сами монтируем.\nМузыка оригинальная, написана для этого слайд-шоу.'
        out.append(dict(slug=slug,ci=ci,src=f'{slug}_{ci+1:02d}.mp4',playlist=pl,title=title,file=fname,desc=desc))
json.dump(out,open('/home/claude/travel/yt/meta.json','w'),ensure_ascii=False,indent=1)
print(len(out)); [print(o['playlist'],'|',o['title'],len(o['title'])) for o in out]

# Travel site — build sources

Published site: https://vmfoberon-star.github.io (branch `main` of this repo).
This branch (`src`) holds the build sources. Build: `python3 build.py` → `site/` (Russian at /, English at /en/).

## Weekly update (new YouTube episodes)
Trips made of YouTube films live in `data.py` (slug, code, title, place, year, playlist id, cover, episodes).
1. For each trip in `data.py` with a playlist id, open https://www.youtube.com/playlist?list=<id> and list its videos (id, title, duration).
2. Videos not yet in that trip's episodes are new. Give each a short Russian site title in the style of the existing ones
   ("День 5", "День 5, часть 1", "Флоренция: Уффици"…) and an English translation ("Day 5", "Day 5, part 1", "Florence: the Uffizi").
3. Thumbnail: fetch https://i.ytimg.com/vi/<id>/mqdefault.jpg in the browser and convert to a data: URI (base64); null if impossible.
4. Write new.json `{"<slug>": [[id, ru, en, "m:ss", thumb], ...]}` and run `python3 tools/update_eps.py new.json`
   (needs the `main` branch checked out at ../vmfoberon-star.github.io; it rebuilds, commits and pushes).
5. Commit the changed `data.py`, `imgs.json`, `en/tr_auto.py` back to this `src` branch.
A brand-new "5 · …" playlist that matches no trip is NOT added automatically — report it to the owner.

# Add new YouTube episodes to existing trips, then rebuild + deploy the site.
# usage: python3 tools/update_eps.py new.json [--no-deploy]
# new.json: {"<slug>": [["<videoId>", "<русское название>", "<English title>", "<m:ss>", "<data:image/...;base64 thumbnail or null>"], ...]}
import json, sys, os, pprint, subprocess, shutil
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '.'); import data
new = json.load(open(sys.argv[1]))
trips = [list(t) for t in data.TRIPS]; bysl = {t[0]: t for t in trips}
imgs = json.load(open('imgs.json'))
auto_p = 'en/tr_auto.py'; auto = {}
if os.path.exists(auto_p):
    ns = {}; exec(open(auto_p).read(), ns); auto = ns['D']
added = []
for slug, eps in new.items():
    if slug not in bysl: print('UNKNOWN TRIP', slug); continue
    have = {e[0] for e in bysl[slug][7]}
    for vid, ru, en, dur, thumb in eps:
        if vid in have: continue
        bysl[slug][7].append((vid, ru, dur)); have.add(vid); added.append(f'{slug}: {ru}')
        if en: auto[ru] = en
        if thumb: imgs['eps'][vid] = thumb
if not added: print('nothing new'); sys.exit(0)
with open('data.py', 'w') as f:
    f.write('# Trips: slug, code, title, place line, year, playlist id, cover video, episodes [(video, title, duration)]\nTRIPS = ')
    f.write(pprint.pformat([tuple(t) for t in trips], width=200, sort_dicts=False)); f.write('\n')
json.dump(imgs, open('imgs.json', 'w'))
with open(auto_p, 'w') as f: f.write('D=' + pprint.pformat(auto, width=200) + '\n')
print('added:', *added, sep='\n  ')
subprocess.run([sys.executable, 'build.py'], check=True)
if '--no-deploy' in sys.argv: sys.exit(0)
R = os.environ.get('PAGES_DIR', '../vmfoberon-star.github.io')
subprocess.run(['cp', '-a', 'site/.', R + '/'], check=True)
msg = 'Add new episodes: ' + '; '.join(added)
subprocess.run(['git', '-C', R, 'add', '-A'], check=True)
subprocess.run(['git', '-C', R, 'commit', '-qm', msg + '\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'], check=True)
subprocess.run(['git', '-C', R, 'push', '-q', 'origin', 'main'], check=True)
print('deployed')

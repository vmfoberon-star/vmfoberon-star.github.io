"""Builds the password-protected family site into ../site/family/.
Plain content lives in family/private/ (gitignored). Password: family/private/password.txt
The encrypted backup of private/ is family/private.enc (safe to commit)."""
import os,sys,json,base64,io,tarfile,html,secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
D=os.path.dirname(os.path.abspath(__file__)); P=os.path.join(D,'private')
ITER=310000
def key(pw,salt): return PBKDF2HMAC(hashes.SHA256(),32,salt,ITER).derive(pw.encode())
def enc(pw,data:bytes):
    salt=secrets.token_bytes(16); iv=secrets.token_bytes(12)
    return salt,iv,AESGCM(key(pw,salt)).encrypt(iv,data,None)
def dec(pw,blob):
    salt,iv,ct=blob[:16],blob[16:28],blob[28:]; return AESGCM(key(pw,salt)).decrypt(iv,ct,None)
pwf=os.path.join(P,'password.txt')
if not os.path.exists(P) and os.path.exists(os.path.join(D,'private.enc')):
    pw=os.environ.get('FAMILY_PW') or input('Пароль: ')
    tarfile.open(fileobj=io.BytesIO(dec(pw,open(os.path.join(D,'private.enc'),'rb').read()))).extractall(D)
pw=open(pwf).read().strip()
sys.path.insert(0,P); import chron
e=html.escape
def chronicle():
    out=[]; years=sorted({c[0] for c in chron.C},reverse=True)
    out.append('<nav class="yrs">'+''.join(f'<a href="#y{y}">{y}</a>' for y in years)+'<a href="#yq">?</a></nav>')
    for y in years:
        items=sorted([c for c in chron.C if c[0]==y],key=lambda c:c[1],reverse=True)
        out.append(f'<section class="yr" id="y{y}"><h3>{y}</h3><div class="grid">')
        for _,d,t,v,n in items:
            out.append(f'<button class="vid" data-v="{v}" type="button"><img loading="lazy" alt="" src="https://i.ytimg.com/vi/{v}/mqdefault.jpg"><span class="vt">{e(t)}</span>'+(f'<span class="vn">{e(n)}</span>' if n else '')+'</button>')
        out.append('</div></section>')
    out.append('<section class="yr" id="yq"><h3>Год уточнить</h3><div class="grid">')
    for t,v in chron.UNDATED:
        out.append(f'<button class="vid" data-v="{v}" type="button"><img loading="lazy" alt="" src="https://i.ytimg.com/vi/{v}/mqdefault.jpg"><span class="vt">{e(t)}</span></button>')
    out.append('</div></section>')
    return '\n'.join(out)
inner=open(os.path.join(D,'inner.html'),encoding='utf8').read().replace('__CHRON__',chronicle()).replace('__NVID__',str(len(chron.C)+len(chron.UNDATED)))
salt,iv,ct=enc(pw,inner.encode())
payload=base64.b64encode(salt+iv+ct).decode()
shell=open(os.path.join(D,'shell.html'),encoding='utf8').read().replace('__PAYLOAD__',payload).replace('__ITER__',str(ITER))
os.makedirs(os.path.join(D,'..','site','family'),exist_ok=True)
open(os.path.join(D,'..','site','family','index.html'),'w',encoding='utf8').write(shell)
# encrypted backup of private sources
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w:gz') as t: t.add(P,arcname='private',filter=lambda i: None if '__pycache__' in i.name else i)
s2,i2,c2=enc(pw,b.getvalue()); open(os.path.join(D,'private.enc'),'wb').write(s2+i2+c2)
print('family: ok',len(chron.C),'videos')

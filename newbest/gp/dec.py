import json,sys,base64,os,glob
out=sys.argv[1];os.makedirs(out,exist_ok=True)
f=sys.argv[2] if len(sys.argv)>2 else max(glob.glob('/root/.claude/projects/-home-claude/54e62534-4242-565a-a911-0fd054055a9e/tool-results/mcp-remote-devices-Claude_Browser__javascript_tool-*.txt'),key=os.path.getmtime)
d=json.load(open(f));t=d[0]['text'] if isinstance(d,list) else d
t=t.split('\n\n(captured')[0].strip()
if t.startswith('"'):t=t[1:]
if t.endswith('"'):t=t[:-1]
t=t.replace('\\n','\n')
n=0;nxt=None
for line in t.split('\n'):
    if line.startswith('NEXT:'):nxt=line;continue
    if ':' not in line:continue
    i,b=line.split(':',1)
    try:raw=base64.b64decode(b,validate=False)
    except Exception as e:print('bad',i,e);continue
    if 'truncated' in line:print('TRUNCATED',i);continue
    ext='webp' if raw[8:12]==b'WEBP' else 'jpg'
    open(os.path.join(out,'%03d.%s'%(int(i),ext)),'wb').write(raw);n+=1
print(n,'images ->',out,nxt,os.path.basename(f))

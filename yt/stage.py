import json,shutil,os,sys
slug=sys.argv[1]; res=[]
for o in json.load(open('/home/claude/travel/yt/meta.json')):
  if o['slug']==slug:
    d=f"/mnt/user-data/outputs/yt/{o['playlist']}";os.makedirs(d,exist_ok=True);shutil.copy('/home/claude/travel/yt/out/'+o['src'],d+'/'+o['file'])
    assert os.path.getsize(d+'/'+o['file'])<30e6, o['file']
    res.append({"stagedPath":d+'/'+o['file'],"devicePath":"C:\\Users\\vmfob\\Videos\\Слайд-шоу для YouTube\\"+o['playlist']+"\\"+o['file']})
print(json.dumps(res,ensure_ascii=False))

window.sl=ms=>new Promise(r=>setTimeout(r,ms));
window.deep=function(root,acc=[]){for(const e of root.querySelectorAll('*')){acc.push(e);if(e.shadowRoot)deep(e.shadowRoot,acc)}return acc};
window.waitFor=async(f,ms=30000)=>{const t0=Date.now();while(Date.now()-t0<ms){const v=f();if(v)return v;await sl(300)}return null};
window.setBox=async function(e,txt){e.click();e.focus();const r=document.createRange();r.selectNodeContents(e);const s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('insertText',false,txt);await sl(400);return e.textContent};
window.okv=()=>deep(document).filter(e=>e.tagName=='YTCP-BUTTON'&&/^(ОК|Готово)$/.test((e.innerText||'').trim())&&e.getBoundingClientRect().width>0);
window.ytOpenKey=async function(key){
 await waitFor(()=>document.querySelectorAll('ytcp-video-row').length);
 const r=[...document.querySelectorAll('ytcp-video-row')].find(r=>(r.querySelector('#video-title')?.textContent.trim()||'').startsWith(key)&&/Черновик/.test(r.innerText));if(!r)return 'norow';
 [...r.querySelectorAll('ytcp-button,button')].find(b=>/Редактировать черновик/.test(b.textContent)).click();
 const d=document.querySelector('ytcp-uploads-dialog');
 const ok=await waitFor(()=>{const e=d.querySelector('#title-textarea #textbox');return e&&e.textContent.length>3&&d.innerText.length>500});
 await sl(2500);return ok?'opened':'nodialog'};
window.plPrep=async function(){
 const d=document.querySelector('ytcp-uploads-dialog');d.querySelector('ytcp-video-metadata-playlists ytcp-dropdown-trigger').click();await sl(2500);
 const nb=deep(document).filter(e=>e.tagName=='YTCP-BUTTON'&&/Новый плейлист/.test(e.innerText||'')&&e.getBoundingClientRect().width>0).pop();nb.click();await sl(1200);
 const it=deep(document).filter(e=>e.tagName=='TP-YT-PAPER-ITEM'&&(e.textContent||'').trim().startsWith('Новый плейлист')).pop();it.click();await sl(2500);
 const cd=document.querySelector('ytcp-playlist-creation-dialog');const tr=[...cd.querySelectorAll('ytcp-dropdown-trigger')].find(e=>/Параметры доступа/.test(e.textContent));tr.click();await sl(1000);
 const un=deep(document).filter(e=>e.tagName=='TP-YT-PAPER-ITEM'&&/^\s*Доступ по ссылке\s*$/.test(e.textContent)).pop();un&&un.click();await sl(800);
 const tb=cd.querySelectorAll('#textbox')[0];const rc=tb.getBoundingClientRect();const k=800/innerWidth;
 return [tr.innerText.replace(/\s+/g,' '),Math.round((rc.x+rc.width/2)*k),Math.round((rc.y+rc.height/2)*k)]};
window.plCreate=async function(name){
 const cd=document.querySelector('ytcp-playlist-creation-dialog');const t=cd.querySelectorAll('#textbox')[0].textContent;if(t!==name)return 'badname '+t;
 cd.querySelector('#create-button').click();await sl(3500);
 const d=document.querySelector('ytcp-uploads-dialog');const plv=d.querySelector('ytcp-video-metadata-playlists ytcp-dropdown-trigger').innerText.replace(/\s+/g,' ');
 {const o=okv();if(o.length){o[o.length-1].click();await sl(1200)}}
 const p=JSON.parse(localStorage.getItem('ytpls')||'[]');if(!p.includes(name))p.push(name);localStorage.setItem('ytpls',JSON.stringify(p));
 return 'created, video playlist field: '+plv};
window.ytFill=async function(title,desc,pl){
 const d=document.querySelector('ytcp-uploads-dialog');
 const tb=await waitFor(()=>{const e=d.querySelector('#title-textarea #textbox');return e&&e.textContent.length>3?e:null});if(!tb)return 'nodialog';
 {const o=okv();if(o.length){o[o.length-1].click();await sl(1200)}}
 await sl(800);
 const t=await setBox(tb,title); await setBox(d.querySelector('#description-textarea #textbox'),desc);
 if(t!==title) return 'titlefail '+t;
 d.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').click();
 d.querySelector('ytcp-video-metadata-playlists ytcp-dropdown-trigger').click();await sl(1500);
 const span=await waitFor(()=>deep(document).find(e=>e.classList&&e.classList.contains('label')&&e.textContent.trim()==pl));
 if(!span) return 'nopl '+t;
 const cbl=span.closest('label').querySelector('ytcp-checkbox-lit');const inner=cbl.querySelector('[role=checkbox]')||cbl;if(inner.getAttribute('aria-checked')!=='true')inner.click();await sl(500);
 const ok=okv();ok[ok.length-1].click();await sl(1000);
 const plv=d.querySelector('ytcp-video-metadata-playlists ytcp-dropdown-trigger').innerText.replace(/\s+/g,' ');
 for(let i=0;i<3;i++){d.querySelector('#next-button').click();await sl(1800)}
 const un=d.querySelector('tp-yt-paper-radio-button[name="UNLISTED"]');un.click();await sl(800);
 d.querySelector('#done-button').click();await sl(4000);
 const cl=[...document.querySelectorAll('ytcp-button,button')].find(b=>b.offsetParent&&/^Закрыть$/.test(b.innerText.trim()));cl&&cl.click();await sl(800);
 return 'ok '+t+' | '+plv+' | '+un.getAttribute('aria-checked');
};
window.ytAuto=async function(){
 const Q=JSON.parse(localStorage.getItem('ytq2'));const done=JSON.parse(localStorage.getItem('ytdone2')||'[]');const norm=s=>s.toLowerCase().replace(/[^0-9a-zа-яё]/g,'');const known=JSON.parse(localStorage.getItem('ytpls')||'[]');
 await waitFor(()=>document.querySelectorAll('ytcp-video-row').length);
 for(const r of document.querySelectorAll('ytcp-video-row')){
  const tt=r.querySelector('#video-title')?.textContent.trim()||'';
  if(!/Черновик/.test(r.innerText))continue;
  const key=Q[norm(tt)]?norm(tt):null;if(!key||done.includes(key))continue;
  const [title,desc,pl]=Q[key];
  if(!known.includes(pl)) return 'NEEDPL '+pl+' for '+key;
  [...r.querySelectorAll('ytcp-button,button')].find(b=>/Редактировать черновик/.test(b.textContent)).click();
  const d=document.querySelector('ytcp-uploads-dialog');
  await waitFor(()=>{const e=d.querySelector('#title-textarea #textbox');return e&&e.textContent.length>3&&d.innerText.length>500});
  await sl(2500);
  const res=await ytFill(title,desc,pl);
  if(res.startsWith('ok')){done.push(key);localStorage.setItem('ytdone2',JSON.stringify(done))}
  return key+' => '+res;
 }
 return 'none';
};
window.ytCycle=async function(){const tab=n=>[...document.querySelectorAll('tp-yt-paper-tab, [role=tab]')].find(t=>t.innerText.trim()==n);tab('Shorts').click();await sl(2500);tab('Видео').click();await sl(4500);return ytAuto()};
window.ytLoop=async function(n){const out=[];for(let i=0;i<n;i++){let r;try{r=await ytCycle()}catch(e){r='err '+e}out.push(r);window.RESL=out.join('\n');if(r=='none'||r.startsWith('NEEDPL')||!/=> ok/.test(r))break;await sl(1500)}window.RESL=out.join('\n')+'\nEND';};
'helpers ok'

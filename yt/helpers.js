window.deep=function(root,acc=[]){for(const e of root.querySelectorAll('*')){acc.push(e);if(e.shadowRoot)deep(e.shadowRoot,acc)}return acc};
window.setBox=async function(e,txt){e.click();e.focus();const r=document.createRange();r.selectNodeContents(e);const s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('insertText',false,txt);await new Promise(r=>setTimeout(r,400));return e.textContent};
window.ytFill=async function(title,desc,pl){
 const sl=ms=>new Promise(r=>setTimeout(r,ms));
 const waitFor=async(f,ms=30000)=>{const t0=Date.now();while(Date.now()-t0<ms){const v=f();if(v)return v;await sl(300)}return null};
 const d=document.querySelector('ytcp-uploads-dialog');
 const tb=await waitFor(()=>{const e=d.querySelector('#title-textarea #textbox');return e&&e.textContent.length>3?e:null});if(!tb)return 'nodialog';
 const okv=()=>deep(document).filter(e=>e.tagName=='YTCP-BUTTON'&&/^(ОК|Готово)$/.test((e.innerText||'').trim())&&e.getBoundingClientRect().width>0);
 {const o=okv();if(o.length){o[o.length-1].click();await sl(1200)}}
 await sl(800);
 const t=await setBox(tb,title); await setBox(d.querySelector('#description-textarea #textbox'),desc);
 if(t!==title) return 'titlefail '+t;
 d.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').click();
 d.querySelector('ytcp-video-metadata-playlists ytcp-dropdown-trigger').click();await sl(1500);
 let span=await waitFor(()=>deep(document).find(e=>e.classList&&e.classList.contains('label')&&e.textContent.trim()==pl));
 if(!span) return 'nopl '+t;
 const cbl=span.closest('label').querySelector('ytcp-checkbox-lit');const inner=cbl.querySelector('[role=checkbox]')||cbl;if(inner.getAttribute('aria-checked')!=='true')inner.click();await sl(500);
 const ok=okv();ok[ok.length-1].click();await sl(1000);
 const plv=d.querySelector('ytcp-video-metadata-playlists ytcp-dropdown-trigger').innerText.replace(/\s+/g,' ');
 for(let i=0;i<3;i++){d.querySelector('#next-button').click();await sl(1500)}
 const un=d.querySelector('tp-yt-paper-radio-button[name="UNLISTED"]');un.click();await sl(700);
 d.querySelector('#done-button').click();await sl(3500);
 const cl=[...document.querySelectorAll('ytcp-button,button')].find(b=>b.offsetParent&&/^Закрыть$/.test(b.innerText.trim()));cl&&cl.click();
 return 'ok '+t+' | '+plv+' | '+un.getAttribute('aria-checked');
};
window.ytAuto=async function(){
 const sl=ms=>new Promise(r=>setTimeout(r,ms));
 const Q=JSON.parse(localStorage.getItem('ytq'));const done=JSON.parse(localStorage.getItem('ytdone')||'[]');const known=JSON.parse(localStorage.getItem('ytpls')||'[]');
 const waitFor=async(f,ms=20000)=>{const t0=Date.now();while(Date.now()-t0<ms){const v=f();if(v)return v;await sl(300)}return null};
 await waitFor(()=>document.querySelectorAll('ytcp-video-row').length);
 for(const r of document.querySelectorAll('ytcp-video-row')){
  const tt=r.querySelector('#video-title')?.textContent.trim()||'';
  const b=[...r.querySelectorAll('ytcp-button,button')].find(b=>/Редактировать черновик/.test(b.textContent));if(!b)continue;
  const key=Object.keys(Q).find(k=>tt.startsWith(k));if(!key||done.includes(key))continue;
  const [title,desc,pl]=Q[key];
  if(!known.includes(pl)) return 'NEEDPL '+pl+' for '+key;
  b.click();
  const d=document.querySelector('ytcp-uploads-dialog');
  await waitFor(()=>{const e=d.querySelector('#title-textarea #textbox');return e&&e.textContent.length>3&&d.innerText.length>500});
  await sl(2500);
  const res=await ytFill(title,desc,pl);
  if(res.startsWith('ok')){done.push(key);localStorage.setItem('ytdone',JSON.stringify(done))}
  return key+' => '+res;
 }
 return 'none';
};
window.ytRun=function(){window.RES='running';ytAuto().then(r=>window.RES=r,e=>window.RES='err '+e)};

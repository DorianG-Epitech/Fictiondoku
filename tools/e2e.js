const puppeteer=require('puppeteer-core');
(async()=>{
const b=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.setViewport({width:900,height:1100});
await p.goto('file://'+require('path').resolve(__dirname,'../docs/index.html')+'');await new Promise(r=>setTimeout(r,500));
const title=await p.$eval('#title',e=>e.textContent);console.log('title',title);
// solve: for each cell pick an answer via UI
for(let k=0;k<9;k++){
  const ans=await p.evaluate(k=>{ /* find a valid unused name */ return null},k);
}
// get grid info from page by re-running core
const info=await p.evaluate(()=>{const G=FD.init(DATA);const d=new Intl.DateTimeFormat('fr-CA',{timeZone:'Europe/Paris',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());const g=G.generate('daily-'+d,'normal');
 const used={};const out=[];for(let r=0;r<3;r++)for(let c=0;c<3;c++){const a=G.answers(g.rows[r],g.cols[c]).filter(i=>!used[i]);used[a[0]]=1;out.push(G.chars[a[0]].name);}
 const wrong=G.chars.find(ch=>!(ch.catset[g.rows[0]]&&ch.catset[g.cols[0]])).name;return {out,wrong,labels:g.rows.map(i=>G.cats[i].label).concat(g.cols.map(i=>G.cats[i].label))};});
console.log(info.labels.join(' / '));
// wrong guess on cell 0
const cells=await p.$$('.cell');await cells[0].click();await p.type('#q',info.wrong);await new Promise(r=>setTimeout(r,200));
await p.keyboard.press('Enter');await new Promise(r=>setTimeout(r,200));console.log('msg',await p.$eval('#msg',e=>e.textContent),'hearts',await p.$eval('#hearts',e=>e.textContent));
await p.keyboard.press('Escape');
for(let k=0;k<9;k++){const cs=await p.$$('.cell');await cs[k].click();await new Promise(r=>setTimeout(r,100));
  await p.$eval('#q',e=>e.value='');await p.type('#q',info.out[k]);await new Promise(r=>setTimeout(r,150));
  const first=await p.$eval('#sugg li span',e=>e.textContent);
  // choose exact item
  const lis=await p.$$('#sugg li');let idx=0;for(let j=0;j<lis.length;j++){const t=await lis[j].$eval('span',e=>e.textContent);if(t===info.out[k]){idx=j;break;}}
  await lis[idx].click();await new Promise(r=>setTimeout(r,150));}
console.log('end',await p.$eval('#end',e=>e.innerText.replace(/\n/g,' | ')));
await p.screenshot({path:''+require('path').resolve(__dirname,'../screenshots')+'/screenshot_end.png',fullPage:true});
const cs=await p.$$('.cell');await cs[4].click();await new Promise(r=>setTimeout(r,200));
console.log('answers',(await p.$eval('#ans',e=>e.innerText)).slice(0,200).replace(/\n/g,', '));
await p.screenshot({path:''+require('path').resolve(__dirname,'../screenshots')+'/screenshot_answers.png'});
// reload persists
await p.reload();await new Promise(r=>setTimeout(r,400));console.log('after reload score',await p.$eval('#score',e=>e.textContent));
// free mode
await p.click('#bFree');await new Promise(r=>setTimeout(r,200));await p.select('#diff','difficile');await new Promise(r=>setTimeout(r,200));
console.log('free title',await p.$eval('#title',e=>e.textContent));
const c0=await p.$$('.cell');await c0[0].click();await p.type('#q','herm');await new Promise(r=>setTimeout(r,150));
console.log('sugg',await p.$$eval('#sugg li',ls=>ls.map(l=>l.innerText.replace(/\n/g,' ')).join(' ; ')));
await p.screenshot({path:''+require('path').resolve(__dirname,'../screenshots')+'/screenshot_search.png'});
await p.setViewport({width:390,height:844});await p.keyboard.press('Escape');await p.screenshot({path:''+require('path').resolve(__dirname,'../screenshots')+'/screenshot_mobile.png'});
console.log('errors',errs);await b.close();})();

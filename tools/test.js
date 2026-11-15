const FD=require('./core.js');const data=JSON.parse(require('fs').readFileSync('../docs/data.json','utf8'));
let t=Date.now();const G=FD.init(data);console.log('init ms',Date.now()-t,'chars',G.chars.length,'cats',G.K);
const C=n=>G.cats[n].label;
for(const d of ['facile','normal','difficile']){
  let fails=0,minCell=1e9,times=[];const seen=new Set();
  for(let k=0;k<300;k++){t=Date.now();const g=G.generate('test-'+k,d);times.push(Date.now()-t);if(!g){fails++;continue;}
    seen.add(g.rows.concat(g.cols).join(','));
    for(const r of g.rows)for(const c of g.cols){const a=G.answers(r,c).filter(i=>G.chars[i].sl>=8).length;minCell=Math.min(minCell,a);}
    if(!G.hasMatching(g.rows,g.cols))throw 'nomatch';}
  times.sort((a,b)=>a-b);console.log(d,'fails',fails,'distinct',seen.size,'minNotableCell',minCell,'median ms',times[150],'max ms',times[299]);
}
// determinism
const a=G.generate('2026-11-15','normal'),b=G.generate('2026-11-15','normal');console.log('deterministic',JSON.stringify(a)===JSON.stringify(b));
console.log('Daily:',a.rows.map(C),'x',a.cols.map(C));
for(const r of a.rows)for(const c of a.cols)console.log(' ',C(r),'×',C(c),G.answers(r,c).length,G.answers(r,c).slice(0,5).map(i=>G.chars[i].name).join(', '));
console.log(G.search('dark vad').map(x=>G.chars[x.i].name+(x.via?' ('+x.via+')':'')));
console.log(G.search('heroine').map(x=>G.chars[x.i].name), G.search('Goku').map(x=>G.chars[x.i].name+(x.via?' ('+x.via+')':'')));

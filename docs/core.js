// Fictiondoku core logic (shared by the page and the node tests)
var FD=(function(){
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/œ/g,'oe').replace(/æ/g,'ae').replace(/[^a-z0-9]+/g,' ').trim();}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}}
function hashStr(s){var h=1779033703^s.length;for(var i=0;i<s.length;i++){h=Math.imul(h^s.charCodeAt(i),3432918353);h=h<<13|h>>>19;}return (h>>>0);}
var SAMEGROUP_BLOCK={lettre:1,nom:1,epoque:1,genre_p:1,pays:1,media:1};
var DIFF={facile:{min:12,big:40,noSmall:true},normal:{min:5,big:0},difficile:{min:3,big:0}};
var W={univers:3,equipe:1.5,createur:1,type:2,metier:2,media:2,genre:1.2,pays:1.2,epoque:1.5,genre_p:0.6,nom:0.8,lettre:0.5};
function init(data){
  var cats=data.cats.map(function(c,i){return {i:i,id:c[0],label:c[1],group:c[2]};});
  var K=cats.length;
  var chars=data.chars.map(function(c,i){var al=c[1]?c[1].split('|'):[];return {i:i,name:c[0],aliases:al,sl:c[2],cats:c[3],alts:c[4]||[],keys:[norm(c[0])].concat(al.map(norm))};});
  var members=cats.map(function(){return [];});
  var pairAll=new Int32Array(K*K),pair8=new Int32Array(K*K);
  chars.forEach(function(ch){ch.catset={};ch.cats.forEach(function(a){ch.catset[a]=1;members[a].push(ch.i);
    ch.cats.forEach(function(b){pairAll[a*K+b]++;if(ch.sl>=8)pair8[a*K+b]++;});});
    ch.altsets=ch.alts.map(function(al){var o={};al.forEach(function(a){o[a]=1;if(!ch.catset[a]&&members[a][members[a].length-1]!==ch.i)members[a].push(ch.i);});return o;});});
  members.forEach(function(m){m.sort(function(x,y){return chars[y].sl-chars[x].sl;});});
  function compat(a,b,d){
    if(a===b)return false;var ga=cats[a].group,gb=cats[b].group;
    if(ga===gb&&SAMEGROUP_BLOCK[ga])return false;
    if((ga==='lettre'||ga==='nom')&&(gb==='lettre'||gb==='nom'))return false;
    var na=pairAll[a*K+a],nb=pairAll[b*K+b];
    if(pairAll[a*K+b]>0.85*Math.min(na,nb))return false;
    return pair8[a*K+b]>=DIFF[d].min;
  }
  function allowed(c,d){var g=cats[c].group;if(DIFF[d].noSmall&&(g==='lettre'||g==='nom'||g==='createur'||g==='equipe'))return false;return pair8[c*K+c]>=DIFF[d].big;}
  function ok(i,r,c){var ch=chars[i];if(ch.catset[r]&&ch.catset[c])return true;for(var k=0;k<ch.altsets.length;k++)if(ch.altsets[k][r]&&ch.altsets[k][c])return true;return false;}
  function answers(r,c){return members[r].filter(function(i){return ok(i,r,c);});}
  function pick(rng,list){var tot=0;list.forEach(function(c){tot+=W[cats[c].group]||1;});var x=rng()*tot;for(var k=0;k<list.length;k++){x-=W[cats[list[k]].group]||1;if(x<=0)return list[k];}return list[list.length-1];}
  function groupOk(sel,c){var g=cats[c].group,n=0,nn=0;sel.forEach(function(s){if(cats[s].group===g)n++;if(cats[s].group==='lettre'||cats[s].group==='nom')nn++;});
    if((g==='lettre'||g==='nom')&&nn>=1)return false;if(g==='genre_p'&&n>=1)return false;return n<(g==='univers'?3:2);}
  function hasMatching(rows,cols){
    var cand=[];for(var r=0;r<3;r++)for(var c=0;c<3;c++)cand.push(answers(rows[r],cols[c]).slice(0,40));
    var used={};var order=[0,1,2,3,4,5,6,7,8].sort(function(a,b){return cand[a].length-cand[b].length;});
    function go(k){if(k===9)return true;var l=cand[order[k]];for(var j=0;j<l.length;j++){if(!used[l[j]]){used[l[j]]=1;if(go(k+1))return true;delete used[l[j]];}}return false;}
    return go(0);
  }
  function generate(seedStr,d){
    var rng=mulberry32(hashStr(seedStr+'|'+d));
    var pool=[];for(var c=0;c<K;c++)if(allowed(c,d))pool.push(c);
    for(var t=0;t<20000;t++){
      var rows=[];var guard=0;
      while(rows.length<3&&guard++<50){var c0=pick(rng,pool);if(rows.indexOf(c0)<0&&groupOk(rows,c0))rows.push(c0);}
      if(rows.length<3)continue;
      var cand=pool.filter(function(c){return rows.indexOf(c)<0&&compat(rows[0],c,d)&&compat(rows[1],c,d)&&compat(rows[2],c,d);});
      if(cand.length<3)continue;
      var cols=[];guard=0;var sel=rows.slice();
      while(cols.length<3&&guard++<60){var c1=pick(rng,cand);if(cols.indexOf(c1)<0&&groupOk(sel,c1)){cols.push(c1);sel.push(c1);}}
      if(cols.length<3)continue;
      if(!hasMatching(rows,cols))continue;
      if(rng()<0.5){var tmp=rows;rows=cols;cols=tmp;}
      return {rows:rows,cols:cols,seed:seedStr,diff:d};
    }
    return null;
  }
  function search(q,limit){
    var nq=norm(q);if(!nq)return [];var res=[];
    for(var i=0;i<chars.length;i++){var ch=chars[i],best=-1,via=null;
      for(var k=0;k<ch.keys.length;k++){var key=ch.keys[k],s=-1;
        if(key===nq)s=4;else if(key.indexOf(nq)===0)s=3;else if(key.indexOf(' '+nq)>=0)s=2;else if(nq.length>=3&&key.indexOf(nq)>=0)s=1;
        if(k>0&&s>0)s-=0.5;
        if(s>best){best=s;via=k===0?null:ch.aliases[k-1];}}
      if(best>0)res.push({i:i,s:best,via:via});}
    res.sort(function(a,b){return b.s-a.s||chars[b.i].sl-chars[a.i].sl;});
    return res.slice(0,limit||8);
  }
  function points(r,c,i){var a=answers(r,c);var k=a.indexOf(i);if(k<0)return 0;if(a.length===1)return 100;return Math.round(10+90*k/(a.length-1));}
  return {ok:ok,cats:cats,chars:chars,members:members,compat:compat,answers:answers,generate:generate,search:search,points:points,hasMatching:hasMatching,pairAll:pairAll,pair8:pair8,K:K};
}
return {init:init,norm:norm,hashStr:hashStr};
})();
if(typeof module!=='undefined')module.exports=FD;

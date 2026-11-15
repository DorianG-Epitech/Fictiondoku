import pickle,json,re,unicodedata,collections,itertools,random
from cats import CATS
chars,mem=pickle.load(open('assigned.pkl','rb'))
G={cid:g for cid,l,g,f in CATS}
SAFE={'univers','equipe','createur','type','metier'}
def norm(s):
    s=unicodedata.normalize('NFKD',s.lower()); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
groups=collections.defaultdict(list)
for c in chars: groups[norm(c['name'])].append(c)
out=[]
for k,cs in groups.items():
    cs.sort(key=lambda c:-c['sl']); p=cs[0]
    cats=set(p['cats'])
    pu={x for x in p['cats'] if G[x]=='univers'}
    alts=[]
    for d in cs[1:]:
        du={x for x in d['cats'] if G[x]=='univers'}
        linked = p['id'] in (d['P']['P144']+d['P']['P460']) or d['id'] in (p['P']['P144']+p['P']['P460'])
        if linked or (du & pu):
            cats|={x for x in d['cats'] if G[x] in SAFE}
        else:
            alts.append(set(d['cats']))  # homonym (other work): accepted only on its own categories
    al=set()
    for d in cs: al|=set(d['aliases'])
    nm=p['name']; nm=nm[0].upper()+nm[1:]
    al={a for a in al if norm(a)!=norm(nm) and norm(a)}
    # dedupe aliases by norm
    seen=set();als=[]
    for a in sorted(al,key=len):
        if norm(a) not in seen: seen.add(norm(a)); als.append(a)
    out.append(dict(name=nm,aliases=als[:12],sl=p['sl'],cats=cats,alts=alts,ids=[d['id'] for d in cs],first=p['first']))
# era fix: a character whose name is an alias of another (e.g. 'Peter Parker' -> Spider-Man) inherits the earliest first-appearance year
aliasmin={}
for c in out:
    for a in c['aliases']:
        k=norm(a)
        if c['first'] is not None: aliasmin[k]=min(aliasmin.get(k,9999),c['first'])
def era(y):
    return 'e_1950' if y<1950 else 'e_5070' if y<1980 else 'e_80' if y<1990 else 'e_90' if y<2000 else 'e_00' if y<2010 else 'e_10'
nfix=0
for c in out:
    m=aliasmin.get(norm(c['name']))
    if m is not None and (c['first'] is None or m<c['first']):
        c['first']=m; c['cats']={x for x in c['cats'] if not x.startswith('e_')}|{era(m)}; nfix+=1
print('era fixed via alias',nfix)
MEAN0={'univers','equipe','createur','type','metier','media','genre'}
for c in out:
    keep=[]
    for a in c['alts']:
        if a<=c['cats'] or not any(G[x] in MEAN0 for x in a): continue
        if any(a<=b for b in keep): continue
        keep=[b for b in keep if not b<=a]+[a]
    c['alts']=keep
# drop characters with no meaningful category
MEAN={g for g in ('univers','equipe','createur','type','metier','media','genre','pays','epoque')}
out=[c for c in out if any(G[x] in MEAN for x in c['cats'])]
out.sort(key=lambda c:-c['sl'])
catids=[cid for cid,l,g,f in CATS]
cnt=collections.Counter(x for c in out for x in c['cats'])
print('characters',len(out),'notable(sl>=8)',sum(c['sl']>=8 for c in out))
json.dump({'cats':[{'id':cid,'label':l,'group':g,'n':cnt[cid],'n8':sum(1 for c in out if cid in c['cats'] and c['sl']>=8)} for cid,l,g,f in CATS],
           'chars':[{'name':c['name'],'aliases':c['aliases'],'sl':c['sl'],'cats':sorted(c['cats'],key=catids.index),'wikidata':c['ids'],'first_year':c['first'],'homonyms_cats':[sorted(a,key=catids.index) for a in c['alts']]} for c in out]},
          open('../data/fictiondoku_clean.json','w'),ensure_ascii=False,indent=0)
pickle.dump((out,catids),open('final.pkl','wb'))

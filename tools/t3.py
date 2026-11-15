from q import q
import json
cls=json.load(open('allclasses.json'))
items={}
for i in range(0,len(cls),300):
    ch=cls[i:i+300]
    v=' '.join('wd:'+c for c in ch)
    res=q(f"""SELECT DISTINCT ?x ?s WHERE {{ VALUES ?cls {{ {v} }} ?x wdt:P31 ?cls . ?x wikibase:sitelinks ?s . FILTER(?s>=4) }}""",timeout=90)
    for b in res: items[b['x']['value'].split('/')[-1]]=int(b['s']['value'])
    print(i,len(items),flush=True)
json.dump(items,open('items.json','w'))
import collections
c=collections.Counter()
for s in items.values():
    for t in [4,5,6,8,10,15,20]:
        if s>=t:c[t]+=1
print(sorted(c.items()))

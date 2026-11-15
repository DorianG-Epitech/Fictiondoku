from q import q
import json
d=json.load(open('raw_chars.json'))
T=d['triples']
vals=sorted({v for x,p,v in T if v.startswith('Q')})
works=sorted({v for x,p,v in T if p in('P1441','P4584','P1080','P8345','P144') and v.startswith('Q')})
print(len(vals),len(works))
props='P31 P495 P577 P571 P580 P8345 P1080 P179 P361 P364 P407 P136 P272 P449 P123 P50 P170 P57 P58 P86 P750 P437'.split()
wt=[];lab={}
B=300
for i in range(0,len(works),B):
    v=' '.join('wd:'+c for c in works[i:i+B]); pv=' '.join('wdt:'+p for p in props)
    for b in q(f"""SELECT ?x ?p ?v WHERE {{ VALUES ?x {{ {v} }} VALUES ?p {{ {pv} }} ?x ?p ?v . }}"""):
        wt.append((b['x']['value'].split('/')[-1],b['p']['value'].split('/')[-1],b['v']['value'].split('/')[-1]))
    print('w',i,len(wt),flush=True)
allv=sorted(set(vals)|{v for x,p,v in wt if v.startswith('Q')})
B=400
for i in range(0,len(allv),B):
    v=' '.join('wd:'+c for c in allv[i:i+B])
    for b in q(f"""SELECT ?x ?l WHERE {{ VALUES ?x {{ {v} }} ?x rdfs:label ?l . FILTER(LANG(?l) IN ("fr","en")) }}"""):
        lab.setdefault(b['x']['value'].split('/')[-1],{})[b['l']['xml:lang']]=b['l']['value']
    print('l',i,flush=True)
json.dump({'wt':wt,'lab':lab},open('raw_works.json','w'),ensure_ascii=False)

from wq import q
import json
from concurrent.futures import ThreadPoolExecutor
d=json.load(open('raw_chars_all.json')); old=json.load(open('raw_works.json'))
T=d['triples']
oldw={x for x,p,v in old['wt']}
works=sorted({v for x,p,v in T if p in('P1441','P4584','P1080','P8345','P144') and v.startswith('Q')})
neww=[w for w in works if w not in oldw]
print(len(works),len(neww),flush=True)
props='P31 P495 P577 P571 P580 P8345 P1080 P179 P361 P364 P407 P136 P272 P449 P123 P50 P170 P57 P58 P86 P750 P437'.split()
pv=' '.join('wdt:'+p for p in props)
def jw(ch):
    v=' '.join('wd:'+c for c in ch)
    return q(f"SELECT ?x ?p ?v WHERE {{ VALUES ?x {{ {v} }} VALUES ?p {{ {pv} }} ?x ?p ?v . }}")
wt=old['wt']
with ThreadPoolExecutor(4) as ex:
    for n,r in enumerate(ex.map(jw,[neww[i:i+250] for i in range(0,len(neww),250)])):
        if r is None: print('failw'); continue
        for b in r: wt.append((b['x']['value'].split('/')[-1],b['p']['value'].split('/')[-1],b['v']['value'].split('/')[-1]))
print('works done',len(wt),flush=True)
lab=old['lab']
allv=sorted(({v for x,p,v in T if v.startswith('Q')}|{v for x,p,v in wt if v.startswith('Q')})-set(lab))
print('labels needed',len(allv),flush=True)
def jl(ch):
    v=' '.join('wd:'+c for c in ch)
    return q(f'SELECT ?x ?l WHERE {{ VALUES ?x {{ {v} }} ?x rdfs:label ?l . FILTER(LANG(?l) IN ("fr","en")) }}')
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(jl,[allv[i:i+400] for i in range(0,len(allv),400)]):
        if r is None: print('faill'); continue
        for b in r: lab.setdefault(b['x']['value'].split('/')[-1],{})[b['l']['xml:lang']]=b['l']['value']
json.dump({'wt':wt,'lab':lab},open('raw_works_all.json','w'),ensure_ascii=False)
print('done',len(lab))

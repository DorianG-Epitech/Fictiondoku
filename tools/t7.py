from wq import q
import json
from concurrent.futures import ThreadPoolExecutor
d=json.load(open('raw_chars_all.json')); w=json.load(open('raw_works_all.json'))
have={x for x,p,v in w['wt']}
cand=set(v for x,p,v in d['triples'] if p in ('P8345','P1080','P463','P144') and v.startswith('Q'))
cand|=set(v for x,p,v in w['wt'] if p in ('P8345','P1080','P179','P361') and v.startswith('Q'))
need=sorted(cand-have); print(len(need))
def job(ch):
    v=' '.join('wd:'+c for c in ch)
    return q(f"SELECT ?x ?p ?v WHERE {{ VALUES ?x {{ {v} }} VALUES ?p {{ wdt:P8345 wdt:P1080 wdt:P179 wdt:P361 wdt:P31 }} ?x ?p ?v . }}")
out=[]
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(job,[need[i:i+300] for i in range(0,len(need),300)]):
        if r is None: print('fail'); continue
        for b in r: out.append((b['x']['value'].split('/')[-1],b['p']['value'].split('/')[-1],b['v']['value'].split('/')[-1]))
lab=w['lab']
miss=sorted({v for x,p,v in out if v.startswith('Q')}|set(need))
miss=[m for m in miss if m not in lab]; print('labels',len(miss))
def jl(ch):
    v=' '.join('wd:'+c for c in ch)
    return q(f'SELECT ?x ?l WHERE {{ VALUES ?x {{ {v} }} ?x rdfs:label ?l . FILTER(LANG(?l) IN ("fr","en")) }}')
nl={}
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(jl,[miss[i:i+400] for i in range(0,len(miss),400)]):
        for b in r or []: nl.setdefault(b['x']['value'].split('/')[-1],{})[b['l']['xml:lang']]=b['l']['value']
json.dump({'wt':out,'lab':nl},open('raw_hop.json','w'),ensure_ascii=False)
print(len(out),len(nl))

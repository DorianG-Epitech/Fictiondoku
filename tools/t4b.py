from wq import q
import json
from concurrent.futures import ThreadPoolExecutor
old=json.load(open('raw_chars.json'))
have=set(old['labels'])|{x for x,p,v in old['triples']}
items=[x for x in json.load(open('items_all.json')) if x not in have]
print('new',len(items))
props='P21 P31 P1080 P8345 P1441 P170 P106 P4584 P571 P569 P172 P1074 P27 P551 P39 P54 P460 P144 P463 P1340 P2348 P3364'.split()
pv=' '.join('wdt:'+p for p in props)
def job(ch):
    v=' '.join('wd:'+c for c in ch)
    a=q(f"SELECT ?x ?p ?v WHERE {{ VALUES ?x {{ {v} }} VALUES ?p {{ {pv} }} ?x ?p ?v . }}")
    b=q(f"""SELECT ?x ?l ?k WHERE {{ VALUES ?x {{ {v} }} {{ ?x rdfs:label ?l . BIND("L" AS ?k) }} UNION {{ ?x skos:altLabel ?l . BIND("A" AS ?k) }} FILTER(LANG(?l) IN ("fr","en")) }}""")
    return ch,a,b
B=250
chunks=[items[i:i+B] for i in range(0,len(items),B)]
T=old['triples'];LB=old['labels'];fail=[]
with ThreadPoolExecutor(4) as ex:
    for n,(ch,a,b) in enumerate(ex.map(job,chunks)):
        if a is None or b is None: fail.append(ch); continue
        for r in a: T.append((r['x']['value'].split('/')[-1],r['p']['value'].split('/')[-1],r['v']['value'].split('/')[-1]))
        for r in b: LB.setdefault(r['x']['value'].split('/')[-1],[]).append((r['k']['value'],r['l'].get('xml:lang'),r['l']['value']))
        if n%40==0: print(n,len(chunks),len(T),flush=True)
print('fail',len(fail))
json.dump({'triples':T,'labels':LB},open('raw_chars_all.json','w'),ensure_ascii=False)

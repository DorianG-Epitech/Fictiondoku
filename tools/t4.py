from q import q
import json
items=list(json.load(open('items.json')))
props='P21 P31 P1080 P8345 P1441 P170 P106 P4584 P571 P569 P172 P1074 P27 P551 P39 P54 P460 P144 P463 P1340 P2348 P3364'.split()
triples=[];labels={}
B=300
for i in range(0,len(items),B):
    v=' '.join('wd:'+c for c in items[i:i+B])
    pv=' '.join('wdt:'+p for p in props)
    res=q(f"""SELECT ?x ?p ?v WHERE {{ VALUES ?x {{ {v} }} VALUES ?p {{ {pv} }} ?x ?p ?v . }}""")
    for b in res: triples.append((b['x']['value'].split('/')[-1],b['p']['value'].split('/')[-1],b['v']['value'].split('/')[-1]))
    res=q(f"""SELECT ?x ?l ?k WHERE {{ VALUES ?x {{ {v} }} {{ ?x rdfs:label ?l . BIND("L" AS ?k) }} UNION {{ ?x skos:altLabel ?l . BIND("A" AS ?k) }} FILTER(LANG(?l) IN ("fr","en")) }}""")
    for b in res:
        x=b['x']['value'].split('/')[-1]; l=b['l']; 
        labels.setdefault(x,[]).append((b['k']['value'],l.get('xml:lang'),l['value']))
    print(i,len(triples),flush=True)
json.dump({'triples':triples,'labels':labels},open('raw_chars.json','w'),ensure_ascii=False)

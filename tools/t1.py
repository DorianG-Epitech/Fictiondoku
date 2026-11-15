from q import q
import json
res=q("""SELECT ?cls ?clsLabel (COUNT(?x) AS ?n) WHERE {
 ?x wdt:P31 ?cls . ?cls wdt:P279* wd:Q95074 . ?x wikibase:sitelinks ?s . FILTER(?s>=6)
 SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
} GROUP BY ?cls ?clsLabel ORDER BY DESC(?n) LIMIT 400""",timeout=90)
tot=0
for b in res:
    n=int(b['n']['value']); tot+=n
    print(n,b['cls']['value'].split('/')[-1],b.get('clsLabel',{}).get('value'))
print('total',tot)

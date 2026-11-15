from q import q
import json
cls=json.load(open('allclasses.json'))
edges=[];lab={}
for i in range(0,len(cls),400):
    v=' '.join('wd:'+c for c in cls[i:i+400])
    for b in q(f"""SELECT ?c ?p ?l WHERE {{ VALUES ?c {{ {v} }} OPTIONAL {{ ?c wdt:P279 ?p }} OPTIONAL {{ ?c rdfs:label ?l FILTER(LANG(?l)="fr" || LANG(?l)="en") }} }}"""):
        c=b['c']['value'].split('/')[-1]
        if 'p' in b: edges.append((c,b['p']['value'].split('/')[-1]))
        if 'l' in b: lab.setdefault(c,{})[b['l']['xml:lang']]=b['l']['value']
json.dump({'edges':sorted(set(edges)),'lab':lab},open('classes_tree.json','w'),ensure_ascii=False)
print(len(edges))

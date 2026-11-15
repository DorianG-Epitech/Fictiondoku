import json,collections
d=json.load(open('raw_chars.json'));w=json.load(open('raw_works.json'))
items=json.load(open('items.json'))
lab=w['lab']; L=lambda q:(lab.get(q,{}).get('fr') or lab.get(q,{}).get('en') or q)
T=d['triples']
for p in ['P21','P31','P1080','P8345','P1441','P170','P106','P4584','P172','P27','P463']:
    c=collections.Counter(v for x,pp,v in T if pp==p and items[x]>=6)
    print('==',p,len(c)); print('; '.join(f'{L(k)}[{k}]:{n}' for k,n in c.most_common(70 if p not in('P21',) else 8)))
wc=collections.Counter(v for x,p,v in w['wt'] if p=='P31')
print('== work P31'); print('; '.join(f'{L(k)}[{k}]:{n}' for k,n in wc.most_common(80)))
wc=collections.Counter(v for x,p,v in w['wt'] if p=='P495')
print('== work P495'); print('; '.join(f'{L(k)}[{k}]:{n}' for k,n in wc.most_common(20)))

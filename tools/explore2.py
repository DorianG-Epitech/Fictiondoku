import json,collections,re
d=json.load(open('raw_chars.json'));ct=json.load(open('classes_tree.json'));items=json.load(open('items.json'))
par=collections.defaultdict(set)
for c,p in ct['edges']: par[c].add(p)
lab=ct['lab'];L=lambda q:(lab.get(q,{}).get('fr') or lab.get(q,{}).get('en') or q)
memo={}
def anc(c,stack=()):
    if c in memo: return memo[c]
    s={c}
    for p in par[c]:
        if p not in stack: s|=anc(p,stack+(c,))
    memo[c]=s;return s
cnt=collections.Counter()
P31=collections.defaultdict(set)
for x,p,v in d['triples']:
    if p=='P31': P31[x].add(v)
for x,cs in P31.items():
    if items[x]<6: continue
    a=set()
    for c in cs: a|=anc(c)
    for c in a: cnt[c]+=1
print('; '.join(f'{L(k)}[{k}]:{n}' for k,n in cnt.most_common(250)))

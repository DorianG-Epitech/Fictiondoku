import requests,json,time,sys,collections
H={'User-Agent':'fictiondoku/0.2 (personal game project)','Accept':'text/tab-separated-values'}
def tsv(query,timeout=120):
    for i in range(4):
        try:
            r=requests.post('https://query.wikidata.org/sparql',data={'query':query},headers=H,timeout=timeout)
            if r.status_code==200:
                lines=r.text.rstrip('\n').split('\n')
                return [l.split('\t') for l in lines[1:]]
            print('ERR',r.status_code,r.text[:200],file=sys.stderr)
        except Exception as e: print('EXC',e,file=sys.stderr)
        time.sleep(8)
    return None
cls=json.load(open('allclasses.json'))
big=set()
items={}
def run(ch):
    v=' '.join('wd:'+c for c in ch)
    rows=tsv(f"SELECT ?x ?s WHERE {{ VALUES ?cls {{ {v} }} ?x wdt:P31 ?cls . ?x wikibase:sitelinks ?s . }}")
    if rows is None:
        if len(ch)==1: big.add(ch[0]); return
        m=len(ch)//2; run(ch[:m]); run(ch[m:]); return
    for x,s in rows: items[x.strip('<>').split('/')[-1]]=int(s.split('^^')[0].strip('"'))
BIG=['Q15632617','Q95074','Q15773317','Q15773347','Q3658341','Q1114461','Q15711870','Q1569167','Q80447738','Q87576284']
rest=[c for c in cls if c not in BIG]
for i in range(0,len(rest),300):
    run(rest[i:i+300]); print(i,len(items),flush=True)
for c in BIG+sorted(big):
    off=0
    while True:
        rows=tsv(f"SELECT ?x ?s WHERE {{ ?x wdt:P31 wd:{c} . ?x wikibase:sitelinks ?s . }} ORDER BY ?x LIMIT 20000 OFFSET {off}",timeout=180)
        if rows is None: print('FAIL',c,off); break
        for x,s in rows: items[x.strip('<>').split('/')[-1]]=int(s.split('^^')[0].strip('"'))
        print(c,off,len(rows),len(items),flush=True)
        if len(rows)<20000: break
        off+=20000
json.dump(items,open('items_all.json','w'))
c=collections.Counter()
for s in items.values():
    for t in [0,1,2,3,4]:
        if s>=t:c[t]+=1
print(sorted(c.items()))

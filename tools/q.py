import requests,sys,json,time
def q(query,timeout=70):
    for i in range(4):
        r=requests.get('https://query.wikidata.org/sparql',params={'query':query,'format':'json'},headers={'User-Agent':'fictiondoku/0.1 (personal game project)'},timeout=timeout)
        if r.status_code==200: return r.json()['results']['bindings']
        print('ERR',r.status_code,r.text[:300],file=sys.stderr); time.sleep(5)
    raise SystemExit('fail')

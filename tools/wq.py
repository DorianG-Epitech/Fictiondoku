import requests,time,sys
H={'User-Agent':'fictiondoku/0.2 (personal game project; dorian)','Accept':'application/sparql-results+json'}
def q(query,timeout=120):
    for i in range(6):
        try:
            r=requests.post('https://query.wikidata.org/sparql',data={'query':query},headers=H,timeout=timeout)
            if r.status_code==200: return r.json()['results']['bindings']
            print('ERR',r.status_code,r.text[:150],file=sys.stderr)
            if r.status_code==429: time.sleep(30)
        except Exception as e: print('EXC',str(e)[:150],file=sys.stderr)
        time.sleep(5+5*i)
    return None

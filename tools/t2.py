from q import q
import json
res=q("""SELECT DISTINCT ?cls WHERE { ?cls wdt:P279* wd:Q95074 . }""",timeout=90)
cls=[b['cls']['value'].split('/')[-1] for b in res]
print(len(cls))
json.dump(cls,open('allclasses.json','w'))

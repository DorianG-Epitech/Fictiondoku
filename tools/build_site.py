import json
d=json.load(open('../data/fictiondoku_clean.json'))
catids=[c['id'] for c in d['cats']]
DESC={'media':"Média de la toute première apparition du personnage.",'epoque':"Année de la première apparition du personnage.",'pays':"Pays d'origine de l'œuvre où le personnage est né.",'genre':"Genre de l'œuvre d'origine / de la franchise.",'lettre':"Nom affiché du personnage (articles Le/La/Les/The ignorés).",'nom':"Basé sur le nom affiché du personnage.",'genre_p':"Genre du personnage.",'univers':"Le personnage appartient à cet univers / cette franchise.",'equipe':"Membre (à un moment) de cette équipe.",'createur':"Personnage créé ou cocréé par cette personne.",'type':"Nature du personnage.",'metier':"Occupation / rôle du personnage."}
U=sorted({c['universe'] for c in d['chars']})
UI={u:i for i,u in enumerate(U)}
data={'cats':[[c['id'],c['label'],c['group']] for c in d['cats']],'desc':DESC,'univ':U,
 'chars':[[c['name'],'|'.join(c['aliases']),c['sl'],[catids.index(x) for x in c['cats']],UI[c['universe']]] for c in d['chars']]}
js=json.dumps(data,ensure_ascii=False,separators=(',',':'))
open('../docs/data.json','w').write(js)
html=open('template.html').read().replace('/*__DATA__*/null',js).replace('/*__CORE__*/',open('core.js').read())
open('../docs/index.html','w').write(html)
print(len(js))

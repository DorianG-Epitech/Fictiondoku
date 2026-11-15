import json,collections,re,unicodedata
d=json.load(open('raw_chars_all.json'));w=json.load(open('raw_works_all.json'));ct=json.load(open('classes_tree.json'))
items=json.load(open('items_all.json'))
lab=dict(w['lab']);
for k,v in ct['lab'].items(): lab.setdefault(k,v)
def Ls(q):
    e=lab.get(q,{}); return [s for s in (e.get('fr'),e.get('en')) if s]
def L(q): s=Ls(q); return s[0] if s else q
par=collections.defaultdict(set)
for c,p in ct['edges']: par[c].add(p)
memo={}
def anc(c,stack=()):
    if c in memo: return memo[c]
    s={c}
    for p in par[c]:
        if p not in stack: s|=anc(p,stack+(c,))
    memo[c]=s;return s
CP=collections.defaultdict(lambda:collections.defaultdict(list))
for x,p,v in d['triples']: CP[x][p].append(v)
WP=collections.defaultdict(lambda:collections.defaultdict(list))
for x,p,v in w['wt']: WP[x][p].append(v)
_hop=json.load(open('raw_hop.json'))
for x,p,v in _hop['wt']:
    if v not in WP[x][p]: WP[x][p].append(v)
for k,v in _hop['lab'].items(): lab.setdefault(k,v)
def year(v):
    m=re.match(r'^(-?\d{4})-',v); return int(m.group(1)) if m else None
CROSS_RE=re.compile(r'Smash Bros|Kingdom Hearts|\bvs\.?\b|\bVersus\b|LEGO|Lego|Fortnite|MultiVersus|Ready Player|Space Jam|Qui veut la peau|Who Framed|Scribblenauts|Project X Zone|All-Stars|Mario Kart|Mario Party|Mario & Sonic|Super Robot|Jump Force|J-Stars|Ralph|Wreck-It|Disney Infinity|Cross ?Edge|Dissidia|Teppen|Brawlhalla|Sonic & Sega|Marvel Contest|Lego',re.I)
CROSSOVER_Q='Q1047299'  # placeholder
def is_cross(wq):
    if any(L(g)=='cross-over' for g in WP[wq]['P136']): return True
    return any(CROSS_RE.search(s) for s in Ls(wq))
# work type classification
def wtypes(wq):
    t=set(); labs=' | '.join(L(c) for c in WP[wq]['P31'])
    jp='Q17' in WP[wq]['P495']
    if re.search(r'jeu vidéo|jeux vidéo|esports|extension de jeu',labs): t.add('jv')
    if re.search(r'manga|anime|animé|animation japonaise|light novel|original video animation',labs): t.add('manga')
    if re.search(r'bande dessinée|comic|strip',labs,re.I): t.add('bd')
    if re.search(r'animation|animé|dessin animé',labs) and not jp: t.add('anim')
    if re.search(r'animation',labs) and jp: t.add('manga')
    if re.search(r'série télévisée|épisode|mini-série|limited series|saison de série|pilote|web-série|programme télévisé|feuilleton|sitcom',labs) : t.add('tv')
    if re.search(r'\bfilm\b|cinématographique|court métrage|téléfilm',labs) and 'animation' not in labs: t.add('film')
    if re.search(r'littéraire|roman|livre|nouvelle|conte|écrite|poème|book|novel|cycle|épopée|saga',labs,re.I) and 'light novel' not in labs: t.add('livre')
    if re.search(r'théâtr|pièce|opéra|dramatique|dramatico|comédie musicale|ballet',labs): t.add('theatre')
    return t
CLASS_MED={'Q3658341':'livre','Q1114461':'bd','Q65967030':'bd','Q15773317':'tv','Q15773347':'film','Q15711870':'anim','Q1569167':'jv','Q80447738':'manga','Q87576284':'manga','Q3375722':'theatre','Q50386450':'theatre','Q63975020':'theatre'}
def norm(s):
    s=unicodedata.normalize('NFKD',s.lower()); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
GENERIC=re.compile(r"#\d|\d$|^(the|a|an|un|une|le|la|les|der|die|das|el|il)\s|\b(of|de|du|des|von)\s|\b(mother|father|son|daughter|wife|husband|brother|sister|servant|guard|man|woman|girl|boy|nurse|doctor|officer|soldier|maid|waiter|priest|policeman|reporter|voice|narrator|chorus|choeur|mère|père|fils|fille|femme|homme|serviteur|garde|soldat|monger|grandfather|grandmother|clerk|thug|first|second|third|bartender|driver|cop|receptionist|customer|passenger|stranger|bystander|announcer|henchman|goon|villager|townsperson|citizen|worker|kid|and|et)\b|&| \d",re.I)

def ulabel(q):
    e=lab.get(q,{}); s=e.get('fr') or e.get('en')
    if not s or re.match(r'^Q\d+$',s): return None
    s=re.sub(r'\s*\((franchise|série|series|media franchise|franchise médiatique|série de jeux vidéo|video game series|univers de fiction|fictional universe)[^)]*\)$','',s,flags=re.I)
    s=re.sub(r'^(franchise|univers de fiction|univers fictif)\s+','',s,flags=re.I)
    s=re.sub(r'^(univers|franchise)\s+(de |d\'|du |des )?','',s,flags=re.I) if re.match(r'^(univers|franchise)\s',s,re.I) and len(s.split())>1 else s
    s=s.strip()
    return (s[0].upper()+s[1:]) if s else None
UBAD=re.compile(r'^(liste|list of|catégorie|category|wikimedia|personnage|character)',re.I)
def ok_u(q):
    if is_cross(q): return None
    l=ulabel(q)
    if not l or UBAD.match(l): return None
    return l
def univ_of_work(q):
    for p in ('P8345','P1080'):
        for v in WP[q][p]:
            l=ok_u(v)
            if l: return l
    for v in WP[q]['P179']:
        for p in ('P8345','P1080'):
            for u in WP[v][p]:
                l=ok_u(u)
                if l: return l
        l=ok_u(v)
        if l: return l
    return ok_u(q)
MEDW=re.compile(r'^(fiction|bande dessinée|cinéma|série|jeu|jeux|anime|manga|animation|théâtre|opéra|comédie|roman|mascotte|littérature|radio|télévision|conte de fées|légende$|webcomic|light novel|film)',re.I)
def class_univ(cls):
    for c in cls:
        l=(lab.get(c,{}).get('fr') or '')
        m=re.match(r"^personnage (?:de la |du |de l'|des |de |d')(.+)$",l)
        if m and not MEDW.match(m.group(1)):
            t=m.group(1).strip(); return t[0].upper()+t[1:]
    return None
LEGW=re.compile(r'légende|mythologie|cycle|matière de|folklore|Bible|épopée',re.I)
def wyear(q):
    ys=[y for p in ('P577','P571') for y in map(year,WP[q][p]) if y]
    if ys: return min(ys)
    return -9999 if any(LEGW.search(x) for x in Ls(q)) else 99999
def universe(P,cls=()):
    for p in ('P8345','P1080'):
        c=collections.Counter(l for l in (ok_u(v) for v in P[p]) if l)
        if c: return c.most_common(1)[0][0]
    for p in ('P4584','P1441'):
        ws=[v for v in P[p] if univ_of_work(v)]
        c=collections.Counter(univ_of_work(v) for v in ws)
        if c:
            top=c.most_common(1)[0]
            if top[1]==1 and len(ws)>=3:
                cu=class_univ(cls)
                if cu: return cu
                return univ_of_work(min(ws,key=wyear))
            return top[0]
    cu=class_univ(cls)
    if cu: return cu
    for p in ('P144','P463'):
        c=collections.Counter(l for l in (univ_of_work(v) for v in P[p]) if l)
        if c: return c.most_common(1)[0][0]
    return None
chars=[]
for x,sl in items.items():
    labs=d['labels'].get(x,[])
    fr=[v for k,l,v in labs if k=='L' and l=='fr']; en=[v for k,l,v in labs if k=='L' and l=='en']
    name=(fr or en or [None])[0]
    if not name or re.match(r'^Q\d+$',name): continue
    P=CP[x]
    cls=set(P['P31'])
    if cls & {'Q14514600','Q5','Q2927074'} and len(cls)==1: continue  # groups, real humans, memes
    if re.search(r'^(liste|list of|famille|family|clan)\b',name,re.I): continue
    if sl<=3 and cls & {'Q340069','Q116143324'}: continue
    name=re.sub(r'\s*\([^)]*\)$','',name).strip() or name
    if sl<=1 and (len(name)>40 or re.search(r'Digimon|Pendulum|Version',name)): continue
    if sl==0:
        if cls & {'Q50386450','Q63975020','Q3375722','Q100708514'} and not cls & {'Q15711870','Q80447738','Q87576284','Q1569167'}: continue  # rôles d'opéra/comédie musicale/théâtre, géants de procession
        if GENERIC.search(name) or name==name.lower(): continue
        if not (P['P1441'] or P['P4584'] or P['P1080'] or P['P8345'] or P['P170']): continue
    aliases=sorted({v for k,l,v in labs if v!=name and 1<len(v)<60})
    ancs=set()
    for c in cls: ancs|=anc(c)
    def expand(qs):
        out=set(qs)
        for q in qs:
            for p in ('P8345','P1080','P179','P361'): out|={v for v in WP[q][p] if not is_cross(v)}
        return out
    prim=[q for p in ('P1080','P8345','P4584') for q in P[p] if not is_cross(q)]
    prim_x=expand(prim)
    ctx_univ=[s for q in prim_x for s in Ls(q)]+[s for c in cls for s in Ls(c)]+[s for q in P['P463'] for s in Ls(q)]
    works_nc=[q for q in P['P1441'] if not is_cross(q)]
    work_ctx=[[s for v in expand([q]) for s in Ls(v)] for q in works_nc]
    ctx_pub=[s for q in prim for p in ('P123','P272') for v in WP[q][p] for s in Ls(v)]
    work_pub=[[s for p in ('P123','P272') for v in WP[q][p] for s in Ls(v)] for q in works_nc]
    ctx_net=[]
    occ=[s for p in ('P106','P39') for q in P[p] for s in Ls(q)]
    clslabs=[s for c in ancs for s in Ls(c)]
    # dates
    yrs=[]
    for q in P['P4584']+P['P1441']:
        for p in ('P577','P571','P580'):
            yrs+= [y for y in map(year,WP[q][p]) if y]
    for p in ('P571',):
        yrs+=[y for y in map(year,P[p]) if y]
    first=min(yrs) if yrs else None
    # origin works (genres computed after)
    orig=[q for q in P['P4584'] if not is_cross(q)]
    if not orig:
        dated=[]
        for q in P['P1441']:
            if is_cross(q): continue
            ys=[y for p in ('P577','P571') for y in map(year,WP[q][p]) if y]
            if ys: dated.append((min(ys),q))
        if dated:
            m=min(dated)[0]; orig=[q for y,q in dated if y==m]
    gsrc=set(orig)|set(prim_x)
    genres=[L(g) for q in gsrc for g in WP[q]['P136']]
    work_gen=[[L(g) for g in WP[q]['P136']] for q in works_nc]
    med=set()
    for q in orig: med|=wtypes(q)
    if not med:
      for c in cls:
        if c in CLASS_MED: med.add(CLASS_MED[c])
        else:
            l=L(c)
            if re.search('jeu vidéo',l): med.add('jv')
            if re.search('manga|anime',l): med.add('manga')
    # country
    ctry=set()
    for src in (P['P4584'],P['P8345'],P['P1080']):
        for q in src: ctry|=set(WP[q]['P495'])
        if ctry: break
    if not ctry:
        c=collections.Counter(v for q in P['P1441'] if not is_cross(q) for v in WP[q]['P495'])
        if c:
            m=max(c.values()); ctry={k for k,n in c.items() if n==m}
    chars.append(dict(id=x,name=name,aliases=aliases,sl=sl,cls=sorted(cls),ancs=ancs,P=P,ctx_univ=ctx_univ,ctx_pub=ctx_pub,ctx_net=ctx_net,genres=genres,work_ctx=work_ctx,work_pub=work_pub,work_gen=work_gen,occ=occ,clslabs=clslabs,first=first,med=med,ctry=ctry,works_all=P['P1441'],creators=[L(c) for c in P['P170']],gender=set(P['P21']),univ=universe(P,cls),uctx=' | '.join([s for q in prim_x for s in Ls(q)]+ctx_pub)))
print('chars',len(chars))
import pickle; pickle.dump(chars,open('chars.pkl','wb'))

import pickle,re,json,collections,unicodedata
chars=pickle.load(open('chars.pkl','rb'))
def R(p,f=re.I): return re.compile(p,f)
def any_re(rx,lst): return any(rx.search(s) for s in lst)
def frac(c,key,rx,th=0.34):
    W=c[key]
    if not W: return False
    k=sum(1 for ws in W if any_re(rx,ws)); return k>=1 and k/len(W)>=th
def univ(rx): rx=R(rx); return lambda c: any_re(rx,c['ctx_univ']) or frac(c,'work_ctx',rx)
def univpub(rx,pub): rx=R(rx); px=R(pub); return lambda c: any_re(rx,c['ctx_univ']) or any_re(px,c['ctx_pub']) or frac(c,'work_ctx',rx) or frac(c,'work_pub',px)
def genre(rx):
    rx=R(rx)
    def f(c):
        if c['genres']: return any_re(rx,c['genres'])
        return frac(c,'work_gen',rx)
    return f
def occ(rx): rx=R(rx); return lambda c: any_re(rx,c['occ'])
def anc(*qs): s=set(qs); return lambda c: bool(c['ancs']&s)
def clsre(rx): rx=R(rx); return lambda c: any_re(rx,c['clslabs'])
OR=lambda *fs: (lambda c: any(f(c) for f in fs))
def first_word(c): return c['name']
def nm(c):
    s=unicodedata.normalize('NFKD',c['name']); return ''.join(ch for ch in s if not unicodedata.combining(ch))
TITLE=R(r"^(Docteur|Dr\.?|Doctor|Doc|Capitaine|Captain|Professeur|Professor|Prof\.?|Roi|Reine|King|Queen|Prince|Princesse|Princess|Lord|Lady|Sir|Mister|Mr\.?|Mrs\.?|Miss|Madame|Mme|Monsieur|M\.|Général|General|Colonel|Commandant|Comte|Comtesse|Baron|Baronne|Sergent|Sergeant|Lieutenant|Inspecteur|Inspector|Agent|Oncle|Uncle|Tante|Aunt|Père|Mère|Frère|Sœur|Maître|Master|Empereur|Emperor|Duc|Duchesse|Commissaire|Shérif|Sheriff|Major|Amiral|Admiral|Saint|Mademoiselle|Grand-mère|Grand-père|Granny|Papa|Maman)\b")
def initials(c):
    ws=[x for x in re.split(r"[\s\-]+",nm(c)) if x and x[0].isalpha()]
    return len(ws)>=2 and ws[0][0].lower()==ws[-1][0].lower() and not TITLE.match(c['name'])
NONHUMAN_ANIMAL={'Q2369882','Q27301300','Q15832079','Q65048226','Q27276270','Q27301047','Q20965826','Q27132946','Q20723931','Q27104461','Q113483678','Q58817999','Q20089147','Q19833563','Q96789659','Q21009831','Q21009825','Q27304634','Q15831457','Q15720625','Q27120684','Q3247351','Q27303980','Q2962925','Q24668268','Q27267085','Q8030589','Q27301420','Q27301864','Q27301467','Q27302054','Q27303911','Q19594644','Q27304428','Q99768640','Q88552881','Q27304565'}
GENDERM={'Q6581097','Q44148'};GENDERF={'Q6581072','Q43445'}
CATS=[
 # (id, label, group, fn)
 ('marvel','Marvel','univers',univpub(r'Marvel|Terre-616|\bX-Men\b|Vengeurs|Avengers|Quatre Fantastiques','Marvel')),
 ('dc','DC Comics','univers',univpub(r'DC Comics|Univers DC|DC Universe|DC Extended|Batman|Superman|Ligue des justiciers|Justice League|Wonder Woman|Green Lantern|Smallville|Gotham|Teen Titans|Arrowverse|Black Lantern|Society of Super Villains','^DC ')),
 ('starwars','Star Wars','univers',univ(r'Star Wars|Guerre des étoiles|\bJedi\b|\bSith\b|Mandalorian|Clone Wars|Rogue One|Obi-Wan|Ahsoka|Boba Fett|Alliance Rebelle|Empire galactique|République galactique')),
 ('startrek','Star Trek','univers',univ(r'Star Trek')),
 ('hp','Harry Potter','univers',univ(r'Harry Potter|Poudlard|Hogwarts|Monde des sorciers|Animaux fantastiques|Fantastic Beasts|Gryffondor|Serpentard|Serdaigle|Poufsouffle|Mangemort|Ordre du Phénix|Armée de Dumbledore|sang-pur|sang-mêlé|Wizarding')),
 ('tolkien','Tolkien (Terre du Milieu)','univers',univ(r'Tolkien|Seigneur des [Aa]nneaux|Silmarillion|\bHobbit|Terre du Milieu|Middle-earth|\bAinur\b|\bValar\b|\bMaiar\b|Ñoldor|Sindar|Númenor|Rohirrim|Contes et légendes inachevés|Les Anneaux de pouvoir')),
 ('disney','Disney / Pixar','univers',univpub(r'Disney|Pixar',r'Disney|Pixar')),
 ('simpsons','Les Simpson','univers',univ(r'Simpson')),
 ('nintendo','Nintendo','univers',univpub(r'Nintendo|Super Mario|Zelda|\bKirby\b|Metroid|Donkey Kong|Pokémon','^Nintendo')),
 ('mario','Univers Mario','univers',univ(r'\bMario\b(?! Puzo)|Donkey Kong|\bYoshi\b|\bWario\b')),
 ('sega','Sega / Sonic','univers',univpub(r'Sonic|Sega','^Sega')),
 ('pokemon','Pokémon (dresseurs & co)','univers',univ(r'Pokémon')),
 ('dbz','Dragon Ball','univers',univ(r'Dragon Ball')),
 ('naruto','Naruto','univers',univ(r'Naruto|Boruto|Akatsuki|Konoha')),
 ('onepiece','One Piece','univers',univ(r'One Piece|Chapeau de paille')),
 ('got','Game of Thrones','univers',univ(r'Trône de fer|Game of Thrones|House of the Dragon|Sept Couronnes|Westeros')),
 ('doctorwho','Doctor Who','univers',univ(r'Doctor Who|Whoniverse|Torchwood|Gallifrey|Sarah Jane')),
 ('looney','Looney Tunes','univers',univ(r'Looney Tunes|Merrie Melodies')),
 ('ff','Final Fantasy','univers',univ(r'Final Fantasy')),
 ('combat','Jeu de combat','univers',lambda c: ('jv' in c['med'] and genre(r'jeu vidéo de combat|jeu de combat')(c)) or univ(r'Mortal Kombat|Street Fighter|Tekken|King of Fighters|Fatal Fury|Soulcalibur|Dead or Alive|Virtua Fighter|Guilty Gear|BlazBlue|Art of Fighting|Killer Instinct')(c)),
 ('smash','Jouable dans Super Smash Bros.','univers',lambda c: any(re.search('Smash Bros',L) for q in c['works_all'] for L in LAB.get(q,[]))),
 ('shakespeare','Personnage de Shakespeare','createur',lambda c: 'William Shakespeare' in c['creators']),
 ('stanlee','Créé par Stan Lee','createur',lambda c: 'Stan Lee' in c['creators']),
 ('kirby','Créé par Jack Kirby','createur',lambda c: 'Jack Kirby' in c['creators']),
 ('avengers','Membre des Avengers','equipe',lambda c: 'Q322646' in c['P']['P463']),
 ('jla','Membre de la Justice League','equipe',lambda c: 'Q735744' in c['P']['P463']),
 ('xmen','Membre des X-Men','equipe',lambda c: 'Q128452' in c['P']['P463']),
 ('m_jv','Origine : jeu vidéo','media',lambda c: 'jv' in c['med']),
 ('m_manga','Origine : manga / anime','media',lambda c: 'manga' in c['med']),
 ('m_bd','Origine : BD / comics','media',lambda c: 'bd' in c['med']),
 ('m_livre','Origine : roman / littérature','media',lambda c: 'livre' in c['med']),
 ('m_film','Origine : film','media',lambda c: 'film' in c['med']),
 ('m_anim','Origine : dessin animé','media',lambda c: 'anim' in c['med']),
 ('m_tv','Origine : série télé','media',lambda c: 'tv' in c['med']),
 ('m_theatre','Origine : théâtre / opéra','media',lambda c: 'theatre' in c['med']),
 ('g_scifi','Science-fiction','genre',genre(r'science-fiction')),
 ('g_fantasy','Fantasy','genre',genre(r'fantasy')),
 ('g_horreur','Horreur','genre',genre(r'horreur|horror')),
 ('g_comedie','Comédie / sitcom','genre',genre(r'comédie|comique|sitcom')),
 ('g_policier','Policier / crime','genre',genre(r'policier|criminel|détective|crime|enquête')),
 ('c_us','Création américaine','pays',lambda c: 'Q30' in c['ctry']),
 ('c_jp','Création japonaise','pays',lambda c: 'Q17' in c['ctry']),
 ('c_uk','Création britannique','pays',lambda c: bool(c['ctry']&{'Q145','Q174193','Q21','Q161885','Q179876','Q22'})),
 ('c_frbe','Création française ou belge','pays',lambda c: bool(c['ctry']&{'Q142','Q31','Q70972'})),
 ('e_1950','Apparu avant 1950','epoque',lambda c: c['first'] is not None and c['first']<1950),
 ('e_5070','Apparu entre 1950 et 1979','epoque',lambda c: c['first'] is not None and 1950<=c['first']<1980),
 ('e_80','Apparu dans les années 80','epoque',lambda c: c['first'] is not None and 1980<=c['first']<1990),
 ('e_90','Apparu dans les années 90','epoque',lambda c: c['first'] is not None and 1990<=c['first']<2000),
 ('e_00','Apparu dans les années 2000','epoque',lambda c: c['first'] is not None and 2000<=c['first']<2010),
 ('e_10','Apparu en 2010 ou après','epoque',lambda c: c['first'] is not None and c['first']>=2010),
 ('sexe_m','Personnage masculin','genre_p',lambda c: bool(c['gender']&GENDERM)),
 ('sexe_f','Personnage féminin','genre_p',lambda c: bool(c['gender']&GENDERF)),
 ('t_animal','Animal','type',lambda c: bool(c['ancs']&NONHUMAN_ANIMAL) and 'Q15632617' not in c['cls']),
 ('t_robot','Robot, androïde ou IA','type',OR(anc('Q18327510','Q22074483','Q66481339','Q102408544','Q11321874','Q126351','Q1050840'),clsre(r'robot|androïde|android|intelligence artificielle|gynoïde'))),
 ('t_alien','Extraterrestre','type',OR(lambda c: bool(c['ancs']&{'Q89050913','Q89050960','Q1307329','Q110625676','Q6439708'}) and 'Q15632617' not in c['cls'],clsre(r'Kryptonien|Vulcain|Klingon|Saiyan|Seigneur du Temps|Time Lord'),lambda c: any_re(R(r'Vulcain|Klingon|Saiyan|Kryptonien|Férengi|Cardassien|Bétazoïde|Romulien|Asgardien|Time Lord'),[s for q in c['P']['P172'] for s in LAB.get(q,[])]))),
 ('t_surnat','Créature fantastique (elfe, vampire, démon…)','type',(lambda f: lambda c: f(c) and not (set(c['cls'])&{'Q15632617','Q15298259'}))(OR(anc('Q30061294','Q203904','Q3050815','Q338688','Q10477881','Q74359','Q2621839','Q42056878','Q8028','Q30318131','Q18616317','Q17624054','Q5174137'),clsre(r'vampire|démon|fantôme|elfe|nain|dragon|loup-garou|werewolf|fée|mort-vivant|zombie|géant|ange|déité|dieu|kaiju|esprit|sorcière|troll|gobelin|ogre|monstre')))),
 ('t_pouvoirs','Doté de super-pouvoirs','type',OR(anc('Q7643449','Q2248485','Q14831768','Q1094617','Q3855553','Q1975749','Q7575652','Q96239200','Q76450109'),occ(r'super-héros|super-vilain'),clsre(r'mutant|méta-humain|superhumain|super-héros'))),
 ('o_hero','Super-héros','metier',OR(occ(r'^super-héros|superhero'),clsre(r'^super-héros$'))),
 ('o_mage','Magicien ou sorcier','metier',OR(anc('Q148401','Q15298259','Q16153191'),occ(r'magicien|sorci|mage\b|wizard|witch|nécromancien|druide'),clsre(r'sorci|magicien|wizard|witch'))),
 ('o_crim','Criminel ou méchant','metier',OR(occ(r'criminel|meurtrier|tueur|assassin|voleur|voleuse|escroc|terroriste|trafiquant|gangster|chef de bande|mafi|braqueur|hors-la-loi|cambrioleur|super-vilain|contrebandier|parrain'),lambda c: any_re(R(r'Society of Super Villains|Confrérie des mauvais|Injustice League|Sinistres Six|Maîtres du mal|Legion of Doom|Mangemort|\bSith\b|Akatsuki|Escadron Suicide|Club des Damnés|HYDRA|Frightful Four|Secret Six'),[s for q in c['P']['P463'] for s in LAB.get(q,[])]))),
 ('o_detective','Détective, policier ou enquêteur','metier',OR(occ(r'détective|inspect|policier|policière|enquêt|agent du FBI|shérif|commissaire|police|agent spécial|agent fédéral'),clsre(r'détective'))),
 ('o_soldat','Soldat, militaire ou guerrier','metier',occ(r'\bsoldat|\bmilitaire|\bofficier|\bguerri|(?<!directeur )(?<!directrice )\bgénéral\b|\bchevalier|\bsamouraï|\bmarine\b|\bcommandant|\bcolonel|\bamiral|\bsergent|\blieutenant|\bmercenaire|\bcommando|\bsoldier')),
 ('o_combat','Épéiste, ninja ou artiste martial','metier',occ(r'\bépéiste|\bescrim|\bninja|\bsamouraï|arts martiaux|\bkaraté|kung-fu|\bboxeu|\blutteu|\bcatcheu|\barcher\b|\barchère|\bswordsman|\bmartial artist')),
 ('o_science','Scientifique, médecin ou inventeur','metier',occ(r'scientifique|médecin|chirurgien|inventeu|chimiste|physicien|biologiste|ingénieu|savant|généticien|psychiatre|psychologue|astronome|archéologue|infirmi|mathématicien|roboticien')),
 ('o_eleve','Élève ou étudiant','metier',OR(occ(r'étudiant|lycéen|élève|écolier|collégien'),anc('Q33295419'))),
 ('o_royal','Roi, reine, prince ou princesse','metier',OR(occ(r'\broi\b|\breine\b|\bprince|monarque|empereur|impératrice|pharaon|souverain|\bseigneur\b(?! de guerre)(?! du crime)|\bnoble\b|\bduc\b|duchesse|comte|aristocrat|tsar|sultan|chef d\'État|régent'),clsre(r'monarch|roi de fiction|chef d\'État|princesse|prince'),lambda c: bool(re.match(r'^(Roi|Reine|King|Queen|Prince|Princesse|Princess|Empereur|Emperor|Impératrice|Lord)\b',c['name'])))),
 ('o_pirate','Pirate','metier',OR(occ(r'pirate|corsaire|flibustier'),lambda c: any_re(R(r'pirate|Chapeau de paille'),[s for q in c['P']['P463'] for s in LAB.get(q,[])]))),
 ('o_pilote','Pilote, aviateur ou astronaute','metier',occ(r'pilote|aviat|astronaut|cosmonaut|spationaut')),
 ('o_time','Voyageur dans le temps','metier',occ(r'voyageur dans le temps|time travel')),
 ('n_seul','Nom en un seul mot','nom',lambda c: not re.search(r"[\s\-]",c['name'].strip())),
 ('n_titre','Titre dans le nom (Docteur, Capitaine, Roi…)','nom',lambda c: bool(TITLE.match(c['name']))),
 ('n_allit','Initiales identiques (ex. Peter Parker)','nom',initials),
]
for letter in 'ABCDEGHJKLMPRST':
    CATS.append((f'l_{letter}',f'Nom commençant par {letter}','lettre',(lambda L_: lambda c: re.sub(r'^(Le |La |Les |L\'|The )','',nm(c)).upper().startswith(L_))(letter)))
LAB={}
w=json.load(open('raw_works.json'))
for k,v in w['lab'].items(): LAB[k]=[s for s in (v.get('fr'),v.get('en')) if s]

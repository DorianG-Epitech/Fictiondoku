from cats import *
mem={cid:[] for cid,*_ in CATS}
for i,c in enumerate(chars):
    c['cats']=[cid for cid,lab_,g,f in CATS if f(c)]
    for cid in c['cats']: mem[cid].append(i)
N8=lambda ids: sum(1 for i in ids if chars[i]['sl']>=8)
for cid,lab_,g,f in CATS:
    print(f'{cid:12s} {len(mem[cid]):5d} {N8(mem[cid]):5d}  ',', '.join(chars[i]['name'] for i in sorted(mem[cid],key=lambda i:-chars[i]['sl'])[:8]))
nocat=[c for c in chars if not [x for x in c['cats'] if not x.startswith(('l_','n_','sexe'))]]
print('no meaningful cats',len(nocat), [c['name'] for c in sorted(nocat,key=lambda c:-c['sl'])[:30]])
pickle.dump((chars,mem),open('assigned.pkl','wb'))

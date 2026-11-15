import pickle,itertools,numpy as np,json,math
out,catids=pickle.load(open('final.pkl','rb'))
K=len(catids); idx={c:i for i,c in enumerate(catids)}
grp={c['id']:c['group'] for c in json.load(open('../data/fictiondoku_clean.json'))['cats']}
M=np.zeros((len(out),K),bool)
for i,c in enumerate(out):
    for x in c['cats']: M[i,idx[x]]=True
sl=np.array([c['sl'] for c in out])
A=M.astype(np.int32); N8=M[sl>=8].astype(np.int32)
pair_all=A.T@A; pair8=N8.T@N8; n_all=np.diag(pair_all)
def compat(minc,ok):
    C=(pair8>=minc)&(pair_all<=0.85*np.minimum.outer(n_all,n_all))
    np.fill_diagonal(C,False)
    C&=np.outer(ok,ok)
    # forbid same 'lettre/nom' pairs and same group for some groups
    for i in range(K):
        for j in range(K):
            gi,gj=grp[catids[i]],grp[catids[j]]
            if gi==gj and gi in('lettre','nom','epoque','genre_p','pays','media'): C[i,j]=False
            if {gi,gj}<= {'lettre','nom'}: C[i,j]=False
    return C
def count(C):
    tot=0
    for r in itertools.combinations(range(K),3):
        if C[r[0],r[1]] or C[r[0],r[2]] or C[r[1],r[2]]: pass
        cand=np.where(C[r[0]]&C[r[1]]&C[r[2]])[0]
        k=len(cand)
        if k>=3: tot+=k*(k-1)*(k-2)//6
    return tot//2  # rows/cols swap
ok_all=np.ones(K,bool)
big=np.array([grp[c] not in('lettre','nom','createur','equipe') and pair8[i,i]>=40 for i,c in enumerate(catids)])
res={}
for name,minc,ok in [('facile',12,big),('normal',5,ok_all),('difficile',3,ok_all)]:
    C=compat(minc,ok); res[name]=count(C); print(name,res[name],'usable cats',int((C.sum(1)>=3).sum()))
json.dump(res,open('../data/grid_counts.json','w'))

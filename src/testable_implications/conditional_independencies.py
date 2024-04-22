import itertools

from src.inference.utils.graph_utils import GraphUtils as gu, sortByName
from src.inference.utils.set_utils import SetUtils as su
from src.common.object_utils import ObjectUtils as ou
from src.inference.utils.graph_utils import compareNames
from src.adjustment.adjustment_sets_utils import writeNodeNames
from src.path_analysis.d_separation import DSeparation

def isSymmetric(ci1, ci2):
    isXYEqual = su.equals(ci1['X'], ci2['Y'], 'name')
    isYXEqual = su.equals(ci1['Y'], ci2['X'], 'name')

    return isXYEqual and isYXEqual

class ConditionalIndependencies():

    # assumes V is topo sorted

    @staticmethod
    def mbplus(G,V,X,C):
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return None
        
        if X is None or C is None or len(C) == 0:
            return None

        VleqX = V[:V.index(X)+1]
        GVleqX = gu.subgraph(G, VleqX)
        PaC = su.union(gu.parents(C,GVleqX), C, 'name')

        return su.difference(PaC, [X], 'name')

    @staticmethod
    def GMP(G,V):
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return []
        
        CI = []
        
        for i in range(1,len(V)):
            Xcombs = list(itertools.combinations(V, i))

            for X in Xcombs:
                if len(X) == 0:
                    continue

                X = ou.makeArray(list(X))
                VminusX = su.difference(V, X, 'name')

                for j in range(1, len(VminusX)+1):
                    Ycombs = list(itertools.combinations(VminusX, j))

                    for Y in Ycombs:
                        if len(Y) == 0:
                            continue

                        Y = ou.makeArray(list(Y))
                        VminusXY = su.difference(VminusX, Y, 'name')

                        for k in range(0, len(VminusXY)+1):
                            Zcombs = list(itertools.combinations(VminusXY, k))
                            
                            for Z in Zcombs:
                                Z = ou.makeArray(list(Z))
                                
                                if DSeparation.test(G, X, Y, Z):
                                    # sort to remove duplicates
                                    CI.append({
                                        'X': sorted(X, key=sortByName),
                                        'Y': sorted(Y, key=sortByName),
                                        'Z': sorted(Z, key=sortByName)
                                    })

        # remove duplicates
        CI = su.unique(CI)

        # remove symmetric CIs
        CI = su.uniqueWith(CI, isSymmetric)

        return CI


    @staticmethod
    def LMP(G, V, onlyMaximalAns = True):
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return []

        CI = []

        V = su.intersection(gu.topoSort(G), V, 'name')

        # hack to force certain topo order, making results consistent
        # namesInOrder = ['A','B','C','D','E','F','H','J']
        # Vordered = []

        # for name in namesInOrder:
        #     Vs = list(filter(lambda n: n['name'] == name, V))
        #     Vordered.append(Vs[0])

        # V = Vordered
        
        Vnames = list(map(lambda n: n['name'], V))
        print('Variables (topo sorted):')
        print(writeNodeNames(Vnames))

        MaxAns = []
        
        for u in V:
            Vlequ = V[:V.index(u)+1]
            GVlequ = gu.subgraph(G, Vlequ)
            
            # brute force all maximal ancestral sets S+
            Anu = gu.ancestors(u, GVlequ)
            Anu = su.union([u], Anu, 'name')
            VnonAnu = su.difference(Vlequ, Anu, 'name')

            for i in range(len(VnonAnu) + 1):
                combs = list(itertools.combinations(VnonAnu, i))

                for Sminus in combs:
                    S = su.union(Anu, Sminus, 'name')

                    AnS = gu.ancestors(S, GVlequ)

                    # check if S is ancestral
                    if not su.equals(S, AnS, 'name'):
                        continue

                    GS = gu.subgraph(GVlequ, S)

                    # C = C(u)_GS
                    CCS = gu.cCompDecomposition(GS)
                    C = None

                    for ccs in CCS:
                        if su.belongs(u, ccs, compareNames):
                            C = ccs
                            break
                    
                    if onlyMaximalAns:
                        # check if S is maximal w.r.t. Z = mb(u,S)
                        # S+ = V<=u \ De( Sp(C) \ (Z + {u}) )
                        # Lemma 5, Richardson 2003
                        PaC = gu.parentsPlus(C, GS)
                        Sp = su.difference(gu.spouses(C, GVlequ), PaC, 'name')
                        DeSp = gu.descendants(Sp, GVlequ)
                        Sminus = su.union(Sp, DeSp, 'name')
                        Splus = su.difference(Vlequ, Sminus, 'name')

                        if not su.equals(S, Splus):
                            continue

                        MaxAns.append(Splus)

                        W = su.difference(Splus, PaC, 'name')
                    else:
                        PaC = gu.parentsPlus(C, GS)
                        W = su.difference(S, PaC, 'name')

                    # check valid CI
                    if su.isEmpty(W):
                        continue

                    # Z = Pa(C)_GS \ {u}
                    Z = su.difference(PaC, [u], 'name')

                    CI.append({
                        'u': u,
                        'W': W,
                        'Z': Z
                    })
        
        return CI
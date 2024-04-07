import itertools

from src.inference.utils.graph_utils import GraphUtils as gu
from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import compareNames
from src.adjustment.adjustment_sets_utils import writeNodeNames


class ConditionalIndependencies():

    @staticmethod
    def ListCIBF(G, V):
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return []

        CI = []

        V = su.intersection(gu.topoSort(G), V, 'name')
        
        Vnames = list(map(lambda n: n['name'], V))
        print('Variables (topo sorted):')
        print(writeNodeNames(Vnames))
        
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
                    
                    # check if S is maximal w.r.t. Z = mb(u,S)
                    GS = gu.subgraph(GVlequ, S)

                    # C = C(u)_GS
                    CCS = gu.cCompDecomposition(GS)
                    C = None

                    for ccs in CCS:
                        if su.belongs(u, ccs, compareNames):
                            C = ccs
                            break

                    # S+ = V<=u \ De( Sp(C) \ (Z + {u}) )
                    # Lemma 5, Richardson 2003
                    PaC = gu.parentsPlus(C, GS)
                    Sp = su.difference(gu.spouses(C, GVlequ), PaC, 'name')
                    DeSp = gu.descendants(Sp, GVlequ)
                    Sminus = su.union(Sp, DeSp, 'name')
                    Splus = su.difference(Vlequ, Sminus, 'name')

                    if not su.equals(S, Splus):
                        continue

                    # check valid CI
                    W = su.difference(Splus, PaC, 'name')

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
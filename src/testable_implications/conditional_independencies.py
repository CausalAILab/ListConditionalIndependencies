import itertools

from src.inference.utils.graph_utils import GraphUtils as gu, sortByName
from src.inference.utils.set_utils import SetUtils as su
from src.common.object_utils import ObjectUtils as ou
from src.inference.utils.graph_utils import compareNames
from src.adjustment.adjustment_sets_utils import writeNodeNames, nodeNamesToString
from src.path_analysis.d_separation import DSeparation

def isSymmetric(ci1, ci2):
    isXYEqual = su.equals(ci1['X'], ci2['Y'], 'name')
    isYXEqual = su.equals(ci1['Y'], ci2['X'], 'name')

    return isXYEqual and isYXEqual

class ConditionalIndependencies():

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
    def LMP(G, V, onlyMaximalAns = True, Vordered = None):
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return []

        CI = []

        V = su.intersection(gu.topoSort(G), V, 'name')

        if Vordered is not None:
            V = Vordered

        print('Variables (topo sorted):')
        print(nodeNamesToString(V, False))

        MaxAns = []
        
        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)
            
            # brute force all maximal ancestral sets S+
            Anu = su.union(gu.ancestors(X, GVleqX), [X], 'name')
            VnonAnu = su.difference(VleqX, Anu, 'name')

            for i in range(len(VnonAnu) + 1):
                combs = list(itertools.combinations(VnonAnu, i))

                for Sminus in combs:
                    S = su.union(Anu, Sminus, 'name')

                    AnS = gu.ancestors(S, GVleqX)

                    # check if S is ancestral
                    if not su.equals(S, AnS, 'name'):
                        continue

                    GS = gu.subgraph(GVleqX, S)

                    # C = C(u)_GS
                    CCS = gu.cCompDecomposition(GS)
                    C = None

                    for ccs in CCS:
                        if su.belongs(X, ccs, compareNames):
                            C = ccs
                            break
                    
                    if onlyMaximalAns:
                        # check if S is maximal w.r.t. Z = mb(X,S)
                        # S+ = V<=X \ De( Sp(C) \ (Z + {X}) )
                        # Lemma 5, Richardson 2003
                        PaC = gu.parentsPlus(C, GS)
                        Sp = su.difference(gu.spouses(C, GVleqX), PaC, 'name')
                        DeSp = gu.descendants(Sp, GVleqX)
                        Sminus = su.union(Sp, DeSp, 'name')
                        Splus = su.difference(VleqX, Sminus, 'name')

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
                    Z = su.difference(PaC, [X], 'name')

                    CI.append({
                        'X': X,
                        'W': W,
                        'Z': Z
                    })
        
        return CI

    # used for comparing outputs with LMP
    # it is still brute force (checks all ancestral sets)

    @staticmethod
    def LMPplus(G, V):
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return []

        CI = []

        V = su.intersection(gu.topoSort(G), V, 'name')

        # print('Variables (topo sorted):')
        # print(nodeNamesToString(V, False))

        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)

            AC_X = []
            
            # brute force all ancestral sets S
            AnX = su.union(gu.ancestors(X, GVleqX), [X], 'name')
            VnonAnX = su.difference(VleqX, AnX, 'name')

            for i in range(len(VnonAnX) + 1):
                combs = list(itertools.combinations(VnonAnX, i))

                for Sminus in combs:
                    S = su.union(AnX, Sminus, 'name')

                    AnS = gu.ancestors(S, GVleqX)

                    # check if S is ancestral
                    if not su.equals(S, AnS, 'name'):
                        continue

                    # C = C(u)_GS
                    GS = gu.subgraph(GVleqX, S)
                    CCS = gu.cCompDecomposition(GS)
                    C = None

                    for ccs in CCS:
                        if su.belongs(X, ccs, compareNames):
                            C = ccs
                            break

                    AC_X.append(C)

            # remove duplicates
            AC_X = su.uniqueWith(AC_X, su.isEqual)

            for C in AC_X:
                Splus = ConditionalIndependencies.Splus(G,VleqX,X,C)
                PaC = gu.parentsPlus(C, GVleqX)
                W = su.difference(Splus, PaC, 'name')

                # check valid CI
                if su.isEmpty(W):
                    continue

                # Z = Pa(C)_GS \ {u}
                Z = su.difference(PaC, [X], 'name')

                CI.append({
                    'X': X,
                    'W': W,
                    'Z': Z
                })

        return CI
    
    @staticmethod
    def ListCI(G,V,Vordered = None):
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return None
        
        CI = []

        V = su.intersection(gu.topoSort(G), V, 'name')

        if Vordered is not None:
            V = Vordered

        print('Variables (topo sorted):')
        print(nodeNamesToString(V, False))

        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)
            
            # I and R
            GVleqX = gu.subgraph(G, VleqX)
            AnX = su.union(gu.ancestors(X, GVleqX), [X], 'name')
            GAnX = gu.subgraph(GVleqX, AnX)
            I = ConditionalIndependencies.C(GAnX,X)
            R = ConditionalIndependencies.C(GVleqX,X)

            # print(X)
            # print(nodeNamesToString(I))
            # print(nodeNamesToString(R))

            # ConditionalIndependencies.ListCIX(GVleqX,X,VleqX,I,R,CI)
            # ConditionalIndependencies.ListCIXv3(GVleqX,X,VleqX,I,R,CI)
            ConditionalIndependencies.ListCIXone(GVleqX,X,VleqX,I,R,CI)

        return CI
    
    @staticmethod
    def ListCIXone(GVleqX,X,VleqX,I,R,CI):
        Spu = ConditionalIndependencies.GetProperSpv3(GVleqX,X,VleqX,I,R)

        if su.isEmpty(Spu):
            return
        
        if (len(Spu) == 1 and Spu[0] == []):
            AnSpI = gu.ancestorsPlus(su.union(gu.spouses(I, GVleqX), I, 'name'), GVleqX)
            AnSpIcapR = su.intersection(AnSpI, R, 'name')
            Gprime = gu.subgraph(GVleqX, AnSpIcapR)
            Ie = ConditionalIndependencies.C(Gprime, [X])
            RmIe = su.difference(R, Ie, 'name')

            if len(RmIe) == 0:
                C = Ie
                Z = ConditionalIndependencies.mbplus(GVleqX,VleqX,X,C)
                Splus = ConditionalIndependencies.Splus(GVleqX,VleqX,X,C)
                W = su.difference(Splus, su.union(Z, [X], 'name'), 'name')

                if len(W) == 0:
                    print('Bug (empty W)!')
                    print('X: ' + nodeNamesToString([X]))
                    print('C: ' + nodeNamesToString(C))
                    print('Z: ' + nodeNamesToString(Z))
                    print('S+: ' + nodeNamesToString(Splus))

                CI.append({
                    'X': X,
                    'W': W,
                    'Z': Z
                })

                return
            else:
                s = RmIe[0]
        else:
            s = Spu[0]

        Des = gu.descendantsPlus(s, GVleqX)
        Iprime = su.union(I, [s], 'name')
        Gprime = gu.subgraph(GVleqX, su.difference(R, Des, 'name'))
        Rprime = ConditionalIndependencies.C(Gprime,[X])

        ConditionalIndependencies.ListCIXone(GVleqX,X,VleqX,I,Rprime,CI)
        ConditionalIndependencies.ListCIXone(GVleqX,X,VleqX,Iprime,R,CI)
    
    @staticmethod
    def ListCIXv3(GVleqX,X,VleqX,I,R,CI):
        Sp = su.difference(gu.ancestorsPlus(gu.spouses(I, GVleqX), GVleqX), I, 'name')
        Sp = su.intersection(Sp, R, 'name')
        Iextend = su.union(I, Sp, 'name')

        # if X['name'] == 'B' or X['name'] == 'C':
        if X['name'] == 'B':
            print('X: ' + nodeNamesToString([X]))
            print('I: ' + nodeNamesToString(I))
            print('R: ' + nodeNamesToString(R))
            print('Sp: ' + nodeNamesToString(Sp))
            # print('Ie: ' + nodeNamesToString(Rprime))

        admissiblePairs = []
        ConditionalIndependencies.ListIRXv3(GVleqX,X,VleqX,I,R,Sp,Sp,Iextend,admissiblePairs)

        if len(admissiblePairs) == 0:
            return

        for (Iprime,Rprime) in admissiblePairs:
            if Iprime is None and Rprime is None:
                return

            if su.equals(Iprime, Rprime, 'name'):
                C = Iprime
                Z = ConditionalIndependencies.mbplus(GVleqX,VleqX,X,C)
                Splus = ConditionalIndependencies.Splus(GVleqX,VleqX,X,C)
                W = su.difference(Splus, su.union(Z, [X], 'name'), 'name')

                if len(W) == 0:
                    print('Bug (empty W)!')
                    print('X: ' + nodeNamesToString([X]))
                    print('C: ' + nodeNamesToString(C))
                    print('Z: ' + nodeNamesToString(Z))
                    print('S+: ' + nodeNamesToString(Splus))

                CI.append({
                    'X': X,
                    'W': W,
                    'Z': Z
                })
            else:
                # if X['name'] == 'B' or X['name'] == 'C':
                if X['name'] == 'B':
                    print('X: ' + nodeNamesToString([X]))
                    print('Iprime: ' + nodeNamesToString(Iprime))
                    print('Rprime: ' + nodeNamesToString(Rprime))

                # if len(Iprime) > len(Rprime):
                #     print('Iprime: ' + nodeNamesToString(Iprime))
                #     print('Rprime: ' + nodeNamesToString(Rprime))

                ConditionalIndependencies.ListCIXv3(GVleqX,X,VleqX,Iprime,Rprime,CI)

    @staticmethod
    def ListIRXv3(GVleqX,X,VleqX,I,R,Sp,Spc,Iextend,admissiblePairs):
        Spu = ConditionalIndependencies.GetProperSpv3(GVleqX,X,VleqX,I,R,Sp,Spc,Iextend)
        Spd = su.difference(Spc, Spu, 'name')

        # Spc -> Spn, Spa
        Spn = su.difference(gu.spouses(I, GVleqX), I, 'name')
        Spn = su.intersection(Spn, Spc, 'name')
        Spa = su.difference(Spc, Spn, 'name')

        # if X['name'] == 'B' or X['name'] == 'C':
        if X['name'] == 'B':
            print('X: ' + nodeNamesToString([X]))
            print('Spc: ' + nodeNamesToString(Spc))
            print('Spu: ' + nodeNamesToString(Spu))

        if su.isEmpty(Spu):
            return
        
        if (len(Spu) == 1 and Spu[0] == []):
            Iprime = Iextend
            Rminus = su.difference(Sp, su.difference(Iprime, I, 'name'), 'name')
            # some s of Sp can't be removed if s is in An(I')
            AnIprime = gu.ancestorsPlus(Iprime, GVleqX)
            Rminus = su.difference(Rminus, AnIprime, 'name')
            DeRminus = gu.descendantsPlus(Rminus, GVleqX)
            GR = gu.subgraph(GVleqX, su.difference(R, DeRminus, 'name'))
            Rprime = ConditionalIndependencies.C(GR,X)

            admissiblePairs.append((Iprime,Rprime))
            return

        Decs = []

        if [] in Spu:
            Decs.append([])
            del Spu[Spu.index([])]

        sortedSpu = su.intersection(VleqX, Spu, 'name')

        Decs.extend(ConditionalIndependencies.ListDec(GVleqX, sortedSpu))

        for D in Decs:
            DeD = gu.descendantsPlus(D, GVleqX)
            Dprime = su.intersection(DeD, Sp, 'name')
            Spcprime = su.difference(Spd, Dprime, 'name')
            Ieprime = su.difference(Iextend, Dprime, 'name')

            # spa-
            Gprime = gu.subgraph(GVleqX, su.difference(R, Dprime, 'name'))
            Spaminus = su.difference(Spa, ConditionalIndependencies.C(Gprime,[X]), 'name')
            
            # remove spa-?
            Spcprime = su.difference(Spcprime, Spaminus, 'name')
            Ieprime = su.difference(Ieprime, Spaminus, 'name')

            if X['name'] == 'B':
                print('X: ' + nodeNamesToString([X]))
                print('D: ' + nodeNamesToString(D))
                print('Dprime: ' + nodeNamesToString(Dprime))
                print('Spcprime: ' + nodeNamesToString(Spcprime))

            # ?
            # ConditionalIndependencies.ListIRXv3(GVleqX,X,VleqX,I,R,Sp,Spcprime,Ieprime,admissiblePairs)

            if su.isEmpty(Spcprime):
                # When Iprime > Rprime?
                Iprime = Ieprime
                Rminus = su.difference(Sp, su.difference(Iprime, I, 'name'), 'name')
                # some s of Sp can't be removed if s is in An(I')
                AnIprime = gu.ancestorsPlus(Iprime, GVleqX)
                Rminus = su.difference(Rminus, AnIprime, 'name')
                DeRminus = gu.descendantsPlus(Rminus, GVleqX)
                GR = gu.subgraph(GVleqX, su.difference(R, DeRminus, 'name'))
                Rprime = ConditionalIndependencies.C(GR,X)

                admissiblePairs.append((Iprime,Rprime))
            else:
                ConditionalIndependencies.ListIRXv3(GVleqX,X,VleqX,I,R,Sp,Spcprime,Ieprime,admissiblePairs)

    @staticmethod
    def GetProperSpv3(GVleqX,X,VleqX,I,R):
        AnSpI = gu.ancestorsPlus(su.union(gu.spouses(I, GVleqX), I, 'name'), GVleqX)
        AnSpIcapR = su.intersection(AnSpI, R, 'name')
        Gprime = gu.subgraph(GVleqX, AnSpIcapR)
        Ie = ConditionalIndependencies.C(Gprime, [X])
        Sp = su.difference(Ie, I, 'name')

        Spu = []

        # Sp -> Spn
        Spn = su.difference(gu.spouses(I, GVleqX), I, 'name')
        Spn = su.intersection(Spn, Sp, 'name')

        # s to be removed cannot be in An(I), otherwise Ie' is not ancestral
        AnI = gu.ancestorsPlus(I, GVleqX)
        SpToSearch = su.difference(Spn, AnI, 'name')

        SpIteration = list(map(lambda n: ou.makeArray(n), SpToSearch))
        SpIteration.extend([[]])

        # SpIteration = [[]]
        # SpIteration.extend(list(map(lambda n: ou.makeArray(n), SpToSearch)))

        for s in SpIteration:
            # Step 1
            Des = gu.descendantsPlus(s, GVleqX)
            Gprime = gu.subgraph(GVleqX, su.difference(Ie, Des, 'name'))
            Ieprime = ConditionalIndependencies.C(Gprime, [X])

            if ConditionalIndependencies.IsAdmissible(GVleqX,X,VleqX,Ieprime):
                if len(s) > 0:
                    Spu.append(s[0])
                else:
                    Spu.append(s)
                
                continue

            # Step 2
            PaIeprime = gu.parentsPlus(Ieprime, GVleqX)
            SpIeprime = gu.spouses(Ieprime,GVleqX)
            Spprime = su.difference(SpIeprime, PaIeprime, 'name')
            Spprime = su.intersection(Spprime, R, 'name')
            # Sps = su.difference(SpIeprime, su.intersection(Des, Sp, 'name'), 'name')
            # Sps = su.difference(Sps, PaIeprime, 'name')
            # Sps = su.intersection(Sps, R, 'name')
            Sps = su.difference(Spprime, su.intersection(Des, Sp, 'name'), 'name')

            isSproper = False

            for sprime in Sps:
                Ansprime = su.union([sprime], gu.ancestors(sprime, GVleqX), 'name')
                AnSpprime = su.intersection(Ansprime, Spprime, 'name')

                DeAnSpprime = gu.descendantsPlus(AnSpprime, GVleqX)
                DeSpprimeMinusAnSpprime = gu.descendantsPlus(su.difference(Spprime, AnSpprime, 'name'), GVleqX)

                Gprime = gu.subgraph(GVleqX, su.difference(DeAnSpprime, DeSpprimeMinusAnSpprime, 'name'))
                DeAnSpInGprime = gu.descendantsPlus(sprime, Gprime)

                for d in su.difference(DeAnSpInGprime, [sprime], 'name'):
                    C = ConditionalIndependencies.C(Gprime, [sprime])
                    
                    if not su.belongs(d, C, compareNames):
                        
                        isSproper = True
                        if len(s) > 0:
                            Spu.append(s[0])
                        else:
                            Spu.append(s)
                        break

                if isSproper:
                    break

        return Spu

    @staticmethod
    def ListCIX(GVleqX,X,VleqX,I,R,CI):
        Sp = su.difference(gu.spouses(I, GVleqX), I, 'name')
        Sp = su.intersection(Sp, R, 'name')
        Iextend = su.union(I, Sp, 'name')

        admissiblePairs = []
        ConditionalIndependencies.ListIRX(GVleqX,X,VleqX,I,R,Sp,Sp,Iextend,admissiblePairs)

        if len(admissiblePairs) == 0:
            return

        for (Iprime,Rprime) in admissiblePairs:
            if Iprime is None and Rprime is None:
                return

            if su.equals(Iprime, Rprime, 'name'):
                C = Iprime
                Z = ConditionalIndependencies.mbplus(GVleqX,VleqX,X,C)
                Splus = ConditionalIndependencies.Splus(GVleqX,VleqX,X,C)
                W = su.difference(Splus, su.union(Z, [X], 'name'), 'name')

                # if X['name'] == 'J':
                #     print('Output CI')
                #     ConditionalIndependencies.printCI(X,W,Z)

                if len(W) == 0:
                    print('Bug (empty W)!')
                    print('X: ' + nodeNamesToString([X]))
                    print('C: ' + nodeNamesToString(C))
                    print('Z: ' + nodeNamesToString(Z))

                CI.append({
                    'X': X,
                    'W': W,
                    'Z': Z
                })
            else:
                # if len(su.difference(Iprime, Rprime, 'name')) > 0:
                #     print('X: ' + nodeNamesToString([X]))
                #     print('Sp: ' + nodeNamesToString(Sp))
                #     print('Ie: ' + nodeNamesToString(Iextend))
                #     print('I: ' + nodeNamesToString(I))
                #     print('R: ' + nodeNamesToString(R))
                #     print('Iprime: ' + nodeNamesToString(Iprime))
                #     print('Rprime: ' + nodeNamesToString(Rprime))
                #     return

                # print('Iprime: ' + nodeNamesToString(Iprime))
                # print('Rprime: ' + nodeNamesToString(Rprime))

                ConditionalIndependencies.ListCIX(GVleqX,X,VleqX,Iprime,Rprime,CI)

    @staticmethod
    def ListIRX(GVleqX,X,VleqX,I,R,Sp,Spc,Iextend,admissiblePairs):
        Spu = ConditionalIndependencies.GetProperSp(GVleqX,X,VleqX,I,Sp,Spc,Iextend)
        Spd = su.difference(Spc, Spu, 'name')

        # if X['name'] == 'R':
        #     print('X: ' + nodeNamesToString([X]))
        #     print('Sp: ' + nodeNamesToString(Sp))
        #     print('Spu: ' + nodeNamesToString(Spu))
        #     print('Spd: ' + nodeNamesToString(Spd))

        if su.isEmpty(Spu):
            return
        
        if (len(Spu) == 1 and Spu[0] == []):
            Iprime = Iextend
            Rminus = su.difference(Sp, su.difference(Iprime, I, 'name'), 'name')
            # some s of Sp can't be removed if s is in An(I')
            AnIprime = su.union(Iprime, gu.ancestors(Iprime, GVleqX), 'name')
            Rminus = su.difference(Rminus, AnIprime, 'name')
            DeRminus = gu.descendantsPlus(Rminus, GVleqX)
            GR = gu.subgraph(GVleqX, su.difference(R, DeRminus, 'name'))
            Rprime = ConditionalIndependencies.C(GR,X)

            admissiblePairs.append((Iprime,Rprime))
            return

        Decs = []

        if [] in Spu:
            Decs.append([])
            del Spu[Spu.index([])]

        sortedSpu = su.intersection(VleqX, Spu, 'name')

        Decs.extend(ConditionalIndependencies.ListDec(GVleqX, sortedSpu))

        for D in Decs:
            DeD = gu.descendantsPlus(D, GVleqX)
            Dprime = su.intersection(DeD, Sp, 'name')
            Spcprime = su.difference(Spd, Dprime, 'name')
            Ieprime = su.difference(Iextend, Dprime, 'name')

            # if X['name'] == 'R':
            #     print('X: ' + nodeNamesToString([X]))
            #     print('Spu: ' + nodeNamesToString(Spu))
            #     print('Dprime: ' + nodeNamesToString(Dprime))
            #     print('Spcprime: ' + nodeNamesToString(Spcprime))
            #     print('Ieprime: ' + nodeNamesToString(Ieprime))

            if su.isEmpty(Spcprime):
                Iprime = Ieprime
                Rminus = su.difference(Sp, su.difference(Iprime, I, 'name'), 'name')
                # some s of Sp can't be removed if s is in An(I')
                AnIprime = su.union(Iprime, gu.ancestors(Iprime, GVleqX), 'name')
                Rminus = su.difference(Rminus, AnIprime, 'name')
                DeRminus = gu.descendantsPlus(Rminus, GVleqX)
                GR = gu.subgraph(GVleqX, su.difference(R, DeRminus, 'name'))
                Rprime = ConditionalIndependencies.C(GR,X)

                admissiblePairs.append((Iprime,Rprime))
            else:
                ConditionalIndependencies.ListIRX(GVleqX,X,VleqX,I,R,Sp,Spcprime,Ieprime,admissiblePairs)

    @staticmethod
    def GetProperSp(GVleqX,X,VleqX,I,Sp,Spc,Iextend):
        Spu = []

        # An(X) cannot be excluded from G
        # SpToSearch = su.difference(Spc, gu.ancestors(X,GVleqX), 'name')
        # s to be removed cannot be in An(I), otherwise Ie' is not ancestral
        AnI = su.union(I, gu.ancestors(I, GVleqX), 'name')
        SpToSearch = su.difference(Spc, AnI, 'name')

        SpIteration = [[]]
        SpIteration.extend(list(map(lambda n: ou.makeArray(n), SpToSearch)))

        for s in SpIteration:
            # Step 1
            Des = gu.descendantsPlus(s, GVleqX)
            DesSp = su.intersection(Des, Sp, 'name')
            Ieprime = su.difference(Iextend, DesSp, 'name')

            if ConditionalIndependencies.IsAdmissible(GVleqX,X,VleqX,Ieprime):
                if len(s) > 0:
                    Spu.append(s[0])
                else:
                    Spu.append(s)
                
                continue

            # Step 2
            PaIeprime = gu.parentsPlus(Ieprime, GVleqX)
            SpIeprime = gu.spouses(Ieprime,GVleqX)
            Spprime = su.difference(SpIeprime, PaIeprime, 'name')
            Sps = su.difference(SpIeprime, DesSp, 'name')
            Sps = su.difference(Sps, PaIeprime, 'name')

            isSproper = False

            for sprime in Sps:
                Ansprime = su.union([sprime], gu.ancestors(sprime, GVleqX), 'name')
                AnSpprime = su.intersection(Ansprime, Spprime, 'name')

                DeAnSpprime = gu.descendantsPlus(AnSpprime, GVleqX)
                DeSpprimeMinusAnSpprime = gu.descendantsPlus(su.difference(Spprime, AnSpprime, 'name'), GVleqX)

                Gprime = gu.subgraph(GVleqX, su.difference(DeAnSpprime, DeSpprimeMinusAnSpprime, 'name'))
                # DeAnSpInGprime = gu.descendantsPlus(AnSpprime, Gprime)
                DeAnSpInGprime = gu.descendantsPlus(sprime, Gprime)

                # for d in su.difference(DeAnSpInGprime, AnSpprime, 'name'):
                for d in su.difference(DeAnSpInGprime, [sprime], 'name'):
                    # C = ConditionalIndependencies.C(Gprime, AnSpprime)
                    C = ConditionalIndependencies.C(Gprime, [sprime])
                    
                    if not su.belongs(d, C, compareNames):
                        
                        isSproper = True
                        if len(s) > 0:
                            Spu.append(s[0])
                        else:
                            Spu.append(s)
                        break

                if isSproper:
                    break

        return Spu
    
    @staticmethod
    def ListDec(G, sortedV):
        if len(sortedV) == 0:
            return []

        marks = {}

        for v in sortedV:
            marks[v['name']] = None

        descSets = []
        stack = [0]

        while len(stack) > 0:
            j = stack[len(stack)-1]
            Vj = sortedV[j]

            if marks[Vj['name']] == None:
                # include al descendants of Vj
                De = gu.descendants(Vj, G)

                for n in De:
                    marks[n['name']] = True
            elif marks[Vj['name']] == True:
                # we are backtracking, change the value of this node to false and unmark all descendants
                De = gu.descendants(Vj, G)

                for n in De:
                    marks[n['name']] = None

                marks[Vj['name']] = False
            else:
                marks[Vj['name']] = None
                stack.pop()
                # continue to the next iteration before adding a new node to the stack
                continue

            # add next unmarked node to the stack
            added = False

            for k in range(j+1, len(sortedV)):
                if marks[sortedV[k]['name']] == None:
                    stack.append(k)
                    added = True
                    break

            # no more variables to process, this is a set, save it
            if not added:
                descSet = list(filter(lambda n: marks[n['name']] == True, sortedV))

                if len(descSet) > 0:
                    descSets.append(descSet)

        return descSets

    # @staticmethod
    # def ListDec(G, T):
    #     if T is None:
    #         return None

    #     if len(T) == 0:
    #         return []
        
    #     Decs = []

    #     for i in range(1,len(T) + 1):
    #         combs = list(itertools.combinations(T, i))

    #         for I in combs:
    #             I = list(I)
    #             E = su.difference(T, I, 'name')

    #             DeI = gu.descendants(I, G)

    #             if len(su.intersection(DeI, E, 'name')) > 0:
    #                 continue
    #             else:
    #                 Decs.append(I)

    #     return Decs
    

    @staticmethod
    def IsAdmissible(G,X,VleqX,C):
        GVleqX = gu.subgraph(G, VleqX)

        Z = ConditionalIndependencies.mbplus(GVleqX,VleqX,X,C)
        Splus = ConditionalIndependencies.Splus(GVleqX,VleqX,X,C)
        W = su.difference(Splus, su.union(Z, [X], 'name'), 'name')

        return not su.isEmpty(W)


    @staticmethod
    def C(G,X):
        X = ou.makeArray(X)

        CC = gu.cCompDecomposition(G)

        for cc in CC:
            if su.isSubset(X, cc, 'name'):
                return cc
            
        return None

    
    # assumes V is topo sorted

    @staticmethod
    def Splus(G,V,X,C):
        VleqX = V[:V.index(X)+1]
        GVleqX = gu.subgraph(G, VleqX)

        PaC = gu.parentsPlus(C, GVleqX)
        Sp = su.difference(gu.spouses(C, GVleqX), PaC, 'name')
        DeSp = gu.descendants(Sp, GVleqX)
        Sminus = su.union(Sp, DeSp, 'name')
        Splus = su.difference(VleqX, Sminus, 'name')

        return Splus

    # assumes V is topo sorted

    @staticmethod
    def mbplus(G,V,X,C):
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return None
        
        if X is None or C is None or len(C) == 0:
            return None

        VleqX = V[:V.index(X)+1]
        GVleqX = gu.subgraph(G, VleqX)

        return su.difference(gu.parentsPlus(C,GVleqX), [X], 'name')
    
    @staticmethod
    def printCI(X,W,Z):
        X = ou.makeArray(X)

        print(nodeNamesToString(X) + ' \indep ' + nodeNamesToString(W) + ' | ' + nodeNamesToString(Z))
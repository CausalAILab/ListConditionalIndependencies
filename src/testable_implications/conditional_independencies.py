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

        print('Variables (topo sorted):')
        print(nodeNamesToString(V, False))

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
            AnX = su.union(gu.ancestors(X, GVleqX), [X], 'name')
            GAnX = gu.subgraph(GVleqX, AnX)
            I = ConditionalIndependencies.C(GAnX,X)
            R = ConditionalIndependencies.C(GVleqX,X)

            # print(X)
            # print(nodeNamesToString(I))
            # print(nodeNamesToString(R))

            ConditionalIndependencies.ListCIX(G,X,VleqX,I,R,CI)

        return CI

    @staticmethod
    def ListCIX(G,X,VleqX,I,R,CI):
        # admissiblePairs = ConditionalIndependencies.ListIRX(G,X,VleqX,I,R)
        admissiblePairs = ConditionalIndependencies.ListIRXv1(G,X,VleqX,I,R)

        if len(admissiblePairs) == 0:
            return

        for (Iprime,Rprime) in admissiblePairs:
            if Iprime is None and Rprime is None:
                return

            if su.equals(Iprime, Rprime, 'name'):
                GVleqX = gu.subgraph(G, VleqX)
                
                C = Iprime
                Z = ConditionalIndependencies.mbplus(GVleqX,VleqX,X,C)
                Splus = ConditionalIndependencies.Splus(GVleqX,VleqX,X,C)
                W = su.difference(Splus, su.union(Z, [X], 'name'), 'name')

                # ConditionalIndependencies.printCI(X,W,Z)

                CI.append({
                    'X': X,
                    'W': W,
                    'Z': Z
                })
            else:
                # if len(su.difference(Iprime, Rprime, 'name')) > 0:
                #     return

                # print('Iprime: ' + nodeNamesToString(Iprime))
                # print('Rprime: ' + nodeNamesToString(Rprime))

                ConditionalIndependencies.ListCIX(G,X,VleqX,Iprime,Rprime,CI)

    @staticmethod
    def ListIRX(G,X,VleqX,I,R):
        admissiblePairs = []

        # Step 1
        GVleqX = gu.subgraph(G, VleqX)

        Z = ConditionalIndependencies.mbplus(GVleqX,VleqX,X,I)
        Sp = su.difference(gu.spouses(I, G), su.union(Z, [X], 'name'))
        Sp = su.intersection(Sp, R, 'name')

        if ConditionalIndependencies.IsAdmissible(G,X,VleqX,I):
            Iprime = I

            DeSp = su.union(Sp, gu.descendants(Sp, GVleqX), 'name')
            GR = gu.subgraph(G, su.difference(R, DeSp, 'name'))
            Rprime = ConditionalIndependencies.C(GR,X)

            admissiblePairs.append((Iprime,Rprime))

        # Step 2
        Spu = ConditionalIndependencies.GetProperSp(G,X,VleqX,I,R,Sp)
        Spd = su.difference(Sp, Spu, 'name')

        # if X['name'] == 'H':
        #     print('I: ' + nodeNamesToString(I))
        #     print('Sp: ' + nodeNamesToString(Sp))
        #     print('Spu: ' + nodeNamesToString(Spu))

        if len(Spu) == 0:
            admissiblePairs.append((None,None))
            return admissiblePairs

        # Step 3
        Ancs = ConditionalIndependencies.ListAnc(GVleqX, Spu)

        # if X['name'] == 'H':
        #     print('Spu: ' + nodeNamesToString(Spu))
            # print(Ancs)

        for A in Ancs:
            if su.isEmpty(A):
                continue

            AnA = su.union(A, gu.ancestors(A, G), 'name')
            Aprime = su.intersection(AnA, Spd, 'name')
            Iu = su.union(A, Aprime, 'name')
            Id = su.difference(Spd, Aprime, 'name')
            Idupdated = []

            for d in Id:
                And = su.union([d], gu.ancestors(d, G), 'name')
                Apprime = su.intersection(And, Sp, 'name')

                Iud = su.union(Iu, Id, 'name')
                
                if su.isSubset(Apprime, Iud, 'name'):
                    Idupdated.append(d)

            Id = Idupdated

            IdAnc = [[]]
            IdAnc.extend(ConditionalIndependencies.ListAnc(GVleqX, Id))

            for Idprime in IdAnc:
                Iplus = su.union(Iu, Idprime, 'name')
                Iprime = su.union(I, Iplus, 'name')
                Rminus = su.difference(Sp, Iplus, 'name')
                DeRminus = su.union(Rminus, gu.descendants(Rminus, G), 'name')
                
                GR = gu.subgraph(G, su.difference(R, DeRminus, 'name'))
                Rprime = ConditionalIndependencies.C(GR,X)

                admissiblePairs.append((Iprime,Rprime))


        # indicate that no more is available
        admissiblePairs.append((None,None))
        
        return admissiblePairs
    
    @staticmethod
    def GetProperSp(G,X,VleqX,I,R,Sp):
        if len(Sp) == 0:
            return []

        Spu = []

        GVleqX = gu.subgraph(G, VleqX)

        # if X['name'] == 'J':
        #     print(nodeNamesToString(I))
        #     print(nodeNamesToString(Sp))
        
        for s in Sp:
            # Step 1
            Ans = gu.ancestors(s, GVleqX)
            AnSp = su.intersection(Ans, Sp, 'name')
            Iprime = su.intersection(su.union(I, AnSp, 'name'), R, 'name')

            # if X['name'] == 'J':
            #     print('s: ' + nodeNamesToString([s]))
            #     print('I\': ' + nodeNamesToString(Iprime))
            #     print('admissible: ' + ConditionalIndependencies.IsAdmissible(G,X,VleqX,Iprime))

            if ConditionalIndependencies.IsAdmissible(G,X,VleqX,Iprime):
                Spu.append(s)
                continue

            # Step 2
            Zprime = ConditionalIndependencies.mbplus(GVleqX,VleqX,X,Iprime)
            Spprime = su.difference(gu.spouses(Iprime,GVleqX), su.union(Zprime, [X], 'name'), 'name')
            Sps = su.difference(gu.spouses(s,GVleqX), su.union(Zprime, [X], 'name'), 'name')

            isSproper = False

            for sprime in Sps:
                Ansprime = su.union([sprime], gu.ancestors(sprime, GVleqX), 'name')
                AnSpprime = su.intersection(Ansprime, Spprime, 'name')
                DeAnSp = su.union(AnSpprime, gu.descendants(AnSpprime, GVleqX), 'name')
                Gprime = gu.subgraph(GVleqX, su.difference(DeAnSp, su.difference(Spprime, AnSpprime, 'name'), 'name'))

                DeAnSpInGprime = su.union(AnSpprime, gu.descendants(AnSpprime, Gprime), 'name')

                for d in su.difference(DeAnSpInGprime, AnSpprime, 'name'):
                    C = ConditionalIndependencies.C(Gprime, AnSpprime)
                    
                    if not su.belongs(d, C, compareNames):
                        isSproper = True
                        Spu.append(s)
                        break

                if isSproper:
                    break

        return Spu
    
    @staticmethod
    def ListAnc(G, T):
        if T is None:
            return None

        if len(T) == 0:
            return []
        
        Ans = []

        for i in range(1,len(T) + 1):
            combs = list(itertools.combinations(T, i))

            for I in combs:
                I = list(I)
                E = su.difference(T, I, 'name')

                AnI = gu.ancestors(I, G)

                if len(su.intersection(AnI, E, 'name')) > 0:
                    continue
                else:
                    Ans.append(I)

        return Ans
    
    @staticmethod
    def ListIRXv1(G,X,VleqX,I,R):
        admissiblePairs = []

        GVleqX = gu.subgraph(G, VleqX)

        # if X['name'] == 'E':
        #     print('*** ListIRX ***')
        # print('X: ' + X['name'])

        Z = ConditionalIndependencies.mbplus(GVleqX,VleqX,X,I)
        # ?
        # Sp = su.difference(gu.spouses(I, GVleqX), su.union(Z, [X], 'name'))
        Sp = su.difference(gu.spouses(I, GVleqX), I, 'name')
        Sp = su.intersection(Sp, R, 'name')
        Iextend = su.union(I, Sp, 'name')
        Spu = ConditionalIndependencies.GetImproperSp(G,X,VleqX,Iextend,Sp,Sp)
        Spd = su.difference(Sp, Spu, 'name')

        # if X['name'] == 'E':
        #     print('*** ListIRX ***')
        #     print('I: ' + nodeNamesToString(I))
        #     print('R: ' + nodeNamesToString(R))
        #     print('Ie: ' + nodeNamesToString(Iextend))
        #     print('Sp: ' + nodeNamesToString(Sp))
        #     print('Spu: ' + nodeNamesToString(Spu))
        #     print('Spd: ' + nodeNamesToString(Spd))

        ConditionalIndependencies.Listv1(G,X,VleqX,I,Iextend,R,Sp,Spu,Spd,admissiblePairs)

        # indicate that no more is available
        admissiblePairs.append((None,None))
        
        return admissiblePairs
    
    @staticmethod
    def Listv1(G,X,VleqX,I,Iextend,R,Sp,Spu,Spd,admissiblePairs):
        GVleqX = gu.subgraph(G, VleqX)

        if su.isEmpty(Spu):
            return
        
        if (len(Spu) == 1 and Spu[0] == []):
            Iprime = Iextend
            Rminus = su.difference(Sp, su.difference(Iprime, I, 'name'), 'name')
            DeRminus = su.union(Rminus, gu.descendants(Rminus, GVleqX), 'name')
            GR = gu.subgraph(GVleqX, su.difference(R, DeRminus, 'name'))
            Rprime = ConditionalIndependencies.C(GR,X)

            admissiblePairs.append((Iprime,Rprime))
            return

        Decs = []

        if [] in Spu:
            Decs.append([])
            del Spu[Spu.index([])]

        Decs.extend(ConditionalIndependencies.ListDec(GVleqX, Spu))

        # print('*** Listv1 ***')
        # print('X: ' + X['name'])

        # if X['name'] == 'J':
        #     print('Spu: ' + nodeNamesToString(Spu))

        for D in Decs:
            DeD = gu.descendantsPlus(D, GVleqX)
            Dprime = su.intersection(DeD, Sp, 'name')
            Spprime = su.difference(Spd, Dprime, 'name')
            Ieprime = su.difference(Iextend, Dprime, 'name')

            # if X['name'] == 'J':
            # print('D: ' + nodeNamesToString(D))
            # print('Ieprime: ' + nodeNamesToString(Ieprime))

            if su.isEmpty(Spprime):
                Iprime = Ieprime
                Rminus = su.difference(Sp, su.difference(Iprime, I, 'name'), 'name')
                DeRminus = su.union(Rminus, gu.descendants(Rminus, GVleqX), 'name')
                GR = gu.subgraph(GVleqX, su.difference(R, DeRminus, 'name'))
                Rprime = ConditionalIndependencies.C(GR,X)

                admissiblePairs.append((Iprime,Rprime))
            else:
                Spuprime = ConditionalIndependencies.GetImproperSp(G,X,VleqX,Ieprime,Sp,Spprime)
                Spdprime = su.difference(Spprime, Spuprime, 'name')

                ConditionalIndependencies.Listv1(G,X,VleqX,I,Ieprime,R,Sp,Spuprime,Spdprime,admissiblePairs)

    @staticmethod
    def GetImproperSp(G,X,VleqX,Iextend,Sp,Spd):
        Spu = []

        GVleqX = gu.subgraph(G, VleqX)

        # An(X) cannot be excluded from G
        SpToSearch = su.difference(Spd, gu.ancestors(X,GVleqX), 'name')

        SpIteration = [[]]
        # SpIteration.extend(list(map(lambda n: ou.makeArray(n), Spd)))
        SpIteration.extend(list(map(lambda n: ou.makeArray(n), SpToSearch)))

        # if X['name'] == 'J':
        # print('*** GetImproperSp ***')
        # print('X: ' + X['name'])
        # print('Ie: ' + nodeNamesToString(Iextend))
        # print('Sp: ' + nodeNamesToString(Spd))

        for s in SpIteration:
            # Step 1
            Des = gu.descendantsPlus(s, GVleqX)
            DesSp = su.intersection(Des, Sp, 'name')
            Ieprime = su.difference(Iextend, DesSp, 'name')

            # if X['name'] == 'E':
            #     print('*** GetImproperSp ***')
            #     print('s: ' + nodeNamesToString(s))
            #     print('Iextend: ' + nodeNamesToString(Iextend))
            #     print('DesSp: ' + nodeNamesToString(DesSp))
            #     print('Ieprime: ' + nodeNamesToString(Ieprime))
            #     print('Adm: ' + str(ConditionalIndependencies.IsAdmissible(G,X,VleqX,Ieprime)))

            if ConditionalIndependencies.IsAdmissible(G,X,VleqX,Ieprime):
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

            # if X['name'] == 'E':
            #     if nodeNamesToString(s) == 'A':
            #         print('*** GetImproperSp ***')
            #         print('s: ' + nodeNamesToString(s))
            #         print('Sps: ' + nodeNamesToString(Sps))

            isSproper = False

            for sprime in Sps:
                Ansprime = su.union([sprime], gu.ancestors(sprime, GVleqX), 'name')
                AnSpprime = su.intersection(Ansprime, Spprime, 'name')

                DeAnSpprime = gu.descendantsPlus(AnSpprime, GVleqX)
                DeSpprimeMinusAnSpprime = gu.descendantsPlus(su.difference(Spprime, AnSpprime, 'name'), GVleqX)

                # fix from v4
                # Gprime = gu.subgraph(GVleqX, su.difference(DeAnSpprime, su.difference(Spprime, AnSpprime, 'name'), 'name'))
                Gprime = gu.subgraph(GVleqX, su.difference(DeAnSpprime, DeSpprimeMinusAnSpprime, 'name'))

                DeAnSpInGprime = gu.descendantsPlus(AnSpprime, Gprime)

                # if X['name'] == 'E':
                #     if nodeNamesToString(s) == 'A':
                #         print('Gprime.nodes: ' + nodeNamesToString(Gprime.nodes))
                #         print('ds: ' + nodeNamesToString(su.difference(DeAnSpInGprime, AnSpprime, 'name')))

                for d in su.difference(DeAnSpInGprime, AnSpprime, 'name'):
                    C = ConditionalIndependencies.C(Gprime, AnSpprime)
                    
                    if not su.belongs(d, C, compareNames):
                        # if X['name'] == 'E':
                        #     if nodeNamesToString(s) == 'A':
                        #         print('d: ' + d['name'])
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
    def GetProperSpv1(G,X,VleqX,I,Sp):
        Spu = []

        GVleqX = gu.subgraph(G, VleqX)

        SpIteration = [[]]
        SpIteration.extend(list(map(lambda n: ou.makeArray(n), Sp)))

        # if X['name'] == 'F':
        #     print('calling GP')
        #     print('I: ' + nodeNamesToString(I))
        #     print('Sp: ' + nodeNamesToString(Sp))

        for s in SpIteration:
            # Step 1
            Des = gu.descendants(s, GVleqX)
            DeSp = su.intersection(Des, Sp, 'name')
            Iprime = su.union(I, su.difference(Sp, DeSp, 'name'), 'name')

            if ConditionalIndependencies.IsAdmissible(G,X,VleqX,Iprime):
                if len(s) > 0:
                    Spu.append(s[0])
                else:
                    Spu.append(s)
                
                continue

            # Step 2
            PaIprime = gu.parentsPlus(Iprime, GVleqX)
            Spprime = su.difference(gu.spouses(Iprime,GVleqX), PaIprime, 'name')
            Des = su.union(s, gu.descendants(s, GVleqX), 'name')
            DesSp = su.intersection(Des, Sp, 'name')
            Sps = su.difference(gu.spouses(Iprime,GVleqX), DesSp, 'name')
            Sps = su.difference(Sps, PaIprime, 'name')

            isSproper = False

            for sprime in Sps:
                Ansprime = su.union([sprime], gu.ancestors(sprime, GVleqX), 'name')
                AnSpprime = su.intersection(Ansprime, Spprime, 'name')
                DeAnSp = su.union(AnSpprime, gu.descendants(AnSpprime, GVleqX), 'name')
                Gprime = gu.subgraph(GVleqX, su.difference(DeAnSp, su.difference(Spprime, AnSpprime, 'name'), 'name'))

                DeAnSpInGprime = su.union(AnSpprime, gu.descendants(AnSpprime, Gprime), 'name')

                for d in su.difference(DeAnSpInGprime, AnSpprime, 'name'):
                    C = ConditionalIndependencies.C(Gprime, AnSpprime)
                    # if X['name'] == 'F':
                    #     print('I\': ' + nodeNamesToString(Iprime))
                    #     print('G\'.nodes: ' + nodeNamesToString(Gprime.nodes))
                    #     print(AnSpprime)
                    #     print(C)
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
    def ListDec(G, T):
        if T is None:
            return None

        if len(T) == 0:
            return []
        
        Decs = []

        for i in range(1,len(T) + 1):
            combs = list(itertools.combinations(T, i))

            for I in combs:
                I = list(I)
                E = su.difference(T, I, 'name')

                DeI = gu.descendants(I, G)

                if len(su.intersection(DeI, E, 'name')) > 0:
                    continue
                else:
                    Decs.append(I)

        return Decs

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
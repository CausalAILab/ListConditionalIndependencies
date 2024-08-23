import itertools

from src.inference.utils.graph_utils import GraphUtils as gu, sortByName
from src.inference.utils.set_utils import SetUtils as su
from src.common.object_utils import ObjectUtils as ou
from src.adjustment.adjustment_sets_utils import nodeNamesToString, TestSep
from src.path_analysis.d_separation import DSeparation
from src.projection.projection_utils import ProjectionUtils as pu

def isSymmetric(ci1, ci2):
    isXYEqual = su.equals(ci1['X'], ci2['Y'], 'name')
    isYXEqual = su.equals(ci1['Y'], ci2['X'], 'name')

    return isXYEqual and isYXEqual

class ConditionalIndependencies():

    @staticmethod
    def ListGMP(G,V):
        """
        Enumerates all conditional independence relations (CIs) invoked by the global Markov property (GMP).
        Reference: Figure D.0.1 in Appendix

        Parameters
        ----------
        G : Graph
            A causal graph.
        V : Node[]
            A set of variables.

        Returns
        -------
        Dict
            A list of objects where each object represents one CI invoked by GMP.
        """
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
    def ListCIBF(G, V, onlyMaximalAns=True, Vordered=None, measuredParams=None):
        """
        Enumerates all conditional independence relations (CIs) invoked by the ordered local Markov property (LMP).
        Reference: Algorithm 1

        Parameters
        ----------
        G : Graph
            A causal graph.
        V : Node[]
            A set of variables.
        onlyMaximalAns: boolean
            Default is True. If set to true, ListCIBF considers only maximal ancestral sets to genereate CIs invoked by LMP.
        Vordered: Node[]
            Default is None. If specified, ListCIBF uses the given fixed consisent ordering of variables.
        measuredParams: Dict
            Default is None. If specified, ListCIBF records the following measured parameters (s: size of the largest c-component, Snum: total number of ancestral sets, Splusnum: total number of maximal ancestral sets) to measuredParams after ListCIBF terminates.

        Returns
        -------
        Dict
            A list of objects where each object represents one CI invoked by LMP.
        """
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return []

        if Vordered is not None:
            V = Vordered
        else:
            V = su.intersection(gu.topoSort(G), V, 'name')

        # print('Variables (topo sorted):')
        # print(nodeNamesToString(V, False))
        
        CI = []
        Ss = []
        Spluss = []
        AC = []

        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)
            
            # brute force all maximal ancestral sets S+
            AnX = gu.ancestorsPlus(X, GVleqX)
            VnonAnX = su.difference(VleqX, AnX, 'name')

            for i in range(len(VnonAnX) + 1):
                combs = list(itertools.combinations(VnonAnX, i))

                for Sminus in combs:
                    S = su.union(AnX, Sminus, 'name')

                    # check if S is ancestral
                    AnS = gu.ancestors(S, GVleqX)

                    if not su.equals(S, AnS, 'name'):
                        continue

                    GS = gu.subgraph(GVleqX, S)
                    C = ConditionalIndependencies.C(GS, X)

                    Ss.append(S)
                    AC.append(C)
                    
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

                        Spluss.append(Splus)

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

        if measuredParams is not None:
            measuredParams['Snum'] = len(Ss)
            measuredParams['Splusnum'] = len(Spluss)

            if len(AC) > 0:
                measuredParams['s'] = len(max(AC, key=len))
            else:
                measuredParams['s'] = 1

        return CI
    

    @staticmethod
    def ListCI(G, V, Vordered = None):
        """
        Enumerates all conditional independence relations (CIs) invoked by the c-component local Markov property (C-LMP).
        Reference: Algorithm 2

        Parameters
        ----------
        G : Graph
            A causal graph.
        V : Node[]
            A set of variables.
        Vordered: Node[]
            Default is None. If specified, ListCI uses the given fixed consisent ordering of variables.

        Returns
        -------
        Dict
            A list of objects where each object represents one CI invoked by C-LMP.
        """
        if G is None or V is None or len(su.difference(V, G.nodes, 'name')) > 0:
            return None
        
        if Vordered is not None:
            V = Vordered
        else:
            V = su.intersection(gu.topoSort(G), V, 'name')

        # print('Variables (topo sorted):')
        # print(nodeNamesToString(V, False))

        CI = []

        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)
            
            AnX = su.union(gu.ancestors(X, GVleqX), [X], 'name')
            GAnX = gu.subgraph(GVleqX, AnX)
            I = ConditionalIndependencies.C(GAnX, X)
            R = ConditionalIndependencies.C(GVleqX, X)

            ConditionalIndependencies.ListCIX(GVleqX, X, VleqX, I, R, CI)

        return CI
    

    @staticmethod
    def ListCIX(GVleqX, X, VleqX, I, R, CI):
        """
        Enumerates all conditional independence relations (CIs) invoked by the c-component local Markov property (C-LMP) for a fixed variable X.
        Reference: Algorithm 2

        Parameters
        ----------
        GVleqX : Graph
            A causal graph. Assumed to be a subgraph of the original graph G consisting of nodes VleqX: all variables up to X in a consistent ordering.
        X : Node
            A variable.
        VleqX : Node[]
            A set of variables up to X in a consistent ordering.
        I: Node[]
            An ancestral c-component (AC) relative to X. Enforces the constraint that every node in I must be included in any admissible ancestral c-component (AAC).
        R: Node[]
            An AC relative to X. Enforces the constraint that any node in R could be included in any AAC.
        CI: Dict
            A collection of all CIs invoked by C-LMP that are generated up to the current point of execution.
        """
        if ConditionalIndependencies.FindAAC(GVleqX, X, VleqX, I, R) is not None:
            if su.equals(I, R, 'name'):
                C = I
                Z = ConditionalIndependencies.mbplus(GVleqX, VleqX, X, C)
                Splus = ConditionalIndependencies.Splus(GVleqX, VleqX, X, C)
                W = su.difference(Splus, su.union(Z, [X], 'name'), 'name')

                CI.append({
                    'X': X,
                    'W': W,
                    'Z': Z
                })
            else:
                SpI = su.difference(gu.spouses(I, GVleqX), I, 'name')
                T = su.intersection(R, SpI, 'name')

                if su.isEmpty(T):
                    print('Bug: T cannot be empty!')
                    return

                s = T[0]
                Des = gu.descendantsPlus(s, GVleqX)
                Gprime = gu.subgraph(GVleqX, su.difference(R, Des, 'name'))
                Rprime = ConditionalIndependencies.C(Gprime,X)

                AnIs = gu.ancestorsPlus(su.union(I, [s], 'name'), GVleqX)
                Gprime = gu.subgraph(GVleqX, AnIs)
                Iprime = ConditionalIndependencies.C(Gprime, X)

                ConditionalIndependencies.ListCIX(GVleqX, X, VleqX, I, Rprime, CI)
                ConditionalIndependencies.ListCIX(GVleqX, X, VleqX, Iprime, R, CI)
    

    @staticmethod
    def FindAAC(GVleqX, X, VleqX, I, R):
        """
        Outputs an admissible ancestral c-component (AAC) C relative to a variable X under the constraint I <= C <= R, if such C exists. Outputs None otherwise.
        Reference: Figure 7

        Parameters
        ----------
        GVleqX : Graph
            A causal graph. Assumed to be a subgraph of the original graph G consisting of nodes VleqX: all variables up to X in a consistent ordering.
        X : Node
            A variable.
        VleqX : Node[]
            A set of variables up to X in a consistent ordering.
        I: Node[]
            An ancestral c-component (AC) relative to X. Enforces the constraint that every node in I must be included in C.
        R: Node[]
            An AC relative to X. Enforces the constraint that any node in R could be included in C.

        Returns
        ----------
        Node[]
            An AAC C under the constraint I <= C <= R, if such C exists. None otherwise.
        """
        if ConditionalIndependencies.IsAdmissible(GVleqX, X, VleqX, I):
            return I
        else:
            PaR = gu.parentsPlus(R, GVleqX)
            SpI = gu.spouses(I, GVleqX)
            PaI = gu.parentsPlus(I, GVleqX)

            dCandidates = gu.descendantsPlus(su.difference(SpI, PaI, 'name'), GVleqX)
            
            for d in dCandidates:
                Z = ConditionalIndependencies.FindSeparator(GVleqX, X, d, PaI, PaR)
                
                if Z is not None:
                    AnIZ = gu.ancestorsPlus(su.union(I, Z, 'name'), GVleqX)
                    Gprime = gu.subgraph(GVleqX, AnIZ)
                    C = ConditionalIndependencies.C(Gprime, X)

                    return C
        return None
    

    @staticmethod
    def IsAdmissible(GVleqX, X, VleqX, C):
        """
        Verifies whether a given ancestral c-component (AC) relative to X is admissible or not.
        Reference: Figure B.2.1 in Appendix

        Parameters
        ----------
        GVleqX : Graph
            A causal graph. Assumed to be a subgraph of the original graph G consisting of nodes VleqX: all variables up to X in a consistent ordering.
        X : Node
            A variable.
        VleqX : Node[]
            A set of variables up to X in a consistent ordering.
        C: Node[]
            An ancestral c-component (AC) relative to X.

        Returns
        ----------
        Boolean
            True if C is an AAC relative to X. False otherwise.
        """
        Z = ConditionalIndependencies.mbplus(GVleqX, VleqX, X, C)
        Splus = ConditionalIndependencies.Splus(GVleqX, VleqX, X, C)
        W = su.difference(Splus, su.union(Z, [X], 'name'), 'name')

        return not su.isEmpty(W)


    @staticmethod
    def FindSeparator(G, X, Y, I, R):
        """
        Generates a set of variables Z that d-separates X and Y in G under the constraint I \ (X \cup Y) <= Z <= R \ (X \cup Y) if such Z exists. Outputs None otherwise.
        Reference: Figure B.2.2 in Appendix

        Parameters
        ----------
        G : Graph
            A causal graph.
        X : Node[]
            A set of variables.
        Y : Node[]
            A set of variables.
        I: Node[]
            A set of variables.
        R: Node[]
            A set of variables.

        Returns
        ----------
        Node[]
            A set of variables Z if and only if there exists Z (under the constraint I \ (X \cup Y) <= Z <= R \ (X \cup Y)) that d-separates X and Y. None otherwise.
        """
        X = ou.makeArray(X)
        Y = ou.makeArray(Y)
        I = ou.makeArray(I)
        R = ou.makeArray(R)

        XY = su.union(X, Y, 'name')
        XYI = su.union(XY, I, 'name')
        Rprime = su.difference(R, XY, 'name')
        Z = su.intersection(Rprime, gu.ancestorsPlus(XYI, G), 'name')

        Ga = pu.unproject(G)
        if TestSep(Ga, X, Y, Z):
            return Z
        else:
            return None


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
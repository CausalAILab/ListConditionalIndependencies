import random
from datetime import datetime

from src.graph.classes.graph import Graph
from src.graph.classes.graph_defs import latentNodeType, directedEdgeType, bidirectedEdgeType
from src.testable_implications.ci_defs import algListGMP, algListCIBF, algListCI
from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import GraphUtils as gu
from src.testable_implications.conditional_independencies import ConditionalIndependencies as ci
from src.projection.projection_utils import ProjectionUtils as pu


class ExperimentUtils():

    @staticmethod
    def measureParams(G, alg=algListCI.id_):
        if G is None:
            return []

        measuredParams = {}

        start = datetime.now()

        if alg == algListGMP.id_:
            CI = ci.ListGMP(G, G.nodes)
        elif alg == algListCIBF.id_:
            CI = ci.ListCIBF(G, G.nodes, True, None, measuredParams)
        elif alg == algListCI.id_:
            CI = ci.ListCI(G, G.nodes)

        end = datetime.now()

        if alg == algListCIBF.id_:
            Snum = measuredParams['Snum']
            Splusnum = measuredParams['Splusnum']
            s = measuredParams['s']
        elif alg == algListCI.id_:
            V = su.intersection(gu.topoSort(G), G.nodes, 'name')
            ACsizes = []

            for X in V:
                VleqX = V[:V.index(X)+1]
                GVleqX = gu.subgraph(G, VleqX)
                
                R = ci.C(GVleqX,X)
                ACsizes.append(len(R))

            if len(ACsizes) > 0:
                s = max(ACsizes)
            else:
                s = 1

        # get parameters
        n = len(G.nodes)
        m = len(G.edges)
        md = len(list(filter(lambda e: e['type_'] == directedEdgeType.id_, G.edges)))
        mb = len(list(filter(lambda e: e['type_'] == bidirectedEdgeType.id_, G.edges)))
        CIsize = len(CI)
        runtime = end - start

        params = []

        if alg == algListGMP.id_:
            params = [n, m, md, mb, CIsize, runtime]
        elif alg == algListCIBF.id_:
            params = [n, m, md, mb, CIsize, runtime, s, Snum, Splusnum]
        elif alg == algListCI.id_:
            params = [n, m, md, mb, CIsize, runtime, s]

        # params = [s, CIsize, runtime]

        return params
    
    @staticmethod
    def constructDirGraph(n, m):
        G = Graph()
        G.addRandomNodes(n)
        G.addRandomEdges(m)

        return G

    @staticmethod
    def constructBidirGraph(n, m):
        G = Graph()
        G.toRandomGraph(n,m,bidirectedEdgeType.id_)

        return G

    @staticmethod
    def constructMixedGraph(n, md, mb):
        mMax = n * (n-1) / 2.0

        if md + mb > mMax:
            return None
        
        G = Graph()
        G.addRandomNodes(n)
        G.addRandomEdges(md)
        G.addRandomEdges(mb, bidirectedEdgeType.id_)

        return G
    
    @staticmethod
    def constructBidirConvGraph(n, m, mb=0):
        G = Graph()
        G.toRandomGraph(n,m)

        # # sample x% of edges and turn those to bidirected
        if mb > 0 and mb <= m:
            edges = G.edges

            indices = random.sample(range(m), mb)

            newEdges = []
            
            for i in range(m):
                edge = edges[i]

                if i in indices:
                    edge['type_'] = bidirectedEdgeType.id_
                    
                newEdges.append(edge)

            G.edges = newEdges

        return G
    
    @staticmethod
    def applyProjection(G, latentFraction=0.3):
        if latentFraction == 0:
            return G
        
        nodes = G.nodes
        edges = G.edges

        # sample x% of nodes and turn those to latent
        k = int(len(nodes) * latentFraction)
        indices = random.sample(range(len(nodes)), k)

        newNodes = []
        V = []

        for i in range(len(nodes)):
            node = nodes[i]

            if i in indices:
                node['type_'] = latentNodeType.id_
            else:
                V.append(node)

            newNodes.append(node)
        
        Gp = G.copy()
        Gp.nodes = newNodes
        Gp.edges = edges
        Gp = pu.projectOver(Gp,V)

        return Gp
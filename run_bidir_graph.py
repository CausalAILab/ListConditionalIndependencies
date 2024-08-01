# import sys
import random
from datetime import datetime

from src.graph.classes.graph import Graph
from src.graph.classes.graph_defs import bidirectedEdgeType
from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import GraphUtils as gu
from src.testable_implications.conditional_independencies import ConditionalIndependencies
from src.adjustment.adjustment_sets_utils import writeNodeNames

# def testERBidirGraphs(numGraphs, n, p):
#     CIs = []
#     runtimes = []

#     line = ''

#     for i in range(numGraphs):
#         G = Graph()
#         G.toErdosRenyiGraph(n,p)

#         # make edges as bidirected
#         edges = G.edges
#         newEdges = []
        
#         for edge in edges:
#             edge['type_'] = bidirectedEdgeType.id_
#             newEdges.append(edge)

#         G.edges = newEdges

#         start = datetime.now()
#         CI = ConditionalIndependencies.ListCI(G, G.nodes)
#         end = datetime.now()

#         CIs.append(CI)
#         runtimes.append(end - start)

#         V = su.intersection(gu.topoSort(G), G.nodes, 'name')
#         ACsizes = []

#         for X in V:
#             VleqX = V[:V.index(X)+1]
#             GVleqX = gu.subgraph(G, VleqX)
            
#             R = ConditionalIndependencies.C(GVleqX,X)
#             ACsizes.append(len(R))

#         s = max(ACsizes)

#         line = str(s) + ' ' + str(len(CI)) + ' ' + str(end - start)
#         print(line)

def testBidirGraphs(numGraphs, n, m):
    CIs = []
    runtimes = []

    line = ''

    for i in range(numGraphs):
        G = Graph()
        G.toRandomGraph(n,m,bidirectedEdgeType.id_)

        start = datetime.now()
        CI = ConditionalIndependencies.ListCI(G, G.nodes)
        end = datetime.now()

        CIs.append(CI)
        runtimes.append(end - start)

        V = su.intersection(gu.topoSort(G), G.nodes, 'name')
        ACsizes = []

        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)
            
            R = ConditionalIndependencies.C(GVleqX,X)
            ACsizes.append(len(R))

        s = max(ACsizes)

        line = str(s) + ' ' + str(len(CI)) + ' ' + str(end - start)
        print(line)


def testBidirConvertedGraphs(numGraphs, n, m, bidirectedEdgesFraction=None):
    CIs = []
    runtimes = []

    line = ''

    for i in range(numGraphs):
        G = Graph()
        G.toRandomGraph(n,m)

        # # sample x% of edges and turn those to bidirected
        if bidirectedEdgesFraction is not None:
            edges = G.edges

            k = int(m * bidirectedEdgesFraction)
            indices = random.sample(range(m), k)

            newEdges = []
            
            for i in range(m):
                edge = edges[i]

                if i in indices:
                    edge['type_'] = bidirectedEdgeType.id_
                    
                newEdges.append(edge)

            G.edges = newEdges

        start = datetime.now()
        CI = ConditionalIndependencies.ListCI(G, G.nodes)
        end = datetime.now()

        CIs.append(CI)
        runtimes.append(end - start)

        V = su.intersection(gu.topoSort(G), G.nodes, 'name')
        ACsizes = []

        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)
            
            R = ConditionalIndependencies.C(GVleqX,X)
            ACsizes.append(len(R))

        s = max(ACsizes)

        line = str(s) + ' ' + str(len(CI)) + ' ' + str(end - start)
        print(line)

if __name__ == '__main__':
    numGraphs = 9
    n = 30
    m = int(n * 1.5)
    numDivisions = 10

    # test bidirected graphs
    # for k in range(numDivisions):
    #     bidirectedEdgesFraction = k * 0.1
    #     testBidirGraphs(numGraphs, n, int(m * bidirectedEdgesFraction))

    testBidirGraphs(numGraphs, n, int(m * 0.7))

    # test bidirected (converted) graphs
    # for k in range(numDivisions):
    #     bidirectedEdgesFraction = k * 0.1
    #     testBidirConvertedGraphs(numGraphs, n, m, bidirectedEdgesFraction)

    # testBidirConvertedGraphs(numGraphs, n, m, 0.1)

    # test clique graphs
    # for k in range(numDivisions):
    #     bidirectedEdgesFraction = k * (1.0/numDivisions) + 0.05
    #     maxNumEdges = int(0.5 * n * (n-1))
    #     testBidirGraphs(numGraphs, n, int(maxNumEdges * bidirectedEdgesFraction))

    # testBidirGraphs(numGraphs, n, 0)
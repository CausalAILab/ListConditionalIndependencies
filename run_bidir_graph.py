import sys
from datetime import datetime

from src.graph.classes.graph import Graph
from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import GraphUtils as gu
from src.testable_implications.conditional_independencies import ConditionalIndependencies
from src.adjustment.adjustment_sets_utils import writeNodeNames

def testRandomGraphs(alg, numGraphs, n, e, bidirectedEdgesFraction=None):
    CIs = []
    runtimes = []

    line = ''

    for i in range(numGraphs):
        G = Graph()
        G.toRandomGraph(n,e,bidirectedEdgesFraction)

        start = datetime.now()

        if alg == 'gmp':
            CI = ConditionalIndependencies.GMP(G, G.nodes)
            end = datetime.now()
        elif alg == 'lmp':
            CI = ConditionalIndependencies.LMP(G, G.nodes, True)
            end = datetime.now()
        elif alg == 'listci':
            CI = ConditionalIndependencies.ListCI(G, G.nodes)
            end = datetime.now()

            V = su.intersection(gu.topoSort(G), G.nodes, 'name')
            ACsizes = []

            for X in V:
                VleqX = V[:V.index(X)+1]
                GVleqX = gu.subgraph(G, VleqX)
                
                GVleqX = gu.subgraph(G, VleqX)
                R = ConditionalIndependencies.C(GVleqX,X)
                ACsizes.append(len(R))

            s = max(ACsizes)

        CIs.append(CI)
        runtimes.append(end - start)

        line = str(s) + ' ' + str(len(CI)) + ' ' + str(end - start)
        print(line)

if __name__ == '__main__':
    numGraphs = 10
    numNodes = 40
    numEdges = int(numNodes * 2)
    bidirectedEdgesDivisions = 10

    for k in range(bidirectedEdgesDivisions):
        bidirectedEdgesFraction = k * 0.1
        testRandomGraphs('listci',numGraphs, numNodes, numEdges, bidirectedEdgesFraction)

    # testRandomGraphs('listci',numGraphs, numNodes, numEdges, 0.5)
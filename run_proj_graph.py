# import sys
import random
from datetime import datetime

from src.graph.classes.graph import Graph
from src.graph.classes.graph_defs import latentNodeType
from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import GraphUtils as gu
from src.projection.projection_utils import ProjectionUtils as pu
from src.testable_implications.conditional_independencies import ConditionalIndependencies
from src.adjustment.adjustment_sets_utils import writeNodeNames

def testRandomGraphs(alg, numGraphs, n, e, latentFraction=None):
    CIs = []
    runtimes = []

    line = ''

    for i in range(numGraphs):
        G = Graph()
        G.toRandomGraph(n,e)

        nodes = G.nodes
        edges = G.edges

        # sample x% of nodes and turn those to latent
        if latentFraction is not None:
            k = int(len(nodes) * latentFraction)
            indices = random.sample(range(len(nodes)), k)

            V = []
            Obs = []

            for i in range(len(nodes)):
                node = nodes[i]

                if i in indices:
                    node['type_'] = latentNodeType.id_
                else:
                    Obs.append(node)

                V.append(node)
        
        G.nodes = V
        G.edges = edges

        G = pu.projectOver(G,Obs)

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
    numNodes = 100
    numDirectedEdges = int(numNodes * 2)
    numLatentRatio = 10

    # for k in range(numLatentRatio):
    #     latentFraction = k * 0.1
    #     testRandomGraphs('listci', numGraphs, numNodes, numDirectedEdges, latentFraction)

    testRandomGraphs('listci', numGraphs, numNodes, numDirectedEdges, 0.3)
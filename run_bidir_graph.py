import random
from datetime import datetime

from src.graph.classes.graph import Graph
from src.graph.classes.graph_defs import directedEdgeType, bidirectedEdgeType
from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import GraphUtils as gu
from src.testable_implications.conditional_independencies import ConditionalIndependencies


def measureParams(G):
    start = datetime.now()
    CI = ConditionalIndependencies.ListCI(G, G.nodes)
    end = datetime.now()

    V = su.intersection(gu.topoSort(G), G.nodes, 'name')
    ACsizes = []

    for X in V:
        VleqX = V[:V.index(X)+1]
        GVleqX = gu.subgraph(G, VleqX)
        
        R = ConditionalIndependencies.C(GVleqX,X)
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

    # params = [n, m, md, mb, CIsize, runtime, s]
    params = [s, CIsize, runtime]

    return params


def constructBidirGraph(n,m):
    G = Graph()
    G.toRandomGraph(n,m,bidirectedEdgeType.id_)

    return G


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


def testBidirGraphs(numGraphs, n, m):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        G = constructBidirGraph(n,m)
        params = measureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testBidirGraphsBatch(numGraphs, n, m, numDivisions=10):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            G = constructBidirGraph(n, int(m * bidirectedEdgesFraction))
            params = measureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testBidirConvertedGraphs(numGraphs, n, m, bidirectedEdgesFraction=0):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        G = constructBidirConvGraph(n, m, int(m * bidirectedEdgesFraction))
        params = measureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testBidirConvertedGraphsBatch(numGraphs, n, m, numDivisions=10):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            G = constructBidirConvGraph(n, m, int(m * bidirectedEdgesFraction))
            params = measureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testCliqueGraphs(numGraphs, n, m, bidirectedEdgesFraction=0):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollection.append([])

        G = constructBidirGraph(n, int(mMax * bidirectedEdgesFraction))
        params = measureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testCliqueGraphsBatch(numGraphs, n, numDivisions=20):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.05
            G = constructBidirGraph(n, int(mMax * bidirectedEdgesFraction))
            params = measureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


if __name__ == '__main__':
    numGraphs = 10
    n = 10
    m = int(n * 1.5)
    numDivisions = 10

    testBidirGraphsBatch(numGraphs, n, m, numDivisions)
    # testBidirGraphs(numGraphs, n, int(m * 0.2))

    # testBidirConvertedGraphsBatch(numGraphs, n, m, numDivisions)
    # testBidirConvertedGraphs(numGraphs, n, m, 0.3)

    # testCliqueGraphsBatch(numGraphs, n, numDivisions)
    # testCliqueGraphs(numGraphs, n, 0.2)
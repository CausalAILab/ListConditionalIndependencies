from src.experiment.experiment_utils import ExperimentUtils as eu


def testMixedGraphs(numGraphs, n, m, bidirectedEdgesFraction=0):
    paramsCollection = []

    md = m
    mb = int(md * bidirectedEdgesFraction)

    for i in range(numGraphs):
        paramsCollection.append([])

        # G = constructMixedGraph(n, m, int(m * bidirectedEdgesFraction))
        G = eu.constructMixedGraph(n, md, mb)
        params = eu.measureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testMixedGraphsBatch(numGraphs, n, m, numDivisions=11):
    paramsCollection = []

    md = m

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            
            mb = int(md * bidirectedEdgesFraction)

            # G = constructMixedGraph(n, m, int(m * bidirectedEdgesFraction))
            G = eu.constructMixedGraph(n, md, mb)
            params = eu.measureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


if __name__ == '__main__':
    numGraphs = 5
    numDivisions = 11
    n = 10
    m = int(n * 3)

    testMixedGraphsBatch(numGraphs, n, m, numDivisions)
    # testMixedGraphs(numGraphs, n, m, 0.6)
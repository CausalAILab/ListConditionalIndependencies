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
    timeout = 1 * 60 * 60
    numGraphs = 10
    numDivisions = 10
    n = 30
    m = int(n * 1)
    U = 1.2

    # testMixedGraphsBatch(numGraphs, n, m, numDivisions)
    testMixedGraphs(numGraphs, n, m, U)
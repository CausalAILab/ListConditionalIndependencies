from src.experiment.experiment_utils import ExperimentUtils as eu


def testMixedGraphs(numGraphs, n, m, bidirectedEdgesFraction=0):
    paramsCollection = []

    md = m
    mb = int(md * bidirectedEdgesFraction)

    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructMixedGraph(n, md, mb)
        params = eu.runAlgorithmAndMeasureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    # for line in paramsCollection:
    #     print(' '.join(line))

    eu.printParams(paramsCollection)


def testMixedGraphsBatch(numGraphs, n, m, numDivisions=11):
    paramsCollection = []

    md = m

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            
            mb = int(md * bidirectedEdgesFraction)

            G = eu.constructMixedGraph(n, md, mb)
            params = eu.runAlgorithmAndMeasureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    # for line in paramsCollection:
    #     print(' '.join(line))

    eu.printParams(paramsCollection)


if __name__ == '__main__':
    timeout = 1 * 60 * 60
    numGraphs = 10
    numDivisions = 10
    n = 10
    m = int(n * 1)
    U = 0.2

    # testMixedGraphsBatch(numGraphs, n, m, numDivisions)
    testMixedGraphs(numGraphs, n, m, U)
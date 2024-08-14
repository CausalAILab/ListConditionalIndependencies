from src.experiment.experiment_utils import ExperimentUtils as eu


def testBE1(numGraphs, n, m):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructBidirGraph(n,m)
        params = eu.measureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testBE1Batch(numGraphs, n, m, numDivisions=10):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            G = eu.constructBidirGraph(n, int(m * bidirectedEdgesFraction))
            params = eu.measureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


if __name__ == '__main__':
    timeout = 1 * 60 * 60
    numGraphs = 1
    numDivisions = 10
    n = 20
    m = int(n * 1.5)
    u = 1.0

    # testBE1Batch(numGraphs, n, m)
    testBE1(numGraphs, n, int(m * u))
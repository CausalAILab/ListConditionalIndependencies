from src.experiment.experiment_utils import ExperimentUtils as eu


def testB3(numGraphs, n, m, bidirectedEdgesFraction=0):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructBidirConvGraph(n, m, int(m * bidirectedEdgesFraction))
        params = eu.runAlgorithmAndMeasureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testB3Batch(numGraphs, n, m, numDivisions=10):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            G = eu.constructBidirConvGraph(n, m, int(m * bidirectedEdgesFraction))
            params = eu.runAlgorithmAndMeasureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testDirGraphs(algorithm, numGraphs, n, m):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructDirGraph(n, m)
        params = eu.runAlgorithmAndMeasureParams(G, algorithm)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testDirGraphBatch(algorithm, numGraphs, n, m, numDivisions=11):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            directedEdgesFraction = j * 0.1
            G = eu.constructDirGraph(n, int(m * directedEdgesFraction))
            params = eu.runAlgorithmAndMeasureParams(G, algorithm)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


if __name__ == '__main__':
    numGraphs = 10
    n = 20
    m = int(n * 1.5)
    numDivisions = 10

    # testB3Batch(numGraphs, n, m, numDivisions)
    # testB3(numGraphs, n, m, 0.3)

    # testDirGraphBatch(algorithm, numGraphs, n, m, numDivisions)
    # testDirGraphs(algorithm, numGraphs, n, int(m * 0.))
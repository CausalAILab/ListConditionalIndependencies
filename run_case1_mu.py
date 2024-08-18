from src.experiment.experiment_utils import ExperimentUtils as eu


def testCase1Mu(numGraphs, n, m, bidirectedEdgesFraction=0.2):
    paramsCollection = []

    mb = int(m * bidirectedEdgesFraction)

    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructBidirGraph(n, mb)
        params = eu.runAlgorithmAndMeasureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testCase1MuBatch(numGraphs, n, m, numDivisions=10):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            mb = int(m * bidirectedEdgesFraction)

            G = eu.constructBidirGraph(n, mb)
            params = eu.runAlgorithmAndMeasureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


if __name__ == '__main__':
    timeout = 1 * 60 * 60
    numGraphs = 10
    numDivisions = 10
    n = 20
    m = int(n * 1.5)
    U = 0.2

    testCase1MuBatch(numGraphs, n, m)
    # testCase1Mu(numGraphs, n, m, U)
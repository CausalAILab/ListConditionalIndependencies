from src.experiment.experiment_utils import ExperimentUtils as eu

def testCase1(numGraphs, n, bidirectedEdgesFraction=0):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructBidirGraph(n, int(mMax * bidirectedEdgesFraction))
        params = eu.runAlgorithmAndMeasureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testCase1Batch(numGraphs, n, numDivisions=10):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            G = eu.constructBidirGraph(n, int(mMax * bidirectedEdgesFraction))
            params = eu.runAlgorithmAndMeasureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


if __name__ == '__main__':
    timeout = 1 * 60 * 60
    numGraphs = 10
    numDivisions = 10
    n = 10
    U = 0.2

    testCase1Batch(numGraphs, n, numDivisions)
    # testCase1(numGraphs, n, U)
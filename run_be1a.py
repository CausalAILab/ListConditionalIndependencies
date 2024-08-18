from src.experiment.experiment_utils import ExperimentUtils as eu


def testBE1a(numGraphs, n, bidirectedEdgesFraction):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))
    
    for i in range(numGraphs):
        paramsCollection.append([])

        mb = int(mMax * (1.0 - bidirectedEdgesFraction))
        print(mb)
        G = eu.constructBidirGraph(n, mb)
        params = eu.runAlgorithmAndMeasureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testBE1aBatch(numGraphs, n, numDivisions=10):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            mb = int(mMax * (1.0 - bidirectedEdgesFraction))
            print(mb)
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
    n = 25
    U = 0.9

    # testBE1aBatch(numGraphs, n, numDivisions)
    testBE1a(numGraphs, n, U)
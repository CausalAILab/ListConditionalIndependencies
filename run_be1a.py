from src.experiment.experiment_utils import ExperimentUtils as eu


def testBE1a(numGraphs, n, bidirectedEdgesFraction):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))
    
    for i in range(numGraphs):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []

        mb = int(mMax * (1.0 - bidirectedEdgesFraction))
        
        G = eu.constructBidirGraph(n, mb)
        params = eu.runAlgorithmAndMeasureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollectionText[i].extend(paramsToStr)

        paramsCollectionPerSample.append(params)
        paramsCollection.append(paramsCollectionPerSample)

    # for line in paramsCollectionText:
    #     print(' '.join(line))

    eu.printParams(paramsCollection)


def testBE1aBatch(numGraphs, n, numDivisions=10):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            mb = int(mMax * (1.0 - bidirectedEdgesFraction))
            
            G = eu.constructBidirGraph(n, mb)
            params = eu.runAlgorithmAndMeasureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollectionText[i].extend(paramsToStr)

            paramsCollectionPerSample.append(params)

        paramsCollection.append(paramsCollectionPerSample)

    # for line in paramsCollectionText:
    #     print(' '.join(line))

    eu.printParams(paramsCollection)


if __name__ == '__main__':
    timeout = 1 * 60 * 60
    numGraphs = 10
    numDivisions = 10
    n = 10
    U = 0.5

    # testBE1aBatch(numGraphs, n, numDivisions)
    testBE1a(numGraphs, n, U)
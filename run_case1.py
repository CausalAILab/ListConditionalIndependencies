from src.experiment.experiment_utils import ExperimentUtils as eu

fileName = 'case1_report'

def testCase1(numBatches, n, bidirectedEdgesFraction=0):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numBatches):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []

        G = eu.constructBidirGraph(n, int(mMax * bidirectedEdgesFraction))
        params = eu.runAlgorithmAndMeasureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollectionText[i].extend(paramsToStr)

        paramsCollectionPerSample.append(params)
        paramsCollection.append(paramsCollectionPerSample)

    # for line in paramsCollectionText:
    #     print(' '.join(line))

    eu.writeParamsToCsv(fileName, paramsCollection)


def testCase1Batch(numBatches, n, numDivisions=10):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numBatches):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []

        line = 'Running a batch of samples [' + str(i * 10 + 1) + ', ' + str((i+1) * 10) + ']'
        print(line)

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            G = eu.constructBidirGraph(n, int(mMax * bidirectedEdgesFraction))
            params = eu.runAlgorithmAndMeasureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollectionText[i].extend(paramsToStr)

            paramsCollectionPerSample.append(params)

        paramsCollection.append(paramsCollectionPerSample)

    # for line in paramsCollectionText:
    #     print(' '.join(line))

    eu.writeParamsToCsv(fileName, paramsCollection)


if __name__ == '__main__':
    numBatches = 10
    numDivisions = 10
    n = 10
    U = 0.2

    testCase1Batch(numBatches, n, numDivisions)
    # testCase1(numBatches, n, U)
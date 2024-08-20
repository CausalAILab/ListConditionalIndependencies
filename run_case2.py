from src.experiment.experiment_utils import ExperimentUtils as eu

fileName = 'case2_report'

def testCase2(numBatches, n, bidirectedEdgesFraction=0.2):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(n * (n-1) * 0.5)
    md = n
    mb = int(mMax * bidirectedEdgesFraction)
    
    for i in range(numBatches):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []

        G = eu.constructMixedGraph(n, md, mb)
        params = eu.runAlgorithmAndMeasureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollectionText[i].extend(paramsToStr)

        paramsCollectionPerSample.append(params)
        paramsCollection.append(paramsCollectionPerSample)

    # for line in paramsCollectionText:
    #     print(' '.join(line))

    eu.writeParamsToCsv(fileName, paramsCollection)


def testCase2Batch(numBatches, n, numDivisions=10):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(n * (n-1) * 0.5)
    md = n

    for i in range(numBatches):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []

        line = 'Running a batch of samples [' + str(i * 10 + 1) + ', ' + str((i+1) * 10) + ']'
        print(line)

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            mb = int(mMax * bidirectedEdgesFraction)

            G = eu.constructMixedGraph(n, md, mb)
            params = eu.runAlgorithmAndMeasureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollectionText[i].extend(paramsToStr)

            paramsCollectionPerSample.append(params)

        paramsCollection.append(paramsCollectionPerSample)

    # for line in paramsCollection:
    #     print(' '.join(line))

    eu.writeParamsToCsv(fileName, paramsCollection)


if __name__ == '__main__':
    numBatches = 10
    numDivisions = 10
    n = 10
    U = 0.2

    testCase2Batch(numBatches, n, numDivisions)
    # testCase2(numBatches, n, U)
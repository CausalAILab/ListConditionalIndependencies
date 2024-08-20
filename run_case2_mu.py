from src.experiment.experiment_utils import ExperimentUtils as eu

fileName = 'case2_mu_report'

def testCase2Mu(numBatches, n, md, bidirectedEdgesFraction=0.2):
    paramsCollectionText = []
    paramsCollection = []

    mb = int(md * bidirectedEdgesFraction)

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


def testCase2MuBatch(numBatches, n, md, numDivisions=10):
    paramsCollectionText = []
    paramsCollection = []

    for i in range(numBatches):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []

        line = 'Running a batch of samples [' + str(i * 10 + 1) + ', ' + str((i+1) * 10) + ']'
        print(line)

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            
            mb = int(md * bidirectedEdgesFraction)

            G = eu.constructMixedGraph(n, md, mb)
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

    testCase2MuBatch(numBatches, n, n, numDivisions)
    # testCase2Mu(numBatches, n, n, U)
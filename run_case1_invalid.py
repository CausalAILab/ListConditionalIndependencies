from src.experiment.experiment_utils import ExperimentUtils as eu
from src.testable_implications.ci_defs import algListCIBF

fileName = 'case1_invalid_CIs_report'

def testCase1Invalid(numGraphs, n, bidirectedEdgesFraction=0):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))
    mb = int(mMax * bidirectedEdgesFraction)

    for i in range(numGraphs):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []
        
        G = eu.constructBidirGraph(n, mb)
        params = eu.runAlgorithmAndMeasureParams(G, algListCIBF.id_)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollectionText[i].extend(paramsToStr)

        paramsCollectionPerSample.append(params)
        paramsCollection.append(paramsCollectionPerSample)

    # for line in paramsCollection:
    #     print(' '.join(line))

    eu.writeParamsToCsv(fileName, paramsCollection, algListCIBF.id_)


def testCase1InvalidBatch(numGraphs, n, numDivisions=10):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []

        line = 'Running a batch of samples [' + str(i * 10 + 1) + ', ' + str((i+1) * 10) + ']'
        print(line)

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            mb = int(mMax * bidirectedEdgesFraction)
            G = eu.constructBidirGraph(n, mb)
            params = eu.runAlgorithmAndMeasureParams(G, algListCIBF.id_)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollectionText[i].extend(paramsToStr)

            paramsCollectionPerSample.append(params)

        paramsCollection.append(paramsCollectionPerSample)

    # for line in paramsCollectionText:
    #     print(' '.join(line))

    eu.writeParamsToCsv(fileName, paramsCollection, algListCIBF.id_)


if __name__ == '__main__':
    # timeout = 1 * 60 * 60
    numGraphs = 10
    numDivisions = 10
    n = 10
    U = 0.2

    testCase1InvalidBatch(numGraphs, n, numDivisions)
    # testCase1Invalid(numGraphs, n, U)
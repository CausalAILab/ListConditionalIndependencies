from src.experiment.experiment_utils import ExperimentUtils as eu
from src.testable_implications.ci_defs import algListCIBF

def testCase1Invalid(numGraphs, n, bidirectedEdgesFraction=0):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))
    mb = int(mMax * bidirectedEdgesFraction)

    for i in range(numGraphs):
        paramsCollection.append([])
        
        G = eu.constructBidirGraph(n, mb)
        params = eu.runAlgorithmAndMeasureParams(G, algListCIBF.id_)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testCase1InvalidBatch(numGraphs, n, numDivisions=10):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            mb = int(mMax * bidirectedEdgesFraction)
            G = eu.constructBidirGraph(n, mb)
            params = eu.runAlgorithmAndMeasureParams(G, algListCIBF.id_)
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

    testCase1InvalidBatch(numGraphs, n, numDivisions)
    # testCase1Invalid(numGraphs, n, U)
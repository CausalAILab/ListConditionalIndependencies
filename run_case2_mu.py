from src.experiment.experiment_utils import ExperimentUtils as eu


def testCase2Mu(numGraphs, n, md, bidirectedEdgesFraction=0.2):
    paramsCollection = []

    mb = int(md * bidirectedEdgesFraction)

    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructMixedGraph(n, md, mb)
        params = eu.runAlgorithmAndMeasureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testCase2MuBatch(numGraphs, n, md, numDivisions=10):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            
            mb = int(md * bidirectedEdgesFraction)

            G = eu.constructMixedGraph(n, md, mb)
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

    testCase2MuBatch(numGraphs, n, n, numDivisions)
    # testCase2Mu(numGraphs, n, n, U)
from src.experiment.experiment_utils import ExperimentUtils as eu


def testBT2(numGraphs, n, bidirectedEdgesFraction=0):
    paramsCollection = []

    mMax = int(n * (n-1) * 0.5)
    md = int(n * 3.0)
    # md = int(mMax * 0.1)
    mb = int(mMax * bidirectedEdgesFraction)
    
    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructMixedGraph(n, md, mb)
        params = eu.measureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testBT2Batch(numGraphs, n, numDivisions=10):
    paramsCollection = []

    mMax = int(n * (n-1) * 0.5)
    md = int(n * 3.0)
    # md = int(mMax * 0.1)

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            mb = int(mMax * bidirectedEdgesFraction)

            G = eu.constructMixedGraph(n, md, mb)
            params = eu.measureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))

if __name__ == '__main__':
    timeout = 1 * 60 * 60
    numGraphs = 10
    numDivisions = 10
    n = 70
    U = 0.05

    testBT2Batch(numGraphs, n, numDivisions)
    # testBT2(numGraphs, n, U)
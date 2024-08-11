from src.experiment.experiment_utils import ExperimentUtils as eu


def testBT2(numGraphs, n, pd, bidirectedEdgesFraction=0):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))
    md = int(mMax * pd)
    mb = int(mMax * bidirectedEdgesFraction)

    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructMixedGraph(n, md, mb)
        params = eu.measureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testBT2Batch(numGraphs, n, pd, numDivisions=10):
    paramsCollection = []

    mMax = int(n * (n-1) * 0.5)
    md = int(mMax * pd)
    # md = int(n * 1.0)

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
    numGraphs = 10
    numDivisions = 10
    n = 30
    pd = 0.1

    testBT2Batch(numGraphs, n, pd, numDivisions)
    # testBT2(numGraphs, n, pd, 0.9)
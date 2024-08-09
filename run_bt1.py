from src.experiment.experiment_utils import ExperimentUtils as eu

# possible alternative experiment: intervene on s
#   type 1) linear, O(n)
#   X <-> V1 <-> V2 <-> ... <-> Z
#   type 2) star-shaped, O(2^n) V1 <-> X, V2 <-> X, ... Z <-> X

def testBT1(numGraphs, n, m, bidirectedEdgesFraction=0):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollection.append([])

        G = eu.constructBidirGraph(n, int(mMax * bidirectedEdgesFraction))
        params = eu.measureParams(G)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testBT1Batch(numGraphs, n, numDivisions=10):
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            bidirectedEdgesFraction = j * 0.1
            G = eu.constructBidirGraph(n, int(mMax * bidirectedEdgesFraction))
            params = eu.measureParams(G)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


if __name__ == '__main__':
    numGraphs = 5
    numDivisions = 10
    n = 20
    m = int(n * 1.5)

    testBT1Batch(numGraphs, n, numDivisions)
    # testBT1(numGraphs, n, 0.2)
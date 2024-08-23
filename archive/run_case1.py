from src.experiment.experiment_utils import ExperimentUtils as eu

fileName = 'case1_report'

def testCase1(numBatches, n, pb=0, randomSeed=0):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numBatches):
        # paramsCollectionText.append([])
        paramsBatchTextBlocks = []
        paramsPerBatch = []
        mb = int(mMax * pb)

        G = eu.constructBidirGraph(n, mb, randomSeed)
        params = eu.runAlgorithmAndMeasureParams(G)

        paramsToStr = list(map(lambda n: str(n), params))
        paramsBatchTextBlocks.extend(paramsToStr)
        paramsPerBatch.append(params)

        paramsCollectionText.append(paramsBatchTextBlocks)
        paramsCollection.append(paramsPerBatch)

    for paramsBatchTextBlocks in paramsCollectionText:
        print(' '.join(paramsBatchTextBlocks))

    # eu.writeParamsToCsv(fileName, paramsCollection)


def testCase1Batch(numBatches, n, numDivisions=10, randomSeed=0):
    paramsCollectionText = []
    paramsCollection = []

    mMax = int(0.5 * n * (n-1))

    for i in range(numBatches):
        # paramsCollectionText.append([])
        paramsBatchTextBlocks = []
        paramsPerBatch = []

        line = 'Running a batch of samples [' + str(i * 10 + 1) + ', ' + str((i+1) * numDivisions) + ']'
        print(line)

        for j in range(numDivisions):
            pb = j * 0.1
            mb = int(mMax * pb)

            G = eu.constructBidirGraph(n, mb, randomSeed)
            params = eu.runAlgorithmAndMeasureParams(G)

            paramsToStr = list(map(lambda n: str(n), params))
            # paramsCollectionText[i].extend(paramsToStr)
            paramsBatchTextBlocks.extend(paramsToStr)

            paramsPerBatch.append(params)

        paramsCollectionText.append(paramsBatchTextBlocks)
        paramsCollection.append(paramsPerBatch)

    for paramsBatchTextBlocks in paramsCollectionText:
        print(' '.join(paramsBatchTextBlocks))

    # eu.writeParamsToCsv(fileName, paramsCollection)


if __name__ == '__main__':
    randomSeed = 0
    numBatches = 1
    numDivisions = 2
    n = 10
    U = 0.2

    testCase1Batch(numBatches, n, numDivisions, randomSeed)
    # testCase1(numBatches, n, U, randomSeed)
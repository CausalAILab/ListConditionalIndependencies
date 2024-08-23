# from src.experiment.experiment_utils import ExperimentUtils as eu

# fileName = 'case2_report'

# def testCase2(numBatches, n, pb=0.2, randomSeed=0):
#     paramsCollectionText = []
#     paramsCollection = []

#     mMax = int(n * (n-1) * 0.5)
#     md = n
#     mb = int(mMax * pb)
    
#     for i in range(numBatches):
#         paramsCollectionText.append([])
#         paramsCollectionPerSample = []

#         G = eu.constructMixedGraph(n, md, mb, randomSeed)
#         params = eu.runAlgorithmAndMeasureParams(G)
#         paramsToStr = list(map(lambda n: str(n), params))
#         paramsCollectionText[i].extend(paramsToStr)

#         paramsCollectionPerSample.append(params)
#         paramsCollection.append(paramsCollectionPerSample)

#     for paramsBatchTextBlocks in paramsCollectionText:
#         print(' '.join(paramsBatchTextBlocks))

#     # eu.writeParamsToCsv(fileName, paramsCollection)


# def testCase2Batch(numBatches, n, numDivisions=10, randomSeed=0):
#     paramsCollectionText = []
#     paramsCollection = []

#     mMax = int(n * (n-1) * 0.5)
#     md = n

#     for i in range(numBatches):
#         # paramsCollectionText.append([])
#         paramsBatchTextBlocks = []
#         paramsPerBatch = []

#         line = 'Running a batch of samples [' + str(i * 10 + 1) + ', ' + str((i+1) * numDivisions) + ']'
#         print(line)

#         for j in range(numDivisions):
#             pb = j * 0.1
#             mb = int(mMax * pb)

#             G = eu.constructMixedGraph(n, md, mb, randomSeed)
#             params = eu.runAlgorithmAndMeasureParams(G)
            
#             paramsToStr = list(map(lambda n: str(n), params))
#             # paramsCollectionText[i].extend(paramsToStr)
#             paramsBatchTextBlocks.extend(paramsToStr)

#             paramsPerBatch.append(params)

#         paramsCollectionText.append(paramsBatchTextBlocks)
#         paramsCollection.append(paramsPerBatch)

#     for paramsBatchTextBlocks in paramsCollectionText:
#         print(' '.join(paramsBatchTextBlocks))

#     # eu.writeParamsToCsv(fileName, paramsCollection)


# if __name__ == '__main__':
#     randomSeed = 0
#     numBatches = 10
#     numDivisions = 10
#     n = 10
#     U = 0.2

#     # testCase2Batch(numBatches, n, numDivisions, randomSeed)
#     testCase2(numBatches, n, U, randomSeed)
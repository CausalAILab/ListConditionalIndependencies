import sys

from src.testable_implications.ci_defs import algListCI, algListCIBF
from src.experiment.experiment_utils import ExperimentUtils as eu

fileName = 'report_case_'

def runCaseX(experimentType, specs):
    n = specs['n']
    U = specs['U']
    numBatches = specs['numBatches']
    randomSeed = specs['randomSeed']
    writeToCsv = specs['writeToCsv']

    paramsCollectionText = []
    paramsCollection = []

    for i in range(numBatches):
        paramsBatchText = []
        paramsBatch = []

        (md, mb) = getEdgeSpecs(experimentType, specs, U)

        G = eu.constructRandomGraph(n, md, mb, randomSeed)

        if experimentType == '1v':
            params = eu.runAlgorithmAndMeasureParams(G, algListCIBF.id_, specs)
        else:
            params = eu.runAlgorithmAndMeasureParams(G, algListCI.id_, specs)

        paramsToStr = list(map(lambda n: str(n), params))

        paramsBatchText.extend(paramsToStr)
        paramsCollectionText.append(paramsBatchText)

        paramsBatch.append(params)
        paramsCollection.append(paramsBatch)

    if writeToCsv:
        eu.writeParamsToCsv(fileName + experimentType,paramsCollection)
    else:
        for paramsBatchTextBlocks in paramsCollectionText:
            print(' '.join(paramsBatchTextBlocks))


def runCaseXBatch(experimentType, specs):
    n = specs['n']
    numBatches = specs['numBatches']
    numDivisions = specs['numDivisions']
    interval = specs['interval']
    randomSeed = specs['randomSeed']
    writeToCsv = specs['writeToCsv']

    paramsCollectionText = []
    paramsCollection = []

    for i in range(numBatches):
        paramsBatchText = []
        paramsBatch = []

        line = 'Running a batch of samples [' + str(i * numDivisions + 1) + ', ' + str((i+1) * numDivisions) + ']'
        print(line)

        for div in range(numDivisions):
            U = div * interval

            (md, mb) = getEdgeSpecs(experimentType, specs, U)

            G = eu.constructRandomGraph(n, md, mb, randomSeed)

            if experimentType == '1v':
                params = eu.runAlgorithmAndMeasureParams(G, algListCIBF.id_, specs)
            else:
                params = eu.runAlgorithmAndMeasureParams(G, algListCI.id_, specs)

            paramsToStr = list(map(lambda n: str(n), params))
            
            paramsBatchText.extend(paramsToStr)
            paramsBatch.append(params)

        paramsCollectionText.append(paramsBatchText)
        paramsCollection.append(paramsBatch)
    
    if writeToCsv:
        eu.writeParamsToCsv(fileName + experimentType, paramsCollection)
    else:
        for paramsBatchTextBlocks in paramsCollectionText:
            print(' '.join(paramsBatchTextBlocks))


def getEdgeSpecs(experimentType, specs, U):
    n = specs['n']

    mMax = int(0.5 * n * (n-1))

    if experimentType == '1a':
        md = 0
        mb = int(mMax * U)
    elif experimentType == '1b':
        md = 0
        # mb = int(n * U)
        mb = int(50 * U)
    elif experimentType == '1r':
        md = 0
        mb = int(mMax * (1.0 - U))
    elif experimentType == '1v':
        md = 0
        mb = int(mMax * U)
    elif experimentType == '2a':
        md = n
        mb = int(mMax * U)
    elif experimentType == '2b':
        md = n
        # mb = int(n * U)
        mb = int(50 * U)
    elif experimentType == '3a':
        md = n * 2
        mb = int(mMax * U)
    elif experimentType == '4a':
        md = n * 3
        mb = int(mMax * U)
    
    return (md, mb)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please specify the experiment type correctly (i.e., \'1a\').')

        sys.exit()

    experimentType = sys.argv[1]
    supportedExpTypes = ['1a', '1b', '1v', '1r', '2a', '2b', '3a', '4a']

    if experimentType not in supportedExpTypes:
        print('Please specify a correct expriment type (e.g., \'1a\').')
        sys.exit()

    specs = {
        'n': 10,
        'U': 0.1,
        'numBatches': 10,
        'numDivisions': 11,
        'interval': 0.1,
        # 'randomSeed': 0,
        'randomSeed': None,
        'timeout': 1 * 60 * 60,
        # 'timeout': None,
        'Vordered': None,
        # 'writeToCsv': False
        'writeToCsv': True
    }

    runAllDivisions = 1

    if runAllDivisions:
        runCaseXBatch(experimentType, specs)
    else:
        runCaseX(experimentType, specs)
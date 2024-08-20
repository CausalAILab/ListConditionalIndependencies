import sys
import os
import multiprocessing as mp
from datetime import datetime

from src.testable_implications.ci_defs import algMap, algListGMP, algListCIBF, algListCI
from src.graph.classes.graph_defs import latentNodeType, directedEdgeType, bidirectedEdgeType
from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import GraphUtils as gu
from src.editor.sections.edges_section import EdgesSection
from src.editor.sections.nodes_section import NodesSection
from src.editor.classes.bidirected_options_parser import BidirectedOptionsParser
from src.editor.classes.latent_options_parser import LatentOptionsParser
from src.editor.input_parser import InputParser
from src.testable_implications.conditional_independencies import ConditionalIndependencies as cu
from src.experiment.experiment_utils import ExperimentUtils as eu

defaultTimeout = 60

ranges = range(0,10,1)
defaultLatentFranctionsToTest = list(map(lambda x: x/10.0, ranges))

numSampleOfFailure = 0
latentFractionOfFailure = 0

reportFileName = 'bnlearn_report'
fileName = ''

def parseGraph(fileContent):
    parsedData = parseInput(fileContent)

    if parsedData is None:
        return None

    return parsedData['graph']


def parseInput(fileContent):
    parser = InputParser()
    parser.sections = [getNodesSection(), getEdgesSection()]

    parsedData = parser.parse(fileContent)

    return parsedData


def getNodesSection():
    nodeTypeParsers = {}
    nodeTypeParsers[latentNodeType.id_] = LatentOptionsParser()

    return NodesSection(nodeTypeParsers)


def getEdgesSection():
    edgeTypeParsers = {}
    edgeTypeParsers[bidirectedEdgeType.id_] = BidirectedOptionsParser()

    return EdgesSection(edgeTypeParsers)


# an internal function to organize and finalize measured parameters
def getFullParams(G, alg, CI, runtime, listCIBFParams):
    n = len(G.nodes)
    m = len(G.edges)
    md = len(list(filter(lambda e: e['type_'] == directedEdgeType.id_, G.edges)))
    mb = len(list(filter(lambda e: e['type_'] == bidirectedEdgeType.id_, G.edges)))
    CIsize = len(CI)

    s = 1

    if alg == algListCIBF.id_:
        Snum = listCIBFParams['Snum']
        Splusnum = listCIBFParams['Splusnum']
        s = listCIBFParams['s']
    elif alg == algListCI.id_:
        V = su.intersection(gu.topoSort(G), G.nodes, 'name')
        ACsizes = []

        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)
            
            R = cu.C(GVleqX,X)
            ACsizes.append(len(R))

        if len(ACsizes) > 0:
            s = max(ACsizes)

    params = []

    if alg == algListGMP.id_:
        params = [n, m, md, mb, CIsize, runtime]
    elif alg == algListCIBF.id_:
        params = [n, m, md, mb, CIsize, runtime, s, Snum, Splusnum]
    elif alg == algListCI.id_:
        params = [n, m, md, mb, CIsize, runtime, s]

    return params


def runAlgorithm(queue, G, alg):
    CI = queue.get()
    listCIBFParams = queue.get()

    if alg == algListGMP.id_:
        CIs = cu.ListGMP(G, G.nodes)
    elif alg == algListCIBF.id_:
        CIs = cu.ListCIBF(G, G.nodes, True, None, listCIBFParams)
    elif alg == algListCI.id_:
        CIs = cu.ListCI(G, G.nodes)

    CI.extend(CIs)

    queue.put(CI)
    queue.put(listCIBFParams)


# returns a pair: (status of sucessful run, measured params)
def tryRunAlgorithm(G, alg, timeout=defaultTimeout):
    CI = []
    listCIBFParams = {}

    # use queue to pass values between processes
    queue = mp.Queue()
    queue.put(CI)
    queue.put(listCIBFParams)
    p = mp.Process(target=runAlgorithm, args=(queue, G, alg))

    start = datetime.now()
    p.start()
    p.join(timeout=timeout)

    if p.is_alive():
        p.terminate()
        p.join()

        return (False, None)
    
    end = datetime.now()

    CI = queue.get()
    listCIBFParams = queue.get()
    runtime = end - start

    params = getFullParams(G, alg, CI, runtime, listCIBFParams)

    return (True, params)


def runAlgorithmAndMeasureParams(G, alg, timeout=defaultTimeout):
    CI = []
    listCIBFParams = {}

    # use queue to pass values between processes
    queue = mp.Queue()
    queue.put(CI)
    queue.put(listCIBFParams)
    p = mp.Process(target=runAlgorithm, args=(queue, G, alg))

    start = datetime.now()
    p.start()
    p.join(timeout=timeout)

    if p.is_alive():
        p.terminate()
        p.join()

        currentAlg = algMap[alg]
        paramNames = currentAlg.params
        params = ['-'] * len(paramNames)

        return params
    
    end = datetime.now()

    CI = queue.get()
    listCIBFParams = queue.get()
    runtime = eu.roundToNearestSecond(end - start)

    params = getFullParams(G, alg, CI, runtime, listCIBFParams)

    return params


def testProjectedGraphs(G, alg, numBatches, latentFraction=0.3, timeout=defaultTimeout):
    paramsCollection = []

    for i in range(numBatches):
        paramsCollection.append([])

        Gp = eu.applyProjection(G, latentFraction)
        params = runAlgorithmAndMeasureParams(Gp, alg, timeout)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testProjectedGraphsBatch(G, alg, numBatches, timeout=defaultTimeout):
    paramsCollectionText = []
    paramsCollection = []

    numDivisions = 10
    offset = 0

    for i in range(numBatches):
        paramsCollectionText.append([])
        paramsCollectionPerSample = []

        line = 'Running a batch of samples [' + str(i * 10 + 1) + ', ' + str((i+1) * 10) + ']'
        print(line)

        for j in range(numDivisions):
            latentFraction = j * 0.1 + offset
            Gp = eu.applyProjection(G, latentFraction)
            params = runAlgorithmAndMeasureParams(Gp, alg, timeout)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollectionText[i].extend(paramsToStr)

            paramsCollectionPerSample.append(params)

        paramsCollection.append(paramsCollectionPerSample)

    # for line in paramsCollectionText:
    #     print(' '.join(line))

    global fileName

    suffix = ''

    if alg == algListGMP.id_:
        suffix = 'gmp'
    elif alg == algListCIBF.id_:
        suffix = 'lmp'
    elif alg == algListCI.id_:
        suffix = 'clmp'

    fullFileName = reportFileName + '_' + fileName.replace('.txt', '') + '_' + suffix

    eu.writeParamsToCsv(fullFileName, paramsCollection)


def tryTestProjectedGraphs(G, alg, numBatches, latentFractionsToTest=defaultLatentFranctionsToTest, timeout=defaultTimeout):
    paramsCollection = []

    global numSampleOfFailure
    numSampleOfFailure = 1

    for i in range(numBatches):
        paramsCollection.append([])

        for U in latentFractionsToTest:
            Gp = eu.applyProjection(G, U)
            (successfullyRun, params) = tryRunAlgorithm(Gp, alg, timeout)

            if not successfullyRun:
                global latentFractionOfFailure
                latentFractionOfFailure = U

                return False

            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

        numSampleOfFailure = numSampleOfFailure + 1

    for line in paramsCollection:
        print(' '.join(line))

    return True

if __name__ == '__main__':

    # read arguments
    if len(sys.argv) != 3:
        print('Please specify 2 arguments: 1) the name of the task (\'gmp\', \'lmp\', or \'clmp\'), and 2) input file path (e.g., graphs/bif/sm/cancer.txt).')

        sys.exit()

    task = sys.argv[1]
    filePath = sys.argv[2]

    numBatches = 10
    # UsToTest = [0.1]

    timeout = 1 * 60 * 60
    # timeout = None

    validTasks = ['gmp', 'lmp', 'clmp']

    if task not in validTasks:
        print('Please specify a valid task to run (\'gmp\', \'lmp\', or \'clmp\').')
    else:
        if task == 'gmp':
            algorithm = algListGMP.id_
        elif task == 'lmp':
            algorithm = algListCIBF.id_
        elif task == 'clmp':
            algorithm = algListCI.id_

        try:
            filePath = os.path.normpath(filePath)
            path, file = os.path.split(filePath)

            fileName = file

            with open(filePath, 'r') as f:
                fileContent = f.read()
                G = parseGraph(fileContent)

                if G is not None:
                    testProjectedGraphsBatch(G, algorithm, numBatches, timeout)
                    # testProjectedGraphs(G, algorithm, numBatches, 0.4, timeout)

                    # if not tryTestProjectedGraphs(G, algorithm, numBatches, UsToTest, timeout):
                    #     currentAlg = algMap[algorithm]
                    #     line = currentAlg.name + ' timed out with U: ' + str(latentFractionOfFailure) + ' on sample ' + str(numSampleOfFailure) + '.'
                    #     print(line)

                f.close()
        except IOError:
            line = 'Please specify the input file correctly.'

            print(line)
    
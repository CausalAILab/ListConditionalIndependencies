import sys
import random
import multiprocessing as mp
from datetime import datetime

from src.testable_implications.ci_defs import algMap, algListGMP, algListCIBF, algListCI
from src.graph.classes.graph_defs import latentNodeType, directedEdgeType, bidirectedEdgeType
from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import GraphUtils as gu
from src.projection.projection_utils import ProjectionUtils as pu
from src.editor.sections.edges_section import EdgesSection
from src.editor.sections.nodes_section import NodesSection
from src.editor.classes.bidirected_options_parser import BidirectedOptionsParser
from src.editor.classes.latent_options_parser import LatentOptionsParser
from src.editor.input_parser import InputParser
from src.testable_implications.conditional_independencies import ConditionalIndependencies


defaultTimeout = 60


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


def applyProjection(G, latentFraction=0.3):
    if latentFraction == 0:
        return G
    
    nodes = G.nodes
    edges = G.edges

    # sample x% of nodes and turn those to latent
    k = int(len(nodes) * latentFraction)
    indices = random.sample(range(len(nodes)), k)

    V = []
    Obs = []

    for i in range(len(nodes)):
        node = nodes[i]

        if i in indices:
            node['type_'] = latentNodeType.id_
        else:
            Obs.append(node)

        V.append(node)
    
    Gp = G.copy()
    Gp.nodes = V
    Gp.edges = edges
    Gp = pu.projectOver(Gp,Obs)

    return Gp


def runAlgorithm(queue, G, alg):
    CI = queue.get()
    measuredParams = queue.get()

    if alg == algListGMP.id_:
        CIs = ConditionalIndependencies.ListGMP(G, G.nodes)
    elif alg == algListCIBF.id_:
        CIs = ConditionalIndependencies.ListCIBF(G, G.nodes, True, None, measuredParams)
    elif alg == algListCI.id_:
        CIs = ConditionalIndependencies.ListCI(G, G.nodes)

    CI.extend(CIs)

    queue.put(CI)
    queue.put(measuredParams)


def measureParams(G, alg, timeout=defaultTimeout):
    CI = []
    measuredParams = {}

    # use queue to pass values between processes
    queue = mp.Queue()
    queue.put(CI)
    queue.put(measuredParams)
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
    measuredParams = queue.get()

    # get parameters
    n = len(G.nodes)
    m = len(G.edges)
    md = len(list(filter(lambda e: e['type_'] == directedEdgeType.id_, G.edges)))
    mb = len(list(filter(lambda e: e['type_'] == bidirectedEdgeType.id_, G.edges)))
    CIsize = len(CI)
    runtime = end - start

    s = 1

    if alg == algListCIBF.id_:
        Snum = measuredParams['Snum']
        Splusnum = measuredParams['Splusnum']
        s = measuredParams['s']
    elif alg == algListCI.id_:
        V = su.intersection(gu.topoSort(G), G.nodes, 'name')
        ACsizes = []

        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)
            
            R = ConditionalIndependencies.C(GVleqX,X)
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


def testProjectedGraphs(G, alg, numGraphs, latentFraction=0.3, timeout=defaultTimeout):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        Gp = applyProjection(G, latentFraction)
        params = measureParams(Gp, alg, timeout)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))


def testProjectedGraphsBatch(G, alg, numGraphs, timeout=defaultTimeout):
    paramsCollection = []

    numDivisions = 10
    offset = 0

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            latentFraction = j * 0.1 + offset
            Gp = applyProjection(G, latentFraction)
            params = measureParams(Gp, alg, timeout)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))

if __name__ == '__main__':

    # read arguments
    if len(sys.argv) != 2:
        print('Please specify input file path correctly (e.g., graphs/bif/sm/cancer.txt).')

        sys.exit()

    filePath = sys.argv[1]

    # algorithm = algListGMP.id_
    # algorithm = algListCIBF.id_
    algorithm = algListCI.id_

    numGraphs = 10

    # 2 hours
    timeout = 2 * 60 * 60

    try:
        with open(filePath, 'r') as f:
            fileContent = f.read()
            G = parseGraph(fileContent)

            if G is not None:
                testProjectedGraphsBatch(G, algorithm, numGraphs, timeout)
                # testProjectedGraphs(G, algorithm, numGraphs, 0.2, timeout)

            f.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)
    
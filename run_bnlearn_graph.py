import sys
import random
from datetime import datetime

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
from src.adjustment.adjustment_sets_utils import writeNodeNames


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


def measureParams(alg, G):
    measuredParams = {}
    s = 1

    start = datetime.now()

    if alg == 'gmp':
        CI = ConditionalIndependencies.ListGMP(G, G.nodes)
        end = datetime.now()
    elif alg == 'lmp':
        CI = ConditionalIndependencies.ListCIBF(G, G.nodes, True, None, measuredParams)
        end = datetime.now()

        Snum = measuredParams['Snum']
        Splusnum = measuredParams['Splusnum']
        s = measuredParams['s']
    elif alg == 'listci':
        CI = ConditionalIndependencies.ListCI(G, G.nodes)
        end = datetime.now()

        V = su.intersection(gu.topoSort(G), G.nodes, 'name')
        ACsizes = []

        for X in V:
            VleqX = V[:V.index(X)+1]
            GVleqX = gu.subgraph(G, VleqX)
            
            R = ConditionalIndependencies.C(GVleqX,X)
            ACsizes.append(len(R))

        if len(ACsizes) > 0:
            s = max(ACsizes)

    # get parameters
    n = len(G.nodes)
    m = len(G.edges)
    md = len(list(filter(lambda e: e['type_'] == directedEdgeType.id_, G.edges)))
    mb = len(list(filter(lambda e: e['type_'] == bidirectedEdgeType.id_, G.edges)))
    CIsize = len(CI)
    runtime = end - start

    params = []

    if alg == 'gmp':
        params = [n, m, md, mb, CIsize, runtime]
    elif alg == 'lmp':
        params = [n, m, md, mb, CIsize, runtime, s, Snum, Splusnum]
    elif alg == 'listci':
        params = [n, m, md, mb, CIsize, runtime, s]

    return params


def testProjectedGraphs(alg, G, numGraphs, latentFraction=0.3):
    paramsCollection = []

    for i in range(numGraphs):
        paramsCollection.append([])

        Gp = applyProjection(G, latentFraction)
        params = measureParams(alg, Gp)
        paramsToStr = list(map(lambda n: str(n), params))
        paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))

def testProjectedGraphsBatch(alg, G, numGraphs):
    paramsCollection = []

    numDivisions = 10

    for i in range(numGraphs):
        paramsCollection.append([])

        for j in range(numDivisions):
            latentFraction = j * 0.1
            Gp = applyProjection(G, latentFraction)
            params = measureParams(alg, Gp)
            paramsToStr = list(map(lambda n: str(n), params))
            paramsCollection[i].extend(paramsToStr)

    for line in paramsCollection:
        print(' '.join(line))

if __name__ == '__main__':

    # read arguments
    if len(sys.argv) != 2:
        print('Please specify input file path (e.g., graphs/bif/sm/cancer.txt).')

        sys.exit()

    filePath = sys.argv[1]

    # algorithm = 'gmp'
    # algorithm = 'lmp'
    algorithm = 'listci'

    numGraphs = 10

    try:
        with open(filePath, 'r') as f:
            fileContent = f.read()
            G = parseGraph(fileContent)

            if G is not None:
                testProjectedGraphsBatch(algorithm, G, numGraphs)
                # testProjectedGraphs(algorithm, G, numGraphs, 0.4)

            f.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)
    
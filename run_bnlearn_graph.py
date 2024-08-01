import sys
import random
from datetime import datetime

from src.graph.classes.graph_defs import latentNodeType, bidirectedEdgeType
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

def testProjectedGraphs(alg, G, numGraphs, latentFraction=None):
    CIs = []
    runtimes = []

    line = ''

    for i in range(numGraphs):
        nodes = G.nodes
        edges = G.edges

        # sample x% of nodes and turn those to latent
        if latentFraction is not None:
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
        else:
            V = nodes
        
        G.nodes = V
        G.edges = edges
        G = pu.projectOver(G,Obs)

        s = 1

        start = datetime.now()

        if alg == 'gmp':
            CI = ConditionalIndependencies.ListGMP(G, G.nodes)
            end = datetime.now()
        elif alg == 'lmp':
            CI = ConditionalIndependencies.ListCIBF(G, G.nodes, True)
            end = datetime.now()
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

        CIs.append(CI)
        runtimes.append(end - start)

        line = str(s) + ' ' + str(len(CI)) + ' ' + str(end - start)
        print(line)


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

if __name__ == '__main__':

    # read arguments
    if len(sys.argv) != 2:
        print('Please specify input file path (e.g., graphs/paper/fig5a.txt).')

        sys.exit()

    filePath = sys.argv[1]

    # algorithms = ['lmp', 'listci']
    # algorithms = ['lmp']
    algorithms = ['listci']

    numGraphs = 10
    numDivisions = 10

    try:
        with open(filePath, 'r') as f:
            fileContent = f.read()
            G = parseGraph(fileContent)

            if G is not None:
                for alg in algorithms:
                    for k in range(numDivisions):
                        latentFraction = k * 0.1
                        testProjectedGraphs(alg, G, numGraphs, latentFraction)

                    # testProjectedGraphs(alg, G, numGraphs, 0.4)

            f.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)
    
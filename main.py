import sys

from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import GraphUtils as gu
from src.editor.sections.edges_section import EdgesSection
from src.editor.sections.nodes_section import NodesSection
from src.editor.classes.bidirected_options_parser import BidirectedOptionsParser
from src.editor.classes.latent_options_parser import LatentOptionsParser
from src.editor.input_parser import InputParser
from src.testable_implications.conditional_independencies import ConditionalIndependencies
from src.adjustment.adjustment_sets_utils import writeNodeNames
from src.graph.classes.graph_defs import latentNodeType, bidirectedEdgeType

def outputCIs(fileContent, task):
    parsedData = parseInput(fileContent)

    if parsedData is None:
        return

    G = parsedData['graph']
    CI = []

    Vordered = None
    namesInOrder = None

    # hack to force certain topo order, making results consistent
    # fig1b
    # namesInOrder = ['A', 'D', 'B', 'C', 'E', 'F', 'H', 'J']
    # fig3a
    # namesInOrder = ['A3', 'A2', 'A1', 'B1', 'B3', 'B2']
    # fig3b
    # namesInOrder = ['A3', 'A1', 'A4', 'A2', 'B3', 'B1', 'B4', 'B2']
    # fig3c
    # namesInOrder = ['A2', 'A4', 'A1', 'A_n', 'A3', 'B_n', 'B3', 'B4', 'B2', 'B1']
    # fig5a
    # namesInOrder = ['A','B','C','D','E','F','H','J']
    # noci2
    # namesInOrder = ['P', 'A', 'B', 'C', 'D', 'H']
    # list2
    # namesInOrder = ['A','B','C','D','E','F','H','J']
    # id72
    namesInOrder = ['C', 'A', 'D', 'Z', 'B', 'X', 'Y', 'E']

    if namesInOrder is not None:
        Vordered = []

        for name in namesInOrder:
            Vs = list(filter(lambda n: n['name'] == name, G.nodes))
            Vordered.append(Vs[0])

    if task == 'gmp':
        CI = ConditionalIndependencies.GMP(G, G.nodes)
    elif task == 'lmp':
        CI = ConditionalIndependencies.LMP(G, G.nodes, True, Vordered)
    elif task == 'lmpp':
        CI = ConditionalIndependencies.LMPplus(G, G.nodes)
    elif task == 'listci':
        CI = ConditionalIndependencies.ListCI(G, G.nodes, Vordered)

    if CI is None or len(CI) == 0:
        print('No conditional independence is implied.')
    else:
        for ci in CI:
            if task == 'gmp':
                X = ci['X']
                Y = ci['Y']
                Z = ci['Z']
            elif task == 'lmp' or task == 'lmpp' or task == 'listci':
                X = [ci['X']]
                Y = ci['W']
                Z = ci['Z']

            Xnames = sorted(list(map(lambda n: n['name'], X)))
            Ynames = sorted(list(map(lambda n: n['name'], Y)))
            Znames = sorted(list(map(lambda n: n['name'], Z)))

            print(writeNodeNames(Xnames) + ' \indep ' + writeNodeNames(Ynames) + ' | ' + writeNodeNames(Znames))

        print('Conditional independencies (' + str(len(CI)) + ') in total.')


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
    if len(sys.argv) != 3:
        print('Please specify 2 arguments: 1) the name of the task (e.g., \'gmp\' or \'lmp\'), and 2) input file path (e.g., graphs/list1.txt).')

        sys.exit()

    task = sys.argv[1]
    filePath = sys.argv[2]

    validTasks = ['gmp', 'lmp', 'lmpp', 'listci']

    try:
        with open(filePath, 'r') as f:
            fileContent = f.read()

            if task in validTasks:
                outputCIs(fileContent, task)
            else:
                print('Please specify a valid task to run (e.g., \'gmp\', \'lmp\', or \'lmpp\').')

            f.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)

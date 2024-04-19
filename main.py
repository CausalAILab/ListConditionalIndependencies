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

def GMP(fileContent):
    parsedData = parseInput(fileContent)

    if parsedData is None:
        return

    G = parsedData['graph']

    CI = ConditionalIndependencies.GMP(G, G.nodes)

    if CI is None or len(CI) == 0:
        print('No conditional independence is implied.')
    else:
        for ci in CI:
            X = ci['X']
            Y = ci['Y']
            Z = ci['Z']

            Xnames = sorted(list(map(lambda n: n['name'], X)))
            Ynames = sorted(list(map(lambda n: n['name'], Y)))
            Znames = sorted(list(map(lambda n: n['name'], Z)))

            print(writeNodeNames(Xnames) + ' \indep ' + writeNodeNames(Ynames) + ' | ' + writeNodeNames(Znames))

        print('Conditional independencies (' + str(len(CI)) + ') in total):')


def LMP(fileContent):
    parsedData = parseInput(fileContent)

    if parsedData is None:
        return

    G = parsedData['graph']

    CI = ConditionalIndependencies.LMP(G, G.nodes)

    if CI is None or len(CI) == 0:
        print('No conditional independence is implied.')
    else:
        for ci in CI:
            u = ci['u']
            W = ci['W']
            Z = ci['Z']

            Wnames = sorted(list(map(lambda n: n['name'], W)))
            Znames = sorted(list(map(lambda n: n['name'], Z)))

            print(u['name'] + ' \indep ' + writeNodeNames(Wnames) + ' | ' + writeNodeNames(Znames))

        print('Conditional independencies (' + str(len(CI)) + ') in total):')


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

    try:
        with open(filePath, 'r') as f:
            fileContent = f.read()

            # decide which feature to run
            if task == 'gmp':
                GMP(fileContent)
            elif task == 'lmp':
                LMP(fileContent)
            else:
                print('Please specify a valid task to run (e.g., \'gmp\' or \'lmp\').')

            f.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)

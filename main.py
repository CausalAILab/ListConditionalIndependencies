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


def ListCIBF(fileContent):
    parsedData = parseInput(fileContent)

    if parsedData is None:
        return

    G = parsedData['graph']

    CI = ConditionalIndependencies.ListCIBF(G, G.nodes)

    if CI is None or len(CI) == 0:
        print('No conditional independence is implied.')
    else:
        print('Conditional independencies:')

        for ci in CI:
            u = ci['u']
            W = ci['W']
            Z = ci['Z']

            Wnames = sorted(list(map(lambda n: n['name'], W)))
            Znames = sorted(list(map(lambda n: n['name'], Z)))

            print(u['name'] + ' \indep ' + writeNodeNames(Wnames) + ' | ' + writeNodeNames(Znames))


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
        # print('Please specify 2 arguments: 1) the name of the task (e.g., \'find\' or \'list\'), and 2) input file path (e.g., graphs/canonical.txt).')
        print('Please specify 1 argument: input file path (e.g., graphs/list1.txt).')

        sys.exit()

    # task = sys.argv[1]
    # filePath = sys.argv[2]
    filePath = sys.argv[1]

    try:
        with open(filePath, 'r') as f:
            fileContent = f.read()

            ListCIBF(fileContent)

            # # decide which feature to run
            # if task == 'find':
            #     FindFDSet(fileContent)
            # elif task == 'list':
            #     ListFDSets(fileContent)
            # else:
            #     print('Please specify a valid task to run (e.g., \'find\' or \'list\').')

            f.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)

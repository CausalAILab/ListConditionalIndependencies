import sys
import csv

import numpy as np
from causallearn.utils.cit import CIT

# from src.graph.classes.graph import Graph
# from src.inference.utils.set_utils import SetUtils as su
# from src.inference.utils.graph_utils import GraphUtils as gu
from src.editor.sections.edges_section import EdgesSection
from src.editor.sections.nodes_section import NodesSection
from src.editor.classes.bidirected_options_parser import BidirectedOptionsParser
from src.editor.classes.latent_options_parser import LatentOptionsParser
from src.editor.input_parser import InputParser
from src.testable_implications.conditional_independencies import ConditionalIndependencies
from src.adjustment.adjustment_sets_utils import writeNodeNames
from src.graph.classes.graph_defs import latentNodeType, bidirectedEdgeType

def parseGraph(fileContent):
    parsedData = parseInput(fileContent)

    if parsedData is None:
        return None

    return parsedData['graph']

def parseDataset(G, lines):
    header = []
    dataPoints = []

    for i in range(len(lines)):
        line = lines[i]

        if i == 0:
            header = line
            continue
        
        # convert string (of numbers) to floats
        parsedLine = list(map(lambda x: float(x), line))

        dataPoints.append(parsedLine)
    
    dataset = np.array(dataPoints)

    # remove columns not present in graph nodes
    nodeNames = list(map(lambda n: n['name'], G.nodes))
    columsToRemove = list(map(lambda name: name not in nodeNames, header))
    
    # 3rd arg: 0 means rows, 1 means columns
    dataset = np.delete(dataset, columsToRemove, 1)
    header = list(filter(lambda name: name in nodeNames, header))

    parsedDataset = {
        'header': header,
        'dataset': dataset
    }

    return parsedDataset

def testModel(G, Pv, pValue, outputCIs = False):
    CIs = ConditionalIndependencies.ListCI(G, G.nodes)

    # tests: 'fisherz', 'kci'
    # https://github.com/py-why/causal-learn/blob/main/causallearn/utils/cit.py
    # https://causal-learn.readthedocs.io/en/latest/independence_tests_index/kci.html
    # CITestMethod = 'fisherz'
    CITestMethod = 'kci'
    CITester = CIT(Pv['dataset'], CITestMethod)
    violatedCIs = []

    nodeNames = Pv['header']

    for CI in CIs:
        X = [CI['X']]
        Y = CI['W']
        Z = CI['Z']

        # get indices of X,Y,Z from headers
        xNames = list(map(lambda n: n['name'], X))
        yNames = list(map(lambda n: n['name'], Y))
        zNames = list(map(lambda n: n['name'], Z))

        xIndices = list(map(lambda n: nodeNames.index(n), xNames))
        yIndices = list(map(lambda n: nodeNames.index(n), yNames))
        zIndices = list(map(lambda n: nodeNames.index(n), zNames))

        p = CITester(xIndices, yIndices, zIndices)

        if p >= pValue:
            violatedCIs.append(CI)
        
        printCI(CI)
        print(p)

    line = 'CIs total: ' + str(len(CIs))
    print(line)

    line = 'CIs violated: ' + str(len(violatedCIs))
    print(line)

    if outputCIs:
        printCIs(CIs)
    
def printCIs(CIs):
    if CIs is None or len(CIs) == 0:
        print('No conditional independence is implied.')
    else:
        for CI in CIs:
            printCI(CI)

        print('Conditional independencies (' + str(len(CIs)) + ') in total.')

def printCI(CI):
    X = [CI['X']]
    Y = CI['W']
    Z = CI['Z']

    Xnames = sorted(list(map(lambda n: n['name'], X)))
    Ynames = sorted(list(map(lambda n: n['name'], Y)))
    Znames = sorted(list(map(lambda n: n['name'], Z)))

    print(writeNodeNames(Xnames) + ' \indep ' + writeNodeNames(Ynames) + ' | ' + writeNodeNames(Znames))


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
        print('Please specify the graph file path (e.g., graphs/list1.txt), followed by the path for dataset.')

        sys.exit()

    graphFilePath = sys.argv[1]
    datasetFilePath = sys.argv[2]

    pValue = 0.05

    try:
        with open(graphFilePath, 'r') as fg:
            fileContent = fg.read()
            G = parseGraph(fileContent)

            with open(datasetFilePath, 'r') as fd:
                r = csv.reader(fd)
                lines = list(r)
                Pv = parseDataset(G, lines)

                if G is not None:
                    testModel(G, Pv, pValue)
                    # testModel(G, Pv, pValue, True)

                fd.close()

            fg.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)
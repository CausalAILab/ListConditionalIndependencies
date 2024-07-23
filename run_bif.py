import Node
import sys
import re
import random
from datetime import datetime

from src.graph.classes.graph import Graph
from src.graph.classes.graph_defs import basicNodeType, latentNodeType, directedEdgeType, edgeTypeMap
from src.testable_implications.conditional_independencies import ConditionalIndependencies
from src.inference.utils.graph_utils import GraphUtils as gu
from src.inference.utils.set_utils import SetUtils as su
from src.projection.projection_utils import ProjectionUtils as pu
from src.adjustment.adjustment_sets_utils import writeNodeNames, compareNames

def testAlgorithm(G, alg):
    start = datetime.now()

    if alg == 'gmp':
        CI = ConditionalIndependencies.GMP(G, G.nodes)
    elif alg == 'lmp':
        CI = ConditionalIndependencies.LMP(G, G.nodes)
    elif alg == 'listci':
        CI = ConditionalIndependencies.ListCI(G, G.nodes)

    end = datetime.now()

    # print runtime
    print('Time (' + alg + '): ' + str(end - start))
    print('CIs: ' + str(len(CI)))
    # printCI(CI, alg)
    

def printCI(CI, alg):
    if CI is None or len(CI) == 0:
        print('No conditional independence is implied.')
    else:
        for ci in CI:
            if alg == 'gmp':
                X = ci['X']
                Y = ci['Y']
                Z = ci['Z']
            elif alg == 'lmp' or alg == 'lmpp' or alg == 'listci':
                X = [ci['X']]
                Y = ci['W']
                Z = ci['Z']

            Xnames = sorted(list(map(lambda n: n['name'], X)))
            Ynames = sorted(list(map(lambda n: n['name'], Y)))
            Znames = sorted(list(map(lambda n: n['name'], Z)))

            print(writeNodeNames(Xnames) + ' \indep ' + writeNodeNames(Ynames) + ' | ' + writeNodeNames(Znames))

        print('Conditional independencies (' + str(len(CI)) + ') in total.')

# bif parser: https://github.com/atcbosselut/bif-parser
def parseToBIFNodes(fileContent):
    fileContent = fixWhiteSpace(fileContent)
    parsedNodes = parseBIF(fileContent)

    return parsedNodes

def fixWhiteSpace(BIF_white):
    i=0
    while i<len(BIF_white):
        if BIF_white[i] == "\n": #or a[i] == "}\n":
            #Remove whitespace lines
            del BIF_white[i]
        else:
            #Add a space after every piece of punctuation. This will make all distinct words separated only by punctuation
            #distinct entries in the list of values when we split a line
            BIF_white[i]=re.sub('([,])', r'\1 ', BIF_white[i])

            #Get rid of white space at the beginning and end
            BIF_white[i]=BIF_white[i].strip()
            i+=1
    #print BIF_white
    return BIF_white

def parseBIF(BIF):
    i=0
    nodes=[]
    while i<len(BIF):
        lineList = BIF[i].split()
        #If this line is a variable declaration
        if lineList[0] == 'variable':
            name = lineList[1]
            i=i+1
            #While the end of the declaration is not parsed
            while BIF[i]!='}':
                lineList = BIF[i].split()
                if lineList[0] == 'type':
                    #Parse the variable type - will be discrete in most cases
                    theType = lineList[1]

                    #Parse the number of states
                    numStates = int(lineList[3])

                    #Remove commas from the names of possible states for this variable
                    lineList[6:6+numStates] = [x.strip(",") for x in lineList[6:6+numStates]]

                    #Set a tuple containing the states
                    theStates = tuple(lineList[6:6+numStates])

                    #Set property to be null string
                    theProperty=""
                elif lineList[0]=='property':
                    #If there is a property, record it
                    theProperty=" ".join(lineList[1:])
                i+=1
            #Append the new node to the list of nodes
            #THIS IS WHERE YOU MUST CHANGE THE INSTANTIATION OF A NODE IF YOU CHANGE THE CONSTRUCTOR IN THE NODE CLASS
            nodes.append(Node.Node(name,theType,numStates,theStates, theProperty))
        elif lineList[0] == 'probability':
            #If this is declaration is a probability distribution

            #Add spaces before and after parentheses
            BIF[i]=re.sub('([()])', r' \1 ', BIF[i])

            lineList = BIF[i].split()

            #Find the query variable
            for theNode in nodes:
                if theNode.getName() == lineList[2]:
                    temp = theNode
                    break

            #Add parents to the query variables if there are any        
            if lineList[3] == '|':
                j=4
                while lineList[j] != ')':
                    for parent in nodes:
                        #Find the parents in the list of nodes
                        if parent.getName() == lineList[j].strip(","):
                            temp.addParent([parent])
                            parent.addChildren([temp])
                            break
                    j+=1
            i+=1

            # no need to parse distribution

            # theCPD = {}
            #While the end of the declaration is not parsed
            # while BIF[i]!='}':   
            #     lineList = BIF[i].split()
            #     print(lineList)
            #     if lineList[0] == 'table':
            #         #Get rid of the identifier
            #         del lineList[0]

            #         #Get rid of commas and semicolons
            #         prob = [x.translate(None, ",;") for x in lineList]

            #         #Store the distribution (this is a marginal distribution)
            #         theCPD[temp.getStates()] = tuple([float(h) for h in prob])

            #     elif lineList[0][0] == "(":
            #         #Remove all punctuation from the evidence names and the probability values
            #         lineList = [states.translate(None,"(,;)") for states in lineList]

            #         #In the CPD dictionary key, the states of the node are stored first. The second tuple is that of the parent values
            #         theCPD[(temp.getStates(), tuple(lineList[:temp.numParents()]))] = tuple([float(h) for h in lineList[temp.numParents():]])                    
            #     i+=1
            #print theCPD
            # temp.setDist(theCPD)
        else:
            i=i+1
    return nodes

def printBIFNodes(nodes):
    for node in nodes:
        print(node.getName())
        print('Parents: ')
        for p in node.parents:
            print(p.getName())
        # print "CPD: "
        # print self.getDist()
        # print("Children: ")
        # for c in node.children:
        #     print(c.getName())
        print('')

def BIFNodesToGraph(parsedNodes, latentFraction = None):
    G = Graph()

    if parsedNodes is None:
        return G

    nodesToAdd = []
    edgesToAdd = []

    for bifNode in parsedNodes:
        # construct nodes
        name = bifNode.getName()
        node = {'name': name, 'label': name, 'type_': basicNodeType.id_, 'metadata': {}}

        # if node does not exist, add to nodes list
        if not su.belongs(node, nodesToAdd, compareNames):
            nodesToAdd.append(node)

        # add directed edges: Pa -> node
        for bifParent in bifNode.parents:
            parentName = bifParent.getName()
            parent = {'name': parentName, 'label': parentName, 'type_': basicNodeType.id_, 'metadata': {}}

            # if parent does not exist, add to nodes list
            if not su.belongs(parent, nodesToAdd, compareNames):
                nodesToAdd.append(parent)

            edge = {'from_': parentName, 'to_': name, 'type_': directedEdgeType.id_, 'metadata': {}}
            edgesToAdd.append(edge)

    # sample x% of nodes and turn those to latent
    if latentFraction is not None:
        k = int(len(parsedNodes) * latentFraction)
        indices = random.sample(range(len(parsedNodes)), k)

        V = []

        for i in range(len(nodesToAdd)):
            if i in indices:
                node = nodesToAdd[i]
                node['type_'] = latentNodeType.id_
            else:
                V.append(node)

        G.addNodes(nodesToAdd)
        G.addEdges(edgesToAdd)

        G = pu.projectOver(G,V)

    return G

def printGraphToEditorFormat(G):
    print('<NODES>')

    nodeNames = list(map(lambda n: n['name'], G.nodes))

    print('\n'.join(nodeNames))

    print('\n<EDGES>')

    edgeList = list(map(
        lambda e: e['from_'] + ' ' + edgeTypeMap[e['type_']].shortId + ' ' + e['to_'], G.edges))

    print('\n'.join(edgeList))

    print('Nodes: ' + str(len(G.nodes)))
    print('Edges: ' + str(len(G.edges)))

# graph files from bnlearn: https://www.bnlearn.com/bnrepository/
# bif file info (# of nodes)
# sm: [1,20]
# md: [21,50]
# lg: [51,100]
# vl: [101,1000]
# ml: [1001,]

if __name__ == '__main__':

    # read arguments
    if len(sys.argv) != 2:
        print('Please specify input file path (e.g., bif/sm/asia.bif).')

        sys.exit()

    filePath = sys.argv[1]

    # algorithms = ['gmp', 'lmp', 'listci']
    algorithms = ['lmp', 'listci']

    try:
        with open(filePath, 'r') as f:
            fileContent = f.readlines()
            bifNodes = parseToBIFNodes(fileContent)
            G = BIFNodesToGraph(bifNodes)
            # G = BIFNodesToGraph(bifNodes, 0.5)
            # printGraphToEditorFormat(G)

            # if G is not None:
            #     for alg in algorithms:
            #         testAlgorithm(G, alg)

            f.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)
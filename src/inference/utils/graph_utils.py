from enum import Enum
from toposort import toposort_flatten

from src.graph.classes.graph_defs import basicNodeType, latentNodeType, directedEdgeType, bidirectedEdgeType, undirectedEdgeType

from src.inference.utils.set_utils import SetUtils as su
from src.common.object_utils import ObjectUtils as ou

distribution_ids = 'distribution_ids'
suffix = '\''


class Direction(Enum):
    both = 0
    forward = 1
    backward = 2


def sortByName(node):
    return node['name']


def compareNames(n1, n2):
    return n1['name'] == n2['name']


class GraphUtils():

    # Graph, Graph
    # boolean
    @staticmethod
    def equals(G1, G2):
        # fix edge comparison
        if su.equals(G1.nodes, G2.nodes, 'name') and len(G1.edges) == len(G2.edges):
            return True

        if len(G1.nodes) != len(G2.nodes) or len(G1.edges) != len(G2.edges):
            return False

        compNodes = dict()

        for node in G1.nodes:
            compNodes[node['name']] = True

        for node in G2.nodes:
            if node['name'] not in compNodes:
                return False

        compEdges = dict()

        for edge in G1.edges:
            compEdges[edge['from_'] + edge['type_'] + edge['to_']] = True

            # bidirected edge (X <-> Y and Y <-> X should be treated as equal)
            if edge['type_'] == bidirectedEdgeType.id_:
                compEdges[edge['to_'] + edge['type_'] + edge['from_']] = True

        for edge in G2.edges:
            if edge['from_'] + edge['type_'] + edge['to_'] not in compEdges:
                return False

        return True

    # Graph

    @staticmethod
    def clone(G, simplified=False):
        return G.copy()

    @staticmethod
    def clear(G):
        G.nodes = []
        G.edges = []
        G.metadata = dict()

    # Node[]

    @staticmethod
    def parents(w, G):
        return G.parents(w)

    # Node[]

    @staticmethod
    def parentsPlus(w, G):
        w = ou.makeArray(w)
        return su.union(w, GraphUtils.parents(w, G))

    # Node[]

    @staticmethod
    def children(w, G):
        return G.children(w)

    # Node[]

    @staticmethod
    def neighbors(w, G, edgeType=None):
        return G.neighbors(w, edgeType)

    # Node[]

    @staticmethod
    def ancestors(w, G):
        # return G.ancestors(w)
        return GraphUtils.reach(w, G, directedEdgeType, Direction.backward)

    # Node | Node[], Graph
    # Node[]

    @staticmethod
    def descendants(w, G):
        # return G.descendants(w)
        return GraphUtils.reach(w, G, directedEdgeType, Direction.forward)

    # Node[]

    @staticmethod
    def nonDescendants(w, G):
        return su.difference(G.nodes, GraphUtils.descendants(w, G), 'name')

    @staticmethod
    def spouses(w, G):
        w = ou.makeArray(w)
        Sp = []

        for node in w:
            Spnode = GraphUtils.neighbors(node, G, bidirectedEdgeType)
            Sp = su.union(Sp, Spnode, 'name')
        
        return Sp

    # Node | Node[], Graph, EdgeType, Direction
    # Node[]

    @staticmethod
    def reach(w, G, edgeType=None, direction=Direction.both):
        w = ou.makeArray(w)

        edges = []

        if not edgeType:
            edges = G.edges
        else:
            edges = list(filter(lambda e: e['type_'] == edgeType.id_, G.edges))

        fringe = []
        visited = dict()

        for node in w:
            fringe.append(node['name'])

        while len(fringe) > 0:
            nodeName = fringe.pop()

            # avoid cycles
            if nodeName in visited:
                continue

            visited[nodeName] = True

            for edge in edges:
                if (
                    (direction == Direction.both or direction == Direction.backward)
                    and edge['to_'] == nodeName
                    and edge['from_'] not in visited
                ):
                    fringe.append(edge['from_'])

                if (
                    (direction == Direction.both or direction == Direction.forward)
                    and edge['from_'] == nodeName
                    and edge['to_'] not in visited
                ):
                    fringe.append(edge['to_'])

        reachableNodes = list(filter(lambda n: n['name'] in visited, G.nodes))

        return reachableNodes

    @staticmethod
    def filterBasicNodes(nodes, excludeLatentNodes=True):
        if not nodes:
            return []

        # add clusterNodeType
        if excludeLatentNodes:
            return list(filter(lambda n: n['type_'] == basicNodeType.id_, nodes))
        else:
            return list(filter(lambda n: n['type_'] == basicNodeType.id_ or n['type_'] == latentNodeType.id_, nodes))

    # Edge[]

    @staticmethod
    def getIncoming(w, G):
        w = ou.makeArray(w)
        wMap = GraphUtils.mapNodeNames(w)
        incoming = list(filter(lambda e: (
            e['type_'] == bidirectedEdgeType.id_ and e['from_'] in wMap) or e['to_'] in wMap, G.edges))

        return incoming

    # Edge[]

    @staticmethod
    def getOutgoing(w, G):
        w = ou.makeArray(w)
        wMap = GraphUtils.mapNodeNames(w)
        outgoing = list(filter(
            lambda e: e['type_'] != bidirectedEdgeType.id_ and e['from_'] in wMap, G.edges))

        return outgoing

    # Graph

    @staticmethod
    def subgraph(G, subset, activeEdges=[]):
        if G is None:
            return None

        if subset is None:
            return G

        graph = G.copy()
        graph.deleteNodes(graph.nodes)
        graph.addNodes(su.intersection(G.nodes, subset, 'name'))

        sub = dict()

        for node in subset:
            sub[node['name']] = True

        edges = list(filter(lambda e: e['from_']
                     in sub and e['to_'] in sub, G.edges))

        # if activeEdges:
        #     edges = list(filter(lambda e: e['from_'] == ))

        graph.deleteEdges(graph.edges)
        graph.addEdges(edges)

        return graph

    # Graph, Node[] | str[], Node[] | str[]

    @staticmethod
    def transform(G, overline=[], underline=[], overlineExcept=[], underlineExcept=[]):
        # if overline and len(overline) > 0 and isinstance(overline[0], str):
        #     overline = GraphUtils.getNodesByName(overline, G)

        # if underline and len(underline) > 0 and isinstance(underline[0], str):
        #     underline = GraphUtils.getNodesByName(underline, G)

        if not overline:
            overline = []
        if not underline:
            underline = []

        over = dict()
        under = dict()
        overExcept = dict()
        underExcept = dict()

        for node in overline:
            over[node['name']] = True
        for node in underline:
            under[node['name']] = True
        for node in overlineExcept:
            overExcept[node['name']] = True
        for node in underlineExcept:
            underExcept[node['name']] = True

        graph = G.copy()

        edgesToRemove = []

        for edge in graph.edges:
            if edge['to_'] in over and edge['from_'] not in overExcept:
                edgesToRemove.append(edge)
                continue

            if (
                (edge['type_'] == directedEdgeType.id_ and edge['from_']
                 in under and edge['to_'] not in underExcept)
                or (edge['type_'] == bidirectedEdgeType.id_ and edge['from_'] in over)
            ):
                edgesToRemove.append(edge)
                continue

        graph.deleteEdges(edgesToRemove)

        return graph

    @staticmethod
    def moralize(G):
        graph = G.copy()

        # convert all edges to undirected
        graph.toUndirected()

        for edge in graph.edges:
            edge['type_'] = undirectedEdgeType.id_

        edgesToAdd = []

        for node in G.nodes:
            Pa = GraphUtils.parents(node, G)

            # generate pairs
            names = list(map(lambda n: n['name'], Pa))
            pairs = [(a, b) for a in names for b in names if b > a]

            for (a, b) in pairs:
                if GraphUtils.hasEdge(a, b, graph) or GraphUtils.hasEdge(b, a, graph):
                    continue

                edge = {
                    'from_': a,
                    'to_': b,
                    'type_': undirectedEdgeType.id_
                }

                edgesToAdd.append(edge)

        graph.addEdges(edgesToAdd)

        return graph

    # Graph, Node[]
    # Graph

    @staticmethod
    def ancestral(G, V):
        V = ou.makeArray(V)

        An = GraphUtils.ancestors(V, G)
        AnG = GraphUtils.subgraph(G, V + An)

        return AnG

    # Node[][]

    @staticmethod
    def cCompDecomposition(G, sortNodesBeforeOrdering=False):
        assignment = {}
        number = 0
        decomp = []
        V = GraphUtils.topoSort(G, sortNodesBeforeOrdering)

        for node in V:
            if node['name'] not in assignment:
                # decomp[number] = []
                decomp.append([])
                assignment[node['name']] = number

                reachable = GraphUtils.reach(
                    node, G, bidirectedEdgeType, Direction.both)

                for rNode in reachable:
                    assignment[rNode['name']] = number
                    decomp[number].append(rNode)

                number = number + 1

        return decomp

    # str, Graph
    # Node

    @staticmethod
    def getNodeByName(name, G):
        if not name or not G or not G.nodes:
            return None

        return next((n for n in G.nodes if GraphUtils.correctNodeName(n['name']) == GraphUtils.correctNodeName(name)), None)

    # str | str[], Graph
    # Node

    @staticmethod
    def getNodesByName(names, G):
        if not names or not G:
            return []

        names = ou.makeArray(names)
        dNames = dict()

        for name in names:
            if isinstance(name, str):
                dNames[GraphUtils.correctNodeName(name)] = False
            else:
                v = name
                dNames[GraphUtils.correctNodeName(v['name'])] = False

        for node in G.nodes:
            if GraphUtils.correctNodeName(node['name']) in dNames:
                dNames[GraphUtils.correctNodeName(node['name'])] = node

        nodes = []

        for name in names:
            actualName = ''

            if isinstance(name, str):
                actualName = GraphUtils.correctNodeName(name)
            else:
                actualName = GraphUtils.correctNodeName(node['name'])

            if actualName in dNames and dNames[actualName] is not False:
                nodes.append(dNames[actualName])

        return nodes

    # str, str, Graph, EdgeType
    # Edge

    @staticmethod
    def getEdgeByName(from_, to_, G, type_=None):
        if not G or not G.edges:
            return None

        fromNode = GraphUtils.getNodeByName(from_, G)
        toNode = GraphUtils.getNodeByName(to_, G)

        if not fromNode or not toNode:
            return None

        if not type_:
            return next((e for e in G.edges if e['from_'] == fromNode['name'] and e['to_'] == toNode['name']), None)
        else:
            return next((e for e in G.edges if e['from_'] == fromNode['name'] and e['to_'] == toNode['name'] and e['type_'] == type_.id_), None)

    @staticmethod
    def hasEdge(from_, to_, G, type=None):
        return G.nx.has_edge(from_, to_)

    # G, boolean
    # Node[]

    @staticmethod
    def topoSort(G, sort_=False):
        nodeNames = list(map(lambda n: n['name'], G.nodes))

        # create dict of dependencies to run toposort
        # format: {to: {from1, from2, ...}}
        dep = dict()

        for edge in G.edges:
            # directed edges only
            if edge['type_'] != directedEdgeType.id_:
                continue

            if edge['to_'] not in dep:
                dep[edge['to_']] = set()

            dep[edge['to_']].add(edge['from_'])

        nodeNames = toposort_flatten(dep, sort_)

        V = GraphUtils.getNodesByName(nodeNames, G)

        return su.union(V, G.nodes, 'name')

    @staticmethod
    def nodesToVariables(nodes):
        nodes = ou.makeArray(nodes)

        variables = []

        for node in nodes:
            if 'label' in node:
                variables.append(
                    {'name': node['name'], 'label': node['label']})
            else:
                variables.append({'name': node['name']})

        return variables

    @staticmethod
    def toString(G):
        return ''

    @staticmethod
    def correctNodeName(name):
        if not name:
            return ''

        return name.strip().upper()

    # Node | Node[]
    # Dict[key, boolean]
    @staticmethod
    def nodeToNameMap(nodes):
        nodes = ou.makeArray(nodes)

        names = dict()

        for node in nodes:
            names[node['name']] = True

        return names

    @staticmethod
    def nodeToList(nodes, attribute='name'):
        nodes = ou.makeArray(nodes)

        attrs = []

        for node in nodes:
            attrs.append(node[attribute])

        return attrs

    @staticmethod
    def mapNodeNames(nodes):
        nodes = ou.makeArray(nodes)

        namesMap = dict()

        for node in nodes:
            namesMap[node['name']] = True

        return namesMap
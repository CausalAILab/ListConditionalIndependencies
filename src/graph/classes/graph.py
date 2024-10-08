import random

import networkx as nx
from typing import Dict, Any

from src.graph.classes.graph_defs import basicNodeType, directedEdgeType, bidirectedEdgeType, EdgeType, edgeTypeMap
from src.task.classes.task import Task
from src.task.basic_task import BasicTask

from src.inference.utils.graph_utils import GraphUtils as gu
from src.inference.utils.set_utils import SetUtils as su
from src.common.object_utils import ObjectUtils as ou


class Graph():

    name = str
    task = Task
    metadata = Dict[str, Any]

    def __init__(self, graph=None, nodes=[], edges=[], task=None, metadata=dict()):
        if graph is not None:
            if isinstance(graph, nx.Graph) or isinstance(graph, nx.DiGraph):
                self.nx = graph
            elif isinstance(graph, Graph):
                self.nx = graph.nx
        else:
            self.nx = nx.DiGraph()
            self.addNodes(nodes)
            self.addEdges(edges)

        if task is None:
            task = BasicTask()

        self.task = task
        self.metadata = metadata

    @property
    def nodes(self):
        nodes = self.nx.nodes(data=True)
        ns = []

        # convert tuple to list of dictionaries
        for node in nodes:
            n = {
                'name': node[0],
                'label': node[1]['label'] if 'label' in node[1] else node[0],
                'type_': node[1]['type_'] if 'type_' in node[1] else basicNodeType.id_,
                'metadata': node[1]['metadata'] if 'metadata' in node[1] else {}
            }

            ns.append(n)

        return ns

    @nodes.setter
    def nodes(self, nodes):
        self.nx.clear()
        self.addNodes(nodes)

    @property
    def edges(self):
        edges = self.nx.edges(data=True)
        es = []

        for edge in edges:
            e = {
                'from_': edge[0],
                'to_': edge[1],
                'label': edge[2]['label'] if 'label' in edge[2] else None,
                'type_': edge[2]['type_'] if 'type_' in edge[2] else directedEdgeType.id_,
                'metadata': edge[2]['metadata'] if 'metadata' in edge[2] else {}
            }

            es.append(e)

        return es

        # return self.nx.edges(data = True)

    @edges.setter
    def edges(self, edges):
        self.deleteEdges(self.edges)
        self.addEdges(edges)

    def copy(self):
        return Graph(self.nx.copy())

    def toUndirected(self):
        # return self.nx.to_undirected()
        self.nx = nx.Graph(self.nx)

        # change all edge types


    def addRandomNodes(self, n, nodeType=basicNodeType.id_):
        nodes = []

        for i in range(n):
            node = {'name': str(i),'label': str(i),'type_': nodeType,'metadata': {}}
            nodes.append(node)
        
        self.addNodes(nodes)

        return nodes

    # possible improvements
    # adding directed edges: 1) pick a topological order, 2) add X -> Y where X < Y.
    # adding bidirected edges: 1) pick permutation, 2) add X -- Y (be careful not to overwrite X -> Y)
    def addRandomEdges(self, m, edgeType=directedEdgeType.id_, randomSeed=None):
        if m == 0:
            return

        if randomSeed is not None:
            random.seed(randomSeed)

        n = len(self.nodes)

        edges = []
        edgeCount = 0

        if edgeType == directedEdgeType.id_:
            while (edgeCount < m):
                x = int(random.random() * n)
                y = int(random.random() * n)

                if x == y:
                    continue

                edge = {'from_': str(x), 'to_': str(y), 'label': None, 'type_': directedEdgeType.id_, 'metadata': {}}

                if not self.nx.has_edge(edge['from_'], edge['to_']):
                    self.__addEdge(edge)

                    try:
                        cycle = nx.find_cycle(self.nx)
                        self.__deleteEdge(edge)
                    except nx.exception.NetworkXNoCycle:
                        edgeCount = edgeCount + 1
                        edges.append(edge)
                        continue

                if not self.nx.has_edge(edge['to_'], edge['from_']):
                    edge = {'from_': str(y), 'to_': str(x), 'label': None, 'type_': directedEdgeType.id_, 'metadata': {}}
                    self.__addEdge(edge)

                    try:
                        cycle = nx.find_cycle(self.nx)
                        self.__deleteEdge(edge)
                    except nx.exception.NetworkXNoCycle:
                        edgeCount = edgeCount + 1
                        edges.append(edge)
                        continue
        elif edgeType == bidirectedEdgeType.id_:
            while (edgeCount < m):
                x = int(random.random() * n)
                y = int(random.random() * n)

                if x == y:
                    continue
                
                edge = {'from_': str(x), 'to_': str(y), 'label': None, 'type_': bidirectedEdgeType.id_, 'metadata': {}}

                # if X -- Y or X -> Y exists
                #   check if X -- Y
                #    if true, skip
                #   else (X -> Y)
                #     check if bidirected edge Y -- X exists
                #       if true, skip
                #       else, add Y -- X
                # else
                #   check if Y -- X exists
                #     if yes, skip
                #     else (Y <- X), add X -- Y
                #   else (no edge exists)
                #     add X -- Y
                if self.nx.has_edge(edge['from_'], edge['to_']):
                    existingEdge = None

                    for e in self.edges:
                        if e['from_'] == edge['from_'] and e['to_'] == edge['to_']:
                            existingEdge = e
                            break

                    if existingEdge['type_'] == bidirectedEdgeType.id_:
                        continue
                    else:
                        if self.nx.has_edge(edge['to_'], edge['from_']):
                            continue
                        else:
                            edge = {'from_': str(y), 'to_': str(x), 'label': None, 'type_': bidirectedEdgeType.id_, 'metadata': {}}

                            self.__addEdge(edge)
                            edgeCount = edgeCount + 1
                            edges.append(edge)
                else:
                    if self.nx.has_edge(edge['to_'], edge['from_']):
                        existingEdge = None

                        for e in self.edges:
                            if e['from_'] == edge['to_'] and e['to_'] == edge['from_']:
                                existingEdge = e
                                break

                        if existingEdge['type_'] == bidirectedEdgeType.id_:
                            continue
                        else:
                            self.__addEdge(edge)
                            edgeCount = edgeCount + 1
                            edges.append(edge)
                    else:
                        self.__addEdge(edge)
                        edgeCount = edgeCount + 1
                        edges.append(edge)

        return edges

    def toRandomGraph(self, n, m, edgeType=directedEdgeType.id_, randomSeed=None):
        nodes = []

        for i in range(n):
            node = {'name': str(i),'label': str(i),'type_': basicNodeType.id_,'metadata': {}}
            nodes.append(node)
        
        self.nodes = nodes

        edges = []
        edgeCount = 0

        if randomSeed is not None:
            random.seed(randomSeed)

        if edgeType == directedEdgeType.id_:
            while (edgeCount < m):
                x = int(random.random() * n)
                y = int(random.random() * n)                

                if x == y:
                    continue

                edge = {'from_': str(x), 'to_': str(y), 'label': None, 'type_': directedEdgeType.id_, 'metadata': {}}

                if not self.nx.has_edge(edge['from_'], edge['to_']):
                    self.__addEdge(edge)

                    try:
                        cycle = nx.find_cycle(self.nx)
                        self.__deleteEdge(edge)
                    except nx.exception.NetworkXNoCycle:
                        edgeCount = edgeCount + 1
                        edges.append(edge)
                        continue

                if not self.nx.has_edge(edge['to_'], edge['from_']):
                    edge = {'from_': str(y), 'to_': str(x), 'label': None, 'type_': directedEdgeType.id_, 'metadata': {}}
                    self.__addEdge(edge)

                    try:
                        cycle = nx.find_cycle(self.nx)
                        self.__deleteEdge(edge)
                    except nx.exception.NetworkXNoCycle:
                        edgeCount = edgeCount + 1
                        edges.append(edge)
                        continue
        elif edgeType == bidirectedEdgeType.id_:
            while (edgeCount < m):
                x = int(random.random() * n)
                y = int(random.random() * n)

                if x == y:
                    continue

                edge = {'from_': str(x), 'to_': str(y), 'label': None, 'type_': bidirectedEdgeType.id_, 'metadata': {}}

                if not self.nx.has_edge(edge['from_'], edge['to_']) and not self.nx.has_edge(edge['to_'], edge['from_']):
                    self.__addEdge(edge)
                    edgeCount = edgeCount + 1
                    edges.append(edge)

        self.edges = edges

    def addNodes(self, nodes):
        nodes = ou.makeArray(nodes)

        if not nodes or len(nodes) == 0:
            return

        for node in nodes:
            # should we throw error if name is not specified?
            # duplicate name/label?

            # if not hasattr(node, 'name'):
            if 'name' not in node:
                continue

            # if not hasattr(node, 'label'):
            if 'label' not in node:
                node['label'] = node['name']

            # if not hasattr(node, 'type_'):
            if 'type_' not in node:
                node['type_'] = basicNodeType.id_

            # if not hasattr(node, 'metadata'):
            if 'metadata' not in node:
                node['metadata'] = dict()

            self.__addNode(node)

    def deleteNodes(self, nodes):
        nodes = ou.makeArray(nodes)

        if not nodes or len(nodes) == 0:
            return

        self.deleteEdges(gu.getIncoming(nodes, self))
        self.deleteEdges(gu.getOutgoing(nodes, self))

        # can we delete all at once instead?
        for node in nodes:
            self.__deleteNode(node)

    def addEdges(self, edges):
        edges = ou.makeArray(edges)
        
        if not edges or len(edges) == 0:
            return

        for edge in edges:
            if 'from_' not in edge or 'to_' not in edge:
                continue

            if 'label' not in edge:
                edge['label'] = None

            if 'type_' not in edge:
                edge['type_'] = directedEdgeType.id_

            if 'metadata' not in edge:
                edge['metadata'] = dict()

            # nx has an unintended feature
            # calling add_edge(X,Y,..) overwrites an existing edge with from: X and to: Y
            # e.g., if X -- Y exists, adding X -> Y will overwrite X -- Y, or vice versa
            if self.nx.has_edge(edge['from_'], edge['to_']):
                existingEdge = None

                for e in self.edges:
                    if e['from_'] == edge['from_'] and e['to_'] == edge['to_']:
                        existingEdge = e
                        break

                # if adding X -> Y, remove X -- Y and add Y -- X first
                if edge['type_'] == directedEdgeType.id_:
                    if existingEdge['type_'] == bidirectedEdgeType.id_:
                        self.deleteEdges(existingEdge)

                        temp = existingEdge['from_']
                        existingEdge['from_'] = existingEdge['to_']
                        existingEdge['to_'] = temp

                        self.addEdges(existingEdge)
                    else:
                        edgeType = directedEdgeType

                        for id_ in edgeTypeMap:
                            if edge['type_'].upper() == edgeTypeMap[id_].id_.upper():
                                edgeType = edgeTypeMap[id_]
                                break

                        raise Exception(
                            'The edge ' + edge['from_'] + ' ' + edgeType.shortId + ' ' + edge['to_'] + ' already exists.')

                # if adding X -- Y, flip from/to and add Y -- X instead
                elif edge['type_'] == bidirectedEdgeType.id_:
                    if existingEdge['type_'] == directedEdgeType.id_:
                        temp = edge['from_']
                        edge['from_'] = edge['to_']
                        edge['to_'] = temp
                    else:
                        edgeType = directedEdgeType

                        for id_ in edgeTypeMap:
                            if edge['type_'].upper() == edgeTypeMap[id_].id_.upper():
                                edgeType = edgeTypeMap[id_]
                                break

                        raise Exception(
                            'The edge ' + edge['from_'] + ' ' + edgeType.shortId + ' ' + edge['to_'] + ' already exists.')

            # test if the new edge generates a cycle
            self.__addEdge(edge)

            # due to the implemenation that X -- Y is stored as a directed edge in nx graph,
            # nx.find_cycle may incorrectly report a cycle
            # if edge['type_'] == directedEdgeType.id_:
            #     fromNode = gu.getNodeByName(edge['from_'], self)
            #     toNode = gu.getNodeByName(edge['to_'], self)

            #     if fromNode is not None and toNode is not None:
            #         if fromNode['type_'] == basicNodeType.id_ and toNode['type_'] == basicNodeType.id_:
            #             try:
            #                 cycle = nx.find_cycle(self.nx)
            #                 self.__deleteEdge(edge)
            #                 if cycle is not None:
            #                     raise Exception('Adding the edge ' + edge['from_'] + ' ' + edgeTypeMap[edge['type_']].shortId + ' ' + edge['to_'] + ' creates a cycle.')
            #             except nx.exception.NetworkXNoCycle:
            #                 continue

    def deleteEdges(self, edges):
        edges = ou.makeArray(edges)

        if not edges or len(edges) == 0:
            return

        # for edge in edges:
        #     self.__deleteEdge(edge)

        pairs = list(map(lambda e: (e['from_'], e['to_']), edges))
        self.__deleteEdges(pairs)

    # Node[]
    # Node[]

    def parents(self, nodes):
        nodes = ou.makeArray(nodes)

        if not nodes or len(nodes) == 0:
            return []

        names = dict()
        parents = dict()

        for node in nodes:
            names[node['name']] = True

        for edge in self.edges:
            if edge['type_'] == directedEdgeType.id_ and edge['to_'] in names:
                parents[edge['from_']] = True

        p = list(filter(lambda n: n['name'] in parents, self.nodes))

        return p

    def ancestors(self, nodes):
        nodes = ou.makeArray(nodes)

        if not nodes or len(nodes) == 0:
            return []

        AnNames = []

        for node in nodes:
            AnNames.extend(list(nx.ancestors(self.nx, node['name'])))

        AnNames = su.unique(AnNames)

        An = gu.getNodesByName(AnNames, self)
        An = su.difference(An, nodes, 'name')

        return An

    def descendants(self, nodes):
        nodes = ou.makeArray(nodes)

        if not nodes or len(nodes) == 0:
            return []

        DeNames = []

        # bug: nx treats bidirected as directed
        for node in nodes:
            DeNames.extend(list(nx.descendants(self.nx, node['name'])))

        DeNames = su.unique(DeNames)
        De = gu.getNodesByName(DeNames, self)
        De = su.difference(De, nodes, 'name')

        return De

    def children(self, nodes):
        nodes = ou.makeArray(nodes)

        names = dict()
        children = dict()

        for node in nodes:
            names[node['name']] = True

        for edge in self.edges:
            if edge['type_'] == directedEdgeType.id_ and edge['from_'] in names:
                children[edge['to_']] = True

        c = list(filter(lambda n: n['name'] in children, self.nodes))

        return c

    # Node | Node[], EdgeType | str
    # Node[]

    def neighbors(self, nodes, edgeType=None):
        nodes = ou.makeArray(nodes)

        if not nodes or len(nodes) == 0:
            return []

        if isinstance(edgeType, EdgeType):
            edgeType = edgeType.id_

        names = dict()
        neighbors = dict()

        for node in nodes:
            names[node['name']] = True

        edges = list(
            filter(lambda e: e['type_'] == edgeType if edgeType else True, self.edges))

        for edge in edges:
            if edge['to_'] in names:
                neighbors[edge['from_']] = True
            if edge['from_'] in names:
                neighbors[edge['to_']] = True

        n = list(
            filter(lambda n: n['name'] in neighbors and n['name'] not in names, self.nodes))

        return n

    def connectedComponents(self):
        # node names
        # convert to nodes
        CC = list(nx.connected_components(self.nx))
        ccsNodes = []

        # cc is a dict
        for cc in CC:
            nodeNames = []

            for nodeName in cc:
                nodeNames.append(nodeName)

            ccNodes = gu.getNodesByName(nodeNames, self)

            ccsNodes.append(ccNodes)

        return ccsNodes

    def print(self):
        if len(self.nodes) > 0:
            print('<Nodes (' + str(len(self.nodes)) + ')>')
        else:
            print('<Nodes (none)>')

        nodeNames = list(map(lambda n: n['name'], self.nodes))

        print('\n'.join(nodeNames))

        if len(self.edges) > 0:
            print('\n<Edges (' + str(len(self.edges)) + ')>')
        else:
            print('\n<Edges (none)>')

        edgeList = list(map(
            lambda e: e['from_'] + ' ' + edgeTypeMap[e['type_']].shortId + ' ' + e['to_'], self.edges))

        print('\n'.join(edgeList))

    def __addNode(self, node):
        self.nx.add_node(node['name'], label=node['label'],
                         type_=node['type_'], metadata=node['metadata'])

    def __deleteNode(self, node):
        self.nx.remove_node(node['name'])

    def __addEdge(self, edge):
        self.nx.add_edge(edge['from_'], edge['to_'], label=edge['label'],
                         type_=edge['type_'], metadata=edge['metadata'])

    def __deleteEdge(self, edge):
        self.nx.remove_edge(edge['from_'], edge['to_'])

    def __deleteEdges(self, edges):
        self.nx.remove_edges_from(edges)

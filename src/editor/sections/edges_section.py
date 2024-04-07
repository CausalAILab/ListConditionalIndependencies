import re
from typing import Dict

from src.graph.classes.graph import Graph
from src.graph.classes.graph_defs import edgeTypeMap, directedEdgeType, bidirectedEdgeType
from src.editor.classes.section import Section
from src.editor.classes.options_parser import OptionsParser
from src.editor.classes.parsing_error import ParsingError


# Regex for parsing node strings
#       from           type            to                 options                   curvature
#  /^ ([^\s]+)  \s+  ([^\s]+)  \s+   ([^\s]+)   (?:\s+\[  (.*)  \])?  (?:\s+((?:\+|-)?(?:0(?:\.\d+)?|1)))?  \s*  $/
regexExp = r'^([^\s]+)\s+([^\s]+)\s+([^\s]+)(?:\s+\[(.*)\])?(?:\s+((?:\+|-)?(?:\d+(?:\.\d+)?|\d+)))?\s*$'

errors = {
    'parse': 'Please specify an edge in correct format.',
    'nodesTagMissing': 'Please specify the nodes before edges.',
    'sourceNodeMissing': 'Please specify a valid source node.',
    'destinationNodeMissing': 'Please specify a valid destination node.',
    'edgeTypeMissing': 'Please specify a valid edge type.'
}

class EdgesSection(Section):

    tag = '<EDGES>'
    required = True
    order = 3
    optTypeMap = Dict[str, OptionsParser]
    semiMarkovianMode = True

    def __init__(self, optTypeMap = {}):
        self.optTypeMap = optTypeMap
        self.re = re.compile(regexExp)
        self.nodeMap = {}


    def parse(self, lines, parsedData = {}):
        if 'graph' not in parsedData:
            return ParsingError(errors['nodesTagMissing'])

        graph = parsedData['graph']

        self.nodeMap = {}
        
        for node in graph.nodes:
            self.nodeMap[node['name']] = node

        lineNumber = 0

        try:
            for line in lines:
                edge = self.edgeFromString(line, graph)

                filterEdge = list(filter(lambda e: e['from_'] == edge['from_'] and e['to_'] == edge['to_'] and e['type_'] == edge['type_'], graph.edges))
                # filterEdge = list(filter(lambda e: e['from_'] == edge['from_'] and e['to_'] == edge['to_'], graph.edges))
                
                if len(filterEdge) > 0:
                    edgeType = self.getEdgeType(edge['type_'])
                    shortId = edgeType.shortId if edgeType is not None else directedEdgeType.shortId

                    return ParsingError('The edge ' + edge['from_'] + ' ' + shortId + ' ' + edge['to_'] + ' already exists.', lineNumber)

                if edge['type_'] == bidirectedEdgeType.id_:
                    if self.semiMarkovianMode:
                        graph.addEdges(edge)
                    else:
                        continue
                else:
                    graph.addEdges(edge)

                # check for cycle

                lineNumber = lineNumber + 1
            
            return parsedData
        except ParsingError as e:
            return ParsingError(e.message, lineNumber)


    # str, Graph
    # Edge
    def edgeFromString(self, line, graph):
        match = self.re.match(line)

        if match is None:
            raise ParsingError(errors['parse'])

        # from, etype, to, options, curvature
        groups = match.groups()
        
        fromText = groups[0]
        eType = groups[1]
        toText = groups[2]
        options = groups[3]

        if fromText is None:
            raise ParsingError(errors['sourceNodeMissing'])

        fromNode = self.nodeMap[fromText] if fromText in self.nodeMap else None

        if fromNode is None:
            raise ParsingError('The node ' + fromText + ' does not exist.')

        if toText is None:
            raise ParsingError(errors['destinationNodeMissing'])

        toNode = self.nodeMap[toText] if toText in self.nodeMap else None

        if toNode is None:
            raise ParsingError('The node ' + toText + ' does not exist.')

        if eType is None:
            raise ParsingError(errors['edgeTypeMissing'])

        edgeType = self.getEdgeType(eType)

        if edgeType is None:
            raise ParsingError("The edge type '" + eType + "' is not supported.")

        parser = None

        if edgeType.id_ not in self.optTypeMap:
            if directedEdgeType.id_ in self.optTypeMap:
                parser = self.optTypeMap[directedEdgeType.id_]
        else:
            parser = self.optTypeMap[edgeType.id_]

        edge = {'from_': fromNode['name'], 'to_': toNode['name'], 'type_': edgeType.id_, 'metadata': {}}

        if parser is not None:
            parser.fromString(options, edge, graph)

        return edge


    # str
    # EdgeType
    def getEdgeType(self, shortId):
        if shortId is None:
            return None
        
        for id_ in edgeTypeMap:
            if shortId.upper() == edgeTypeMap[id_].shortId.upper():
                return edgeTypeMap[id_]

        return None


    def getLines(self):
        return []


    def destroy(self):
        pass
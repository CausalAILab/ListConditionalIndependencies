import random
import csv
import time
import multiprocessing as mp
from datetime import datetime, timedelta

from src.graph.classes.graph import Graph
from src.graph.classes.graph_defs import latentNodeType, directedEdgeType, bidirectedEdgeType
from src.testable_implications.ci_defs import algMap, algListGMP, algListCIBF, algListCI
from src.inference.utils.set_utils import SetUtils as su
from src.inference.utils.graph_utils import GraphUtils as gu
from src.testable_implications.conditional_independencies import ConditionalIndependencies as ci
from src.projection.projection_utils import ProjectionUtils as pu


class ExperimentUtils():

    # an internal function to organize and finalize measured parameters
    @staticmethod
    def getFullParams(G, alg, CI, runtime, listCIBFParams):
        n = len(G.nodes)
        m = len(G.edges)
        md = len(list(filter(lambda e: e['type_'] == directedEdgeType.id_, G.edges)))
        mb = len(list(filter(lambda e: e['type_'] == bidirectedEdgeType.id_, G.edges)))
        CIsize = len(CI)

        s = 1

        if alg == algListCIBF.id_:
            Snum = listCIBFParams['Snum']
            Splusnum = listCIBFParams['Splusnum']
            s = listCIBFParams['s']
        elif alg == algListCI.id_:
            V = su.intersection(gu.topoSort(G), G.nodes, 'name')
            ACsizes = []

            for X in V:
                VleqX = V[:V.index(X)+1]
                GVleqX = gu.subgraph(G, VleqX)
                
                R = ci.C(GVleqX,X)
                ACsizes.append(len(R))

            if len(ACsizes) > 0:
                s = max(ACsizes)

        params = []

        if alg == algListGMP.id_:
            params = [n, m, md, mb, CIsize, runtime]
        elif alg == algListCIBF.id_:
            params = [n, m, md, mb, CIsize, runtime, s, Snum, Splusnum]
        elif alg == algListCI.id_:
            params = [n, m, md, mb, CIsize, runtime, s]

        return params


    @staticmethod
    def runAlgorithm(queue, G, alg, specs):
        orgVordered = specs['Vordered']

        if orgVordered is not None:
            Vordered = su.intersection(orgVordered, G.nodes, 'name')
        else:
            Vordered = None

        CI = queue.get()
        listCIBFParams = queue.get()

        if alg == algListGMP.id_:
            CIs = ci.ListGMP(G, G.nodes)
        elif alg == algListCIBF.id_:
            CIs = ci.ListCIBF(G, G.nodes, True, Vordered, listCIBFParams)
        elif alg == algListCI.id_:
            CIs = ci.ListCI(G, G.nodes, Vordered)

        CI.extend(CIs)

        queue.put(CI)
        queue.put(listCIBFParams)


    @staticmethod
    def runAlgorithmAndMeasureParams(G, alg, specs):
        timeout = specs['timeout']

        CI = []
        listCIBFParams = {}

        # use queue to pass values between processes
        queue = mp.Queue()
        queue.put(CI)
        queue.put(listCIBFParams)
        p = mp.Process(target=ExperimentUtils.runAlgorithm, args=(queue, G, alg, specs))

        start = datetime.now()
        p.start()
        p.join(timeout=timeout)

        if p.is_alive():
            p.terminate()
            p.join()

            currentAlg = algMap[alg]
            paramNames = currentAlg.params
            params = ['-'] * len(paramNames)

            return params
        
        end = datetime.now()

        CI = queue.get()
        listCIBFParams = queue.get()
        runtime = ExperimentUtils.roundToNearestSecond(end - start)

        params = ExperimentUtils.getFullParams(G, alg, CI, runtime, listCIBFParams)

        return params

    # @staticmethod
    # def runAlgorithmAndMeasureParams(G, alg=algListCI.id_):
    #     if G is None:
    #         return []

    #     measuredParams = {}

    #     start = datetime.now()

    #     if alg == algListGMP.id_:
    #         CI = ci.ListGMP(G, G.nodes)
    #     elif alg == algListCIBF.id_:
    #         CI = ci.ListCIBF(G, G.nodes, True, None, measuredParams)
    #     elif alg == algListCI.id_:
    #         CI = ci.ListCI(G, G.nodes)

    #     end = datetime.now()

    #     if alg == algListCIBF.id_:
    #         Snum = measuredParams['Snum']
    #         Splusnum = measuredParams['Splusnum']
    #         s = measuredParams['s']
    #     elif alg == algListCI.id_:
    #         V = su.intersection(gu.topoSort(G), G.nodes, 'name')
    #         ACsizes = []

    #         for X in V:
    #             VleqX = V[:V.index(X)+1]
    #             GVleqX = gu.subgraph(G, VleqX)
                
    #             R = ci.C(GVleqX,X)
    #             ACsizes.append(len(R))

    #         if len(ACsizes) > 0:
    #             s = max(ACsizes)
    #         else:
    #             s = 1

    #     # get parameters
    #     n = len(G.nodes)
    #     m = len(G.edges)
    #     md = len(list(filter(lambda e: e['type_'] == directedEdgeType.id_, G.edges)))
    #     mb = len(list(filter(lambda e: e['type_'] == bidirectedEdgeType.id_, G.edges)))
    #     CIsize = len(CI)
    #     runtime = ExperimentUtils.roundToNearestSecond(end - start)

    #     params = []

    #     if alg == algListGMP.id_:
    #         params = [n, m, md, mb, CIsize, runtime]
    #     elif alg == algListCIBF.id_:
    #         params = [n, m, md, mb, CIsize, runtime, s, Snum, Splusnum]
    #     elif alg == algListCI.id_:
    #         params = [n, m, md, mb, CIsize, runtime, s]
        
    #     return params
    

    @staticmethod
    def printParams(paramsCollection=[], algId=algListCI.id_):
        numGraphs = len(paramsCollection)
        numDivisions = len(paramsCollection[0])

        # print header row
        headerTextBlocks = []
        
        for j in range(numDivisions):
            sampleLine = ''

            if algId == algListGMP.id_:
                sampleLine = 'n\tm\tmd\tmu\t# CI\truntime'
            elif algId == algListCIBF.id_:
                sampleLine = 'n\tm\tmd\tmu\t# CI\truntime\ts\t# S\t# S+'
            elif algId == algListCI.id_:
                sampleLine = 'n\tm\tmd\tmu\t# CI\truntime\ts'

            headerTextBlocks.append(sampleLine)

        print('\t'.join(headerTextBlocks))

        for i in range(numGraphs):
            paramsRow = paramsCollection[i]
            textBlocks = []

            for j in range(numDivisions):
                sampleParam = paramsRow[j]
                paramToStr= list(map(lambda n: str(n), sampleParam))

                sampleLine = '\t'.join(paramToStr)

                textBlocks.append(sampleLine)

            print('\t'.join(textBlocks))
        

    @staticmethod
    def writeParamsToCsv(fileName, paramsCollection=[], algId=algListCI.id_):
        numGraphs = len(paramsCollection)
        numDivisions = len(paramsCollection[0])

        headers = []

        for j in range(numDivisions):
            header = []

            if algId == algListGMP.id_:
                header = ['n', 'm', 'md', 'mu', '# CI', 'runtime']
            elif algId == algListCIBF.id_:
                header = ['n', 'm', 'md', 'mu', '# CI', 'runtime', 's', '# S', '# S+']
            elif algId == algListCI.id_:
                header = ['n', 'm', 'md', 'mu', '# CI', 'runtime', 's']

            headers.extend(header)

        data = []

        for i in range(numGraphs):
            paramsRow = paramsCollection[i]
            textBlocks = []

            for j in range(numDivisions):
                sampleParam = paramsRow[j]
                paramToStr = list(map(lambda n: str(n), sampleParam))

                textBlocks.extend(paramToStr)

            data.append(textBlocks)

        with open(fileName + '.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',')

            writer.writerow(headers)
            writer.writerows(data)

            print('Results written to ' + fileName + '.csv.')
    

    @staticmethod
    def durationStringToSeconds(runtime):
        x = time.strptime(runtime, '%H:%M:%S')
        seconds = timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
        
        # round up to avoid undefined value in log-log plot
        # if seconds == 0.0:
        #     seconds = seconds + 1

        return seconds
    

    @staticmethod
    def roundToNearestSecond(td):
        return timedelta(seconds=int(td.total_seconds()))


    # @staticmethod
    # def constructDirGraph(n, m):
    #     G = Graph()
    #     G.addRandomNodes(n)
    #     G.addRandomEdges(m)

    #     return G


    # @staticmethod
    # def constructBidirGraph(n, m, randomSeed=0):
    #     G = Graph()
    #     G.toRandomGraph(n, m, bidirectedEdgeType.id_, randomSeed)

    #     return G


    @staticmethod
    def constructRandomGraph(n, md, mb, randomSeed=None):
        G = Graph()
        G.addRandomNodes(n)
        G.addRandomEdges(md, directedEdgeType.id_, randomSeed)
        G.addRandomEdges(mb, bidirectedEdgeType.id_, randomSeed)

        return G
    

    @staticmethod
    def constructBidirConvGraph(n, m, mb=0):
        G = Graph()
        G.toRandomGraph(n,m)

        # # sample x% of edges and turn those to bidirected
        if mb > 0 and mb <= m:
            edges = G.edges

            indices = random.sample(range(m), mb)

            newEdges = []
            
            for i in range(m):
                edge = edges[i]

                if i in indices:
                    edge['type_'] = bidirectedEdgeType.id_
                    
                newEdges.append(edge)

            G.edges = newEdges

        return G
    
    @staticmethod
    def applyProjection(G, U=0.3, randomSeed=None):
        if U == 0:
            return G
        
        nodes = G.nodes
        edges = G.edges

        # sample x% of nodes and turn those to latent
        if randomSeed is not None:
            random.seed(randomSeed)

        k = int(len(nodes) * U)
        indices = random.sample(range(len(nodes)), k)

        newNodes = []
        V = []

        for i in range(len(nodes)):
            node = nodes[i]

            if i in indices:
                node['type_'] = latentNodeType.id_
            else:
                V.append(node)

            newNodes.append(node)
        
        Gp = G.copy()
        Gp.nodes = newNodes
        Gp.edges = edges
        Gp = pu.projectOver(Gp,V)

        return Gp
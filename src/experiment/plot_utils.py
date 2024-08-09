import numpy as np

from src.testable_implications.ci_defs import algMap, algListGMP, algListCIBF, algListCI
from src.testable_implications.ci_utils import ConditionalIndependenceUtils as cu


class PlotUtils():

    # use/set colors
    # https://colorbrewer2.org/#type=diverging&scheme=Spectral&n=8

    @staticmethod
    def paramNameToAxisLabel(paramName, averageSamples=True):
        if paramName == 'proj':
            return 'Projected out observed nodes (%)'
        if paramName == 'u_clique':
            return 'pb'
        elif paramName == 'n':
            if averageSamples:
                return 'Average number of nodes'
            else:
                return 'Number of nodes'
        elif paramName == 'm':
            if averageSamples:
                return 'Average number of edges'
            else:
                return 'Number of edges'
        elif paramName == 's':
            if averageSamples:
                return 'Average s'
            else:
                return 's (size of the largest c-component)'
        elif paramName == 'runtime':
            if averageSamples:
                return 'Average runtime in seconds'
            else:
                return 'Runtime in seconds'
        elif paramName == 'CI':
            if averageSamples:
                return 'Average number of CIs'
            else:
                return 'Number of CIs'
        elif paramName == 'S':
            if averageSamples:
                return 'Average number of ancestral sets'
            else:
                return 'Number of ancestral sets'
        elif paramName == 'Splus':
            if averageSamples:
                return 'Average number of maximal ancestral sets'
            else:
                return 'Number of maximal ancestral sets'
            
        return ''
    
    @staticmethod
    def parseData(alg, lines):
        paramNames = []

        if alg == algListGMP.id_:
            paramNames = algListGMP.params
        elif alg == algListCIBF.id_:
            paramNames = algListCIBF.params
        elif alg == algListCI.id_:
            paramNames = algListCI.params

        # specific for s/CI/runtime
        # paramNames = ['s', 'CI', 'runtime']

        paramsCollection = []

        for i in range(len(paramNames)):
            paramsCollection.append([])
        
        numSamples = len(lines[0])

        for i in range(len(lines)):
            line = lines[i]

            collectionIndex = i % len(paramNames)

            measurements = []

            if paramNames[collectionIndex] == 'runtime':
                measurements = list(map(lambda t: np.nan if t.strip() == '-' else cu.durationStringToSeconds(t), line))
            else:
                measurements = list(map(lambda x: np.nan if x.strip() == '-' else int(x), line))

            paramsCollection[collectionIndex].extend(measurements)

        data = {
            'numSamples': numSamples
        }

        for i in range(len(paramNames)):
            data[paramNames[i]] = np.array(paramsCollection[i])
        
        return data
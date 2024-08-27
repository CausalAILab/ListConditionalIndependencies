import numpy as np
import matplotlib.colors as mcolors

from src.testable_implications.ci_defs import algMap, algListGMP, algListCIBF, algListCI
from src.experiment.experiment_utils import ExperimentUtils as eu

# redColor = '#f00'
# blueColor = '#2D7BB1'
# greenColor = '#5CB769'

class PlotUtils():

    # use/set colors
    # https://colorbrewer2.org/#type=diverging&scheme=Spectral&n=8
    @staticmethod
    def getColorPalette(numDivisions=6):
        red = '#d53e4f'
        orange = '#fc8d59'
        yellow = '#fee08b'
        lightYellow = '#ffffbf'
        limeGreen = '#e6f598'
        green = '#99d594'
        blue = '#3288bd'

        # ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
        colors = list(mcolors.TABLEAU_COLORS)

        return colors

        # # diverging - right-most option
        # if numDivisions == 6:
        #     return [red, orange, yellow, limeGreen, green, blue]
        # elif numDivisions == 7:
        #     return [red, orange, yellow, lightYellow, limeGreen, green, blue]
        
        # # diverging - 2nd right-most option
        # red = '#d73027'
        # lightGreen1 = '#d9ef8b'
        # lightGreen2 = '#91cf60'
        # green = '#1a9850'

        # if numDivisions == 6:
        #     return [red, orange, yellow, lightGreen1, lightGreen2, green]
        # elif numDivisions == 7:
        #     return [red, orange, yellow, lightYellow, lightGreen1, lightGreen2, green]

    

    @staticmethod
    def paramNameToAxisLabel(paramName, averageSamples=True):
        if paramName == 'proj':
            return 'Projected out observed nodes (%)'
        elif paramName == 'u_clique':
            return 'pb'
        elif paramName == 'pd':
            return 'pd: Probability for adding directed edges'
        elif paramName == 'pb':
            return 'pb: Probability for adding bidirected edges'
        elif paramName == 'ivCI':
            return 'Number of vacuous CIs'
        elif paramName == 'n':
            # if averageSamples:
            #     return 'Average number of nodes'
            # else:
            return 'Number of nodes'
        elif paramName == 'm':
            # if averageSamples:
            #     return 'Average number of edges'
            # else:
            return 'Number of edges'
        elif paramName == 'md':
            # if averageSamples:
            #     return 'Average number of directed edges'
            # else:
            return 'md: Number of directed edges'
        elif paramName == 'mb':
            # if averageSamples:
            #     return 'Average number of bidirected edges'
            # else:
            return 'mu: Number of bidirected edges'
        elif paramName == 's':
            # if averageSamples:
            #     return 'Average s'
            # else:
            return 's: size of the largest c-component'
        elif paramName == 'runtime':
            # if averageSamples:
            #     return 'Average runtime in seconds'
            # else:
            return 'Runtime in seconds'
        elif paramName == 'CI':
            # if averageSamples:
            #     return 'Average number of CIs'
            # else:
            return 'Number of non-vacuous CIs'
        elif paramName == 'S':
            # if averageSamples:
            #     return 'Average number of ancestral sets'
            # else:
            return 'Number of ancestral sets'
        elif paramName == 'Splus':
            # if averageSamples:
            #     return 'Average number of maximal ancestral sets'
            # else:
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
                measurements = list(map(lambda t: np.nan if t.strip() == '-' else eu.durationStringToSeconds(t), line))
            else:
                measurements = list(map(lambda x: np.nan if x.strip() == '-' else int(x), line))

            paramsCollection[collectionIndex].extend(measurements)

        data = {
            'numSamples': numSamples
        }

        for i in range(len(paramNames)):
            data[paramNames[i]] = np.array(paramsCollection[i])
        
        return data
import sys
import csv

import matplotlib.pyplot as plt
import numpy as np

from src.experiment.experiment_utils import ExperimentUtils as eu


def parseData(lines):
    u30_s = []
    u30_CIs = []
    u30_runtime = []
    u50_s = []
    u50_CIs = []
    u50_runtime = []

    for line in lines:
        s = line[0]
        u30_s.append(int(s))
        s = line[3]
        u50_s.append(int(s))

        CIsize = line[1]
        u30_CIs.append(int(CIsize))
        CIsize = line[4]
        u50_CIs.append(int(CIsize))

        runtime = eu.durationStringToSeconds(line[2])
        u30_runtime.append(runtime)
        runtime = eu.durationStringToSeconds(line[5])
        u50_runtime.append(runtime)

    data = {
        'u30': {
            's': np.array(u30_s),
            'CI': np.array(u30_CIs),
            'runtime': np.array(u30_runtime),
        },
        'u50': {
            's': np.array(u50_s),
            'CI': np.array(u50_CIs),
            'runtime': np.array(u50_runtime),
        }
    }

    return data

def drawPlot(data):
    u30_s = data['u30']['s']
    u30_CIs = data['u30']['CI']
    u30_runtime = data['u30']['runtime']
    u50_s = data['u50']['s']
    u50_CIs = data['u50']['CI']
    u50_runtime = data['u50']['runtime']

    u30Label = 'U 30'
    u50Label = 'U 50'
    blueColor = '#2D7BB1'
    greenColor = '#5CB769'
    labelFontsize = 16
    plt.xlabel('s size', fontsize=labelFontsize)

    selectPlot = 's_CI'
    # selectPlot = 's_runtime'
    # selectPlot = 'CI_runtime'

    if selectPlot == 's_CI':
        plt.scatter(u30_s, u30_CIs, color=blueColor, label=u30Label)
        plt.scatter(u50_s, u50_CIs, color=greenColor, label=u50Label)

        plt.ylabel('Number of CIs', fontsize=labelFontsize)
    elif selectPlot == 's_runtime':
        plt.scatter(u30_s, u30_runtime, color=blueColor, label=u30Label)
        plt.scatter(u50_s, u50_runtime, color=greenColor, label=u50Label)

        # plt.yscale('log')

        plt.ylabel('Runtime in seconds', fontsize=labelFontsize)
    elif selectPlot == 'CI_runtime':
        plt.scatter(u30_CIs, u30_runtime, color=blueColor, label=u30Label)
        plt.scatter(u50_CIs, u50_runtime, color=greenColor, label=u50Label)

        plt.xlabel('Number of CIs', fontsize=labelFontsize)
        plt.ylabel('Runtime in seconds', fontsize=labelFontsize)

    plt.legend()
    plt.show()

if __name__ == '__main__':

    # read arguments
    if len(sys.argv) != 2:
        print('Please specify input file path (e.g., u30.csv).')

        sys.exit()

    filePath = sys.argv[1]

    try:
        with open(filePath, 'r') as f:
            r = csv.reader(f)
            lines = list(r)

            data = parseData(lines)
            drawPlot(data)

            f.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)
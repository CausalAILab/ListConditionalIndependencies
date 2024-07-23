import sys
import csv
import datetime
import time

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def durationStringToSeconds(runtime):
    # convert durating string '00:00:00' to seconds
    x = time.strptime(runtime,'%H:%M:%S')
    seconds = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()

    # round up to avoid undefined value in log-log plot
    if seconds == 0.0:
        seconds = seconds + 1

    return seconds

def parseData(lines):
    ssCollection = []
    CIsizeCollection = []
    runtimeCollection = []

    numSamples = len(lines[0])

    for i in range(len(lines)):
        line = lines[i]

        # s
        if i % 3 == 0:
            ss = list(map(lambda s: int(s), line))
            ssCollection.extend(ss)
        # CI size
        elif i % 3 == 1:
            CIsizes = list(map(lambda ci: int(ci), line))
            CIsizeCollection.extend(CIsizes)
        # runtime
        elif i % 3 == 2:
            runtimes = list(map(lambda t: durationStringToSeconds(t), line))
            runtimeCollection.extend(runtimes)

    data = {
        's': np.array(ssCollection),
        'CI': np.array(CIsizeCollection),
        'runtime': np.array(runtimeCollection),
        'numSamples': numSamples
    }

    return data

def drawPlot(data):
    ss = data['s']
    CIsizes = data['CI']
    runtimes = data['runtime']

    numDivisions = 10
    numSamples = data['numSamples']

    listciLabel = 'ListCI'
    blueColor = '#2D7BB1'
    # greenColor = '#5CB769'
    labelFontsize = 16

    # ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    colors = list(mcolors.TABLEAU_COLORS)

    # selectPlot = 's_CI'
    # selectPlot = 's_runtime'
    # selectPlot = 'CI_runtime'
    selectPlot = 'proj_CI'
    # selectPlot = 'proj_runtime'

    plotAllInOne = False

    if selectPlot == 's_CI':
        plt.scatter(ss, CIsizes, color=blueColor, label=listciLabel)

        plt.xlabel('s size', fontsize=labelFontsize)
        plt.ylabel('Number of CIs', fontsize=labelFontsize)
    elif selectPlot == 's_runtime':
        plt.scatter(ss, runtimes, color=blueColor, label=listciLabel)

        # plt.yscale('log')

        plt.xlabel('s size', fontsize=labelFontsize)
        plt.ylabel('Runtime in seconds', fontsize=labelFontsize)
    elif selectPlot == 'CI_runtime':
        if plotAllInOne:
            plt.scatter(CIsizes, runtimes, color=blueColor, label=listciLabel)
        else:
            for i in range(numDivisions):
                plt.scatter(CIsizes[i * numSamples : ((i+1) * numSamples)-1], runtimes[i * numSamples : ((i+1) * numSamples)-1], color=colors[i], label='Projected (' + str(i+1) + '0%)')

        plt.xscale('log')

        plt.xlabel('Number of CIs', fontsize=labelFontsize)
        plt.ylabel('Runtime in seconds', fontsize=labelFontsize)
    elif selectPlot == 'proj_CI':
        xData = []
        yData = []

        for i in range(numDivisions):
            xData.append(i * 10)
            CIsize = CIsizes[i * numSamples : ((i+1) * numSamples)-1]
            yData.append(round(sum(CIsize) / numSamples, 3))

        plt.scatter(xData, yData, color=blueColor)
        plt.xlabel('Projected observed nodes (%)', fontsize=labelFontsize)
        # plt.xlabel('Ratio of bidirected edges (%)', fontsize=labelFontsize)
        plt.ylabel('Average number of CIs', fontsize=labelFontsize)
    elif selectPlot == 'proj_runtime':
        xData = []
        yData = []

        for i in range(numDivisions):
            xData.append(i * 10)
            runtime = runtimes[i * numSamples : ((i+1) * numSamples)-1]
            yData.append(round(sum(runtime) / numSamples, 3))

        plt.scatter(xData, yData, color=blueColor)
        plt.xlabel('Projected observed nodes (%)', fontsize=labelFontsize)
        plt.ylabel('Average runtime in seconds', fontsize=labelFontsize)

    # plt.legend()
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
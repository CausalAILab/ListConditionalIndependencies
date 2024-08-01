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

    xData = []
    yData = []

    # if set to true, get average of numSamples, then plot a dot per division
    # otherwise, plot all individual samples
    plotAveragedSamples = True

    if selectPlot == 's_CI':
        if plotAveragedSamples:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)-1
                sSamples = ss[startIndex : endIndex]
                averageS = int(sum(sSamples) / numSamples)
                xData.append(averageS)

                CIsize = CIsizes[startIndex : endIndex]
                averageCIsize = round(sum(CIsize) / numSamples, 3)
                yData.append(averageCIsize)

            plt.scatter(xData, yData, color=blueColor)

            yLabel = 'Average number of CIs'
        else:
            plt.scatter(ss, CIsizes, color=blueColor)
            
            # n = 10
            # m = n * 1.5
            # mMax = n*(n-1) / 2

            # for i in range(numDivisions):
            #     startIndex = i * numSamples
            #     endIndex = ((i+1) * numSamples)-1
            #     mb = int(m * (i * 0.1))
            #     md = m - mb
            #     p1 = round(md / mMax, 3)
            #     p2 = round(mb / mMax, 3)
            #     label = 'md (p1) = ' + str(md) + ' (' + str(p1) + '), mb (p2) = ' + str(mb) + ' (' + str(p2) + ')'
            #     # label = 'mb (p2) = ' + str(mb) + '(' + str(p2) + ')'
            #     plt.scatter(ss[startIndex : endIndex], CIsizes[startIndex : endIndex], color=colors[i], label=label)

            yLabel = 'Number of CIs'

        xLabel = 's'

        plt.xlabel(xLabel, fontsize=labelFontsize)
        plt.ylabel(yLabel, fontsize=labelFontsize)
    elif selectPlot == 's_runtime':
        plt.scatter(ss, runtimes, color=blueColor, label=listciLabel)

        # plt.yscale('log')

        plt.xlabel('s', fontsize=labelFontsize)
        plt.ylabel('Runtime in seconds', fontsize=labelFontsize)
    elif selectPlot == 'CI_runtime':
        if plotAveragedSamples:
            plt.scatter(CIsizes, runtimes, color=blueColor, label=listciLabel)

            yLabel = 'Average runtime in seconds'
        else:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)-1

                yLabel = 'Projected (' + str(i+1) + '0%)'
                plt.scatter(CIsizes[startIndex : endIndex], runtimes[startIndex : endIndex], color=colors[i], label=yLabel)

            yLabel = 'Runtime in seconds'

        plt.xscale('log')

        xLabel = 'Number of CIs'

        plt.xlabel(xLabel, fontsize=labelFontsize)
        plt.ylabel(yLabel, fontsize=labelFontsize)
    elif selectPlot == 'proj_CI':
        if plotAveragedSamples:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)-1
                xData.append(i * 10)

                CIsize = CIsizes[startIndex : endIndex]
                averageCIsize = round(sum(CIsize) / numSamples, 3)
                yData.append(averageCIsize)

            plt.scatter(xData, yData, color=blueColor)
            # plt.plot(xData, yData, linestyle='--', marker='o', color=blueColor)
            # plt.errorbar(xData, yData, yerr=[yLower,yUpper], capsize=5, linestyle='--', marker='o', color=blueColor)

            yLabel = 'Average number of CIs'
        else:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)-1

                label = 'Projected (' + str(i+1) + '0%)'
                plt.scatter([i * 10] * numSamples, CIsizes[startIndex : endIndex], color=colors[i], label=label)
            
            yLabel = 'Number of CIs'

        xLabel = 'Projected observed nodes (%)'
        # xLabel = 'Ratio of bidirected edges (%)'
        # xLabel = '% of bidirected edges in a clique'

        plt.xlabel(xLabel, fontsize=labelFontsize)
        plt.ylabel(yLabel, fontsize=labelFontsize)
    elif selectPlot == 'proj_runtime':
        if plotAveragedSamples:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)-1
                xData.append(i * 10)

                runtime = runtimes[startIndex : endIndex]
                averageRuntime = round(sum(runtime) / numSamples, 3)
                yData.append(averageRuntime)

            # plt.scatter(xData, yData, color=blueColor)
            plt.plot(xData, yData, linestyle='--', marker='o', color=blueColor)
            # plt.errorbar(xData, yData, yerr=[yLower,yUpper], capsize=5, linestyle='--', marker='o', color=blueColor)

            yLabel = 'Average runtime in seconds'
        else:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)-1

                label = 'Projected (' + str(i+1) + '0%)'
                plt.scatter([i * 10] * numSamples, runtimes[startIndex : endIndex], color=colors[i], label=label)
            
            yLabel = 'Runtime in seconds'

        xLabel = 'Projected observed nodes (%)'
        # xLabel = 'Ratio of bidirected edges (%)'
        # xLabel = '% of bidirected edges in a clique'

        plt.xlabel(xLabel, fontsize=labelFontsize)
        plt.ylabel(yLabel, fontsize=labelFontsize)

    # plt.legend()
    plt.show()

def getBoundaryValues(samples):
    lower = np.quantile(samples, 0.25)
    upper = np.quantile(samples, 0.75)

    return (lower,upper)

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
import sys
import csv

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from src.experiment.experiment_utils import ExperimentUtils as eu


def parseGraphSizeData(lines):
    nCollection = []
    mCollection = []
    mdCollection = []
    mbCollection = []

    numSamples = len(lines[0])

    mSizes = []

    for i in range(len(lines)):
        line = lines[i]

        # n
        if i % 3 == 0:
            ns = list(map(lambda n: int(n), line))
            nCollection.extend(ns)
        # m
        elif i % 3 == 1:
            ms = list(map(lambda m: int(m), line))
            mCollection.extend(ms)

            mSizes = ms
        # mb
        elif i % 3 == 2:
            mbs = list(map(lambda mb: int(mb), line))
            mbCollection.extend(mbs)

            for i in range(len(mbs)):
                md = mSizes[i] - mbs[i]
                mdCollection.append(md)

    data = {
        'n': np.array(nCollection),
        'm': np.array(mCollection),
        'md': np.array(mdCollection),
        'mb': np.array(mbCollection),
        'numSamples': numSamples
    }

    return data

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
            runtimes = list(map(lambda t: eu.durationStringToSeconds(t), line))
            runtimeCollection.extend(runtimes)

    data = {
        's': np.array(ssCollection),
        'CI': np.array(CIsizeCollection),
        'runtime': np.array(runtimeCollection),
        'numSamples': numSamples
    }

    return data

def drawPlot(data, gsData):
    ss = data['s']
    CIsizes = data['CI']
    runtimes = data['runtime']

    numDivisions = 10
    numSamples = data['numSamples']

    ns = gsData['n']
    ms = gsData['m']
    mds = gsData['md']
    mbs = gsData['mb']
    gsNumSamples = gsData['numSamples']

    listciLabel = 'ListCI'
    blueColor = '#2D7BB1'
    # greenColor = '#5CB769'
    labelFontsize = 16

    # ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    colors = list(mcolors.TABLEAU_COLORS)

    # selectPlot = 's_CI'
    # selectPlot = 's_runtime'
    # selectPlot = 'CI_runtime'
    # selectPlot = 'proj_CI'
    # selectPlot = 'proj_runtime'
    selectPlot = 'proj_s'

    xData = []
    yData = []

    # if set to true, get average of numSamples, then plot a dot per division
    # otherwise, plot all individual samples
    plotAveragedSamples = True

    if selectPlot == 's_CI':
        if plotAveragedSamples:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)
                sSamples = ss[startIndex : endIndex]
                averageS = int(sum(sSamples) / numSamples)
                xData.append(averageS)

                CIsize = CIsizes[startIndex : endIndex]
                averageCIsize = round(sum(CIsize) / numSamples, 3)
                yData.append(averageCIsize)

                # print edges info
                gsStartIndex = i * gsNumSamples
                gsEndIndex = ((i+1) * gsNumSamples)

                n = ns[gsStartIndex]
                mdSamples = mds[gsStartIndex : gsEndIndex]
                mbSamples = mbs[gsStartIndex : gsEndIndex]

                mMax = n*(n-1) / 2

                md = int(np.average(mdSamples))
                mb = int(np.average(mbSamples))
                p1 = round(md / mMax, 3)
                p2 = round(mb / mMax, 3)
                label = 'n: ' + str(n) +  ', md(p1): ' + str(md) + ' (' + str(p1) + '), mb(p2): ' + str(mb) + ' (' + str(p2) + ')'
                plt.scatter([averageS], [averageCIsize], color=colors[i], label=label)

            # plt.scatter(xData, yData, color=blueColor)

            xLabel = 'Average s'
            yLabel = 'Average number of CIs'

            plt.legend()
        else:
            # plt.scatter(ss, CIsizes, color=blueColor)

            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)

                gsStartIndex = i * gsNumSamples
                gsEndIndex = ((i+1) * gsNumSamples)

                n = ns[gsStartIndex]
                mdSamples = mds[gsStartIndex : gsEndIndex]
                mbSamples = mbs[gsStartIndex : gsEndIndex]

                mMax = n*(n-1) / 2

                md = int(np.average(mdSamples))
                mb = int(np.average(mbSamples))
                p1 = round(md / mMax, 3)
                p2 = round(mb / mMax, 3)
                label = 'n = ' + str(n) +  ', md (p1) = ' + str(md) + ' (' + str(p1) + '), mb (p2) = ' + str(mb) + ' (' + str(p2) + ')'
                # label = 'mb (p2) = ' + str(mb) + '(' + str(p2) + ')'
                plt.scatter(ss[startIndex : endIndex], CIsizes[startIndex : endIndex], color=colors[i], label=label)

            xLabel = 's'
            yLabel = 'Number of CIs'

            plt.legend()

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
                endIndex = ((i+1) * numSamples)

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
                endIndex = ((i+1) * numSamples)
                xData.append(i * 10)

                CIsize = CIsizes[startIndex : endIndex]
                averageCIsize = round(sum(CIsize) / numSamples, 3)
                yData.append(averageCIsize)

            # plt.scatter(xData, yData, color=blueColor)
            plt.plot(xData, yData, linestyle='--', marker='o', color=blueColor)
            # plt.errorbar(xData, yData, yerr=[yLower,yUpper], capsize=5, linestyle='--', marker='o', color=blueColor)

            yLabel = 'Average number of CIs'
        else:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)

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
                endIndex = ((i+1) * numSamples)
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
                endIndex = ((i+1) * numSamples)

                label = 'Projected (' + str(i+1) + '0%)'
                plt.scatter([i * 10] * numSamples, runtimes[startIndex : endIndex], color=colors[i], label=label)
            
            yLabel = 'Runtime in seconds'

        xLabel = 'Projected observed nodes (%)'
        # xLabel = 'Ratio of bidirected edges (%)'
        # xLabel = '% of bidirected edges in a clique'

        plt.xlabel(xLabel, fontsize=labelFontsize)
        plt.ylabel(yLabel, fontsize=labelFontsize)
    elif selectPlot == 'proj_s':
        if plotAveragedSamples:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)
                xData.append(i * 10)

                sSamples = ss[startIndex : endIndex]
                averageS = round(sum(sSamples) / numSamples, 3)
                yData.append(averageS)

            # plt.scatter(xData, yData, color=blueColor)
            plt.plot(xData, yData, linestyle='--', marker='o', color=blueColor)
            # plt.errorbar(xData, yData, yerr=[yLower,yUpper], capsize=5, linestyle='--', marker='o', color=blueColor)

            yLabel = 's'
        else:
            for i in range(numDivisions):
                startIndex = i * numSamples
                endIndex = ((i+1) * numSamples)

                label = 'Projected (' + str(i+1) + '0%)'
                plt.scatter([i * 10] * numSamples, ss[startIndex : endIndex], color=colors[i], label=label)

            yLabel = 's'

        xLabel = 'Projected observed nodes (%)'
        # xLabel = 'Ratio of bidirected edges (%)'
        # xLabel = '% of bidirected edges in a clique'

        plt.xlabel(xLabel, fontsize=labelFontsize)
        plt.ylabel(yLabel, fontsize=labelFontsize)

    # plt.legend()
    plt.show()

if __name__ == '__main__':

    # read arguments
    if len(sys.argv) != 3:
        print('Please specify input file path (e.g., u30.csv).')

        sys.exit()

    filePath = sys.argv[1]
    graphSizeFilePath = sys.argv[2]

    try:
        with open(filePath, 'r') as f:
            r = csv.reader(f)
            lines = list(r)

            data = parseData(lines)

            with open(graphSizeFilePath, 'r') as fg:
                r = csv.reader(fg)
                gsLines = list(r)

                gsData = parseGraphSizeData(gsLines)

                drawPlot(data, gsData)

                fg.close()
            f.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)
import sys
import csv

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.optimize import curve_fit
from scipy.interpolate import make_interp_spline

from src.testable_implications.ci_defs import algMap, algListGMP, algListCIBF, algListCI
from src.testable_implications.ci_utils import ConditionalIndependenceUtils as cu


def func(x, a, b, c):
    return a * np.exp(b * x) + c

def funcLog(x, a, b):
    return a + b * np.log(x)

def paramNameToAxisLabel(paramName, averageSamples):
    if paramName == 'proj':
        return 'Projected observed nodes (%)'
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


def parseData(alg, lines):
    paramNames = []

    if alg == algListGMP.id_:
        paramNames = algListGMP.params
    elif alg == algListCIBF.id_:
        paramNames = algListCIBF.params
    elif alg == algListCI.id_:
        paramNames = algListCI.params

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


def drawPlot(algs, datas, specs):
    labelFontsize = specs['labelFontsize']
    numDivisions = specs['numDivisions']
    averageSamples = specs['averageSamples']
    smoothCurve = specs['smoothCurve']
    doExpRegression = specs['doExpRegression']
    xParam = specs['x']
    yParam = specs['y']
    
    # ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    colors = list(mcolors.TABLEAU_COLORS)

    plt.figure(dpi=300)

    redColor = '#f00'
    blueColor = '#2D7BB1'
    greenColor = '#5CB769'

    for i in range(len(algs)):
        algId  = algs[i]
        data = datas[i]

        currentAlg = algMap[algId]

        if algId == algListGMP.id_:
            plotColor = redColor
        elif algId == algListCIBF.id_:
            plotColor = greenColor
        elif algId == algListCI.id_:
            plotColor = blueColor

        numSamples = data['numSamples']

        paramsToProcess = [xParam, yParam]
        dataPoints = [[], []]

        exceptionParams = ['S', 'Splus']

        if xParam in exceptionParams or yParam in exceptionParams:
            if algId != algListCIBF.id_:
                continue
        
        for k in range(len(paramsToProcess)):
            paramAxisName = paramsToProcess[k]

            if paramAxisName == 'proj':
                for j in range(numDivisions):
                    startIndex = j * numSamples
                    endIndex = ((j+1) * numSamples)

                    if averageSamples:
                        dataPoints[k].append(j * 10)
                    else:
                        dataPoints[k].extend([j * 10] * numSamples)
            else:
                axisDataPoints = data[paramAxisName]

                if averageSamples:
                    for j in range(numDivisions):
                        startIndex = j * numSamples
                        endIndex = ((j+1) * numSamples)
                        samples = axisDataPoints[startIndex : endIndex]
                        average = round(sum(samples) / numSamples, 3)
                        dataPoints[k].append(average)
                else:
                    dataPoints[k] = axisDataPoints.tolist()
        
        xData = dataPoints[0]
        yData = dataPoints[1]
        
        if smoothCurve:
            # in case of 'S', reverse the list
            if xParam == 'S':
                xData.reverse()
            if yParam == 'S':
                yData.reverse()
            splineModel = make_interp_spline(xData, yData)
            xSplines = np.linspace(min(xData), max(xData), 500)
            ySplines = splineModel(xSplines)
            xData = xSplines
            yData = ySplines

        if averageSamples:
            # plt.scatter(xData, yData, color=plotColor, label=currentAlg.name)
            plt.plot(xData, yData, linestyle='--', color=plotColor, label=currentAlg.name)
            # plt.plot(xData, yData, linestyle='--', marker='o', color=plotColor, label=currentAlg.name)
            # plt.errorbar(xData, yData, yerr=[yLower,yUpper], capsize=5, linestyle='--', marker='o', color=plotColor)

            # for j in range(numDivisions):
            #     if j >= 2 and j <= 6:
            #         label = 'Projected (' + str(j+1) + '0%)'
            #         plt.scatter(xData[j], yData[j], color=colors[j], label=label)
            #     else:
            #         label = 'The remaining'
            #         plt.scatter(xData[j], yData[j], color=plotColor, label=label)

            # plt.yscale('log')
        else:
            plt.scatter(xData, yData, color=plotColor, label=currentAlg.name)

            # choose this option to color paramters differently for each U
            # for j in range(numDivisions):
            #     startIndex = j * numSamples
            #     endIndex = ((j+1) * numSamples)

            #     # label = 'Projected (' + str(j+1) + '0%)'
            #     # plt.scatter(xData[startIndex : endIndex], yData[startIndex : endIndex], color=colors[j], label=label)

            #     if j >= 1 and j <= 5:
            #         label = 'Projected (' + str(j+1) + '0%)'
            #         plt.scatter(xData[startIndex : endIndex], yData[startIndex : endIndex], color=colors[j], label=label)
            #     else:
            #         if j == 6:
            #             label = 'The remaining'
            #         else:
            #             label = ''
            #         plt.scatter(xData[startIndex : endIndex], yData[startIndex : endIndex], color=plotColor, label=label)

                # plt.yscale('log')
        
        xLabel = paramNameToAxisLabel(xParam, averageSamples)
        yLabel = paramNameToAxisLabel(yParam, averageSamples)

        plt.xlabel(xLabel, fontsize=labelFontsize)
        plt.ylabel(yLabel, fontsize=labelFontsize)
        
        if algId == algListCIBF.id_:
            if doExpRegression:
                xData.reverse()
                yData.reverse()
                npX = np.array(xData)
                npY = np.array(yData)

                # popt, pcov = curve_fit(lambda t,a,b: a*np.exp(b*t), np.array(xData), np.array(yData))
                # popt, pcov = curve_fit(func, npX, npY)
                # plt.plot(npX, func(npX, *popt), 'r-', label="Fitted Curve")

                # log
                popt, pcov = curve_fit(funcLog, npX, npY)
                plt.plot(npX, funcLog(npX, *popt), 'r-', label="Fitted Curve")

                # popt, pcov = curve_fit(funcLog, npY, npX)
                # plt.plot(funcLog(npY, *popt), npY, 'r-', label="Fitted Curve")
                
                # popt, pcov = curve_fit(func, xData, yData)
                # plt.plot(xData, func(xData, *popt), 'r-', label="Fitted Curve")

                # polyfit
                # fit = np.polyfit(npX, npY, 1)
                # fit = np.append(fit, 0)
                # plt.plot(npX, func(npX, *fit), 'r-', label="Fitted Curve")

                # fit = np.polyfit(np.log(npX), npY, 1)
                # plt.plot(npX, funcLog(npX, *fit), 'r-', label="Fitted Curve")

    setAxisBoundaries()

    plt.legend()
    # plt.show()
    plt.savefig('a.pdf')


def setAxisBoundaries():
    # x-axis for proj
    # plt.xticks(range(0,100,10))
    # x-axis for s
    # plt.xticks(range(0,22,2))

    # y-axis for s
    # plt.yticks(range(0,22,2))

    return


if __name__ == '__main__':

    # read arguments
    # assumption: 2nd arg is the path to a file containing ListCI measurements.
    # 3rd arg (if exists) is for ListCIBF.
    # 4nd arg (if exists) is for ListGMP.
    argLength = len(sys.argv)

    if argLength < 2 or argLength > 4:
        print('Please specify input file paths correctly.')

        sys.exit()

    filePathListCI = sys.argv[1]

    specs = {
        'x': 's',
        'y': 'runtime',
        'numDivisions': 10,
        'labelFontsize': 16,
        'averageSamples': False,
        'smoothCurve': False,
        'doExpRegression': False
    }

    try:
        with open(filePathListCI, 'r') as fci:
            r = csv.reader(fci)
            lines = list(r)

            dataListCI = parseData(algListCI.id_, lines)

            if argLength <= 2:
                drawPlot([algListCI.id_], [dataListCI], specs)
            else:
                filePathListCIBF = sys.argv[2]

                with open(filePathListCIBF, 'r') as fcibf:
                    r = csv.reader(fcibf)
                    lines = list(r)

                    dataListCIBF = parseData(algListCIBF.id_, lines)

                    if argLength <= 3:
                        drawPlot([algListCI.id_, algListCIBF.id_], [dataListCI, dataListCIBF], specs)
                    else:
                        filePathListGMP = sys.argv[3]

                        with open(filePathListGMP, 'r') as fgmp:
                            r = csv.reader(fgmp)
                            lines = list(r)

                            dataListGMP = parseData(algListGMP.id_, lines)
                            drawPlot([algListCI.id_, algListCIBF.id_, algListGMP.id_], [dataListCI, dataListCIBF, dataListGMP], specs)

                            fgmp.close()

                    fcibf.close()

            fci.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)
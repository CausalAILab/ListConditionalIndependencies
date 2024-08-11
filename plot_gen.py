import sys
import csv

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
# from scipy.optimize import curve_fit
from scipy.interpolate import make_interp_spline

from src.testable_implications.ci_defs import algMap, algListGMP, algListCIBF, algListCI
from src.experiment.plot_utils import PlotUtils as pu


def func(x, a, b, c):
    return a * np.exp(b * x) + c

def funcLog(x, a, b):
    return a + b * np.log(x)

def drawPlot(algs, datas, specs):
    labelFontsize = specs['labelFontsize']
    numDivisions = specs['numDivisions']
    averageSamples = specs['averageSamples']
    smoothCurve = specs['smoothCurve']
    showmdmb = specs['showmdmb']
    xParam = specs['x']
    yParam = specs['y']
    imageFormat = specs['imageFormat']
    plotStyle = specs['plotStyle']
    
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
            elif paramAxisName == 'u_clique':
                for j in range(numDivisions):
                    startIndex = j * numSamples
                    endIndex = ((j+1) * numSamples)

                    if averageSamples:
                        dataPoints[k].append(j * 0.1)
                    else:
                        dataPoints[k].extend([j * 0.1] * numSamples)
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
            if plotStyle == 'scatter':
                plt.scatter(xData, yData, color=plotColor, label=currentAlg.name)
            elif plotStyle == 'line':
                plt.plot(xData, yData, linestyle='--', color=plotColor, label=currentAlg.name)
            elif plotStyle == 'line_scatter':
                plt.plot(xData, yData, linestyle='--', marker='o', color=plotColor, label=currentAlg.name)
            # plt.errorbar(xData, yData, yerr=[yLower,yUpper], capsize=5, linestyle='--', marker='o', color=plotColor)

            # main overleaf - plot 5,6
            # for j in range(numDivisions):
            #     if j >= 2 and j <= 6:
            #         label = 'Projected (' + str(j+1) + '0%)'
            #         plt.scatter(xData[j], yData[j], color=colors[j], label=label)
            #     else:
            #         label = 'The remaining'
            #         plt.scatter(xData[j], yData[j], color=plotColor, label=label)

            # plt.yscale('log')
        else:
            if showmdmb:
                for j in range(numDivisions):
                    startIndex = j * numSamples
                    endIndex = ((j+1) * numSamples)

                    n = data['n'][startIndex]
                    md = data['md'][startIndex]
                    mb = data['mb'][startIndex]

                    # B2/B3: hard-coded
                    # n = 10
                    # m = int(n * 2)
                    # # B2
                    # # md = 0
                    # # mb = int(m * j * 0.1)
                    # # B3
                    # mb = int(m * j * 0.1)
                    # md = m - mb

                    mMax = n*(n-1) / 2
                    pd = round(md / mMax, 3)
                    pb = round(mb / mMax, 3)
                    # label = 'md (pd) = ' + str(md) + ' (' + str(pd) + '), mb (pb) = ' + str(mb) + ' (' + str(pb) + ')'
                    label = 'mb (pb) = ' + str(mb) + ' (' + str(pb) + ')'
                    plt.scatter(xData[startIndex : endIndex], yData[startIndex : endIndex], color=colors[j % len(colors)], label=label)
            else:
                plt.scatter(xData, yData, color=plotColor, label=currentAlg.name)

            # choose this option to color paramters differently for each U
            # for j in range(numDivisions):
            #     startIndex = j * numSamples
            #     endIndex = ((j+1) * numSamples)

            #     label = 'Projected (' + str(j+1) + '0%)'
            #     plt.scatter(xData[startIndex : endIndex], yData[startIndex : endIndex], color=colors[j], label=label)

            # main overleaf, plot 5,6
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
        
        xLabel = pu.paramNameToAxisLabel(xParam, averageSamples)
        yLabel = pu.paramNameToAxisLabel(yParam, averageSamples)

        plt.xlabel(xLabel, fontsize=labelFontsize)
        plt.ylabel(yLabel, fontsize=labelFontsize)
        
    setAxisBoundaries(xParam, yParam)

    plt.legend()
    # plt.show()

    savePlotToFile(imageFormat)    


def setAxisBoundaries(xParam, yParam):
    if xParam == 'proj':
        plt.xticks(range(0,100,10))
    if xParam == 'u_clique':
        ranges = range(0,100,10)
        plt.xticks(list(map(lambda x: x/100.0, ranges)))
    if xParam == 's':
        plt.xticks(range(0,55,5))

    if yParam == 's':
        plt.yticks(range(0,45,5))
    # runtime (timeout = 1h)
    if yParam == 'runtime':
        plt.ylim(0,3600)
        # plt.yscale('log')
    if yParam == 'CI':
        plt.ylim(1,1e7)
        plt.yscale('log')

    return


def savePlotToFile(imageFormat='png'):
    if imageFormat == 'png':
        plt.savefig('a.png')
    elif imageFormat == 'pdf':
        plt.savefig('a.pdf')


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
        'y': 'CI',
        'numDivisions': 10,
        'labelFontsize': 16,
        'plotStyle': 'scatter',
        'imageFormat': 'png',
        'averageSamples': False,
        'showmdmb': True,
        'smoothCurve': False
    }

    try:
        with open(filePathListCI, 'r') as fci:
            r = csv.reader(fci)
            lines = list(r)

            dataListCI = pu.parseData(algListCI.id_, lines)

            if argLength <= 2:
                drawPlot([algListCI.id_], [dataListCI], specs)
            else:
                filePathListCIBF = sys.argv[2]

                with open(filePathListCIBF, 'r') as fcibf:
                    r = csv.reader(fcibf)
                    lines = list(r)

                    dataListCIBF = pu.parseData(algListCIBF.id_, lines)

                    if argLength <= 3:
                        drawPlot([algListCI.id_, algListCIBF.id_], [dataListCI, dataListCIBF], specs)
                    else:
                        filePathListGMP = sys.argv[3]

                        with open(filePathListGMP, 'r') as fgmp:
                            r = csv.reader(fgmp)
                            lines = list(r)

                            dataListGMP = pu.parseData(algListGMP.id_, lines)
                            drawPlot([algListCI.id_, algListCIBF.id_, algListGMP.id_], [dataListCI, dataListCIBF, dataListGMP], specs)

                            fgmp.close()

                    fcibf.close()

            fci.close()
    except IOError:
        line = 'Please specify the input file correctly.'

        print(line)
import sys
import csv

import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.colors as mcolors
from scipy.interpolate import make_interp_spline

from src.testable_implications.ci_defs import algMap, algListGMP, algListCIBF, algListCI
from src.experiment.plot_utils import PlotUtils as pu


def getDataPoints(algId, datas, specs, divisionsToRead=range(0,10)):
    numDivisions = specs['numDivisions']
    averageSamples = specs['averageSamples']
    sort = specs['sort']
    xParam = specs['x']
    yParam = specs['y']

    dataPoints = [[], []]

    for i in range(len(datas)):
        data = datas[i]

        numSamples = data['numSamples']

        axes = [xParam, yParam]

        exceptionParams = ['S', 'Splus']

        if xParam in exceptionParams or yParam in exceptionParams:
            if algId != algListCIBF.id_:
                continue
        
        for k in range(len(axes)):
            paramAxisName = axes[k]

            # handle pd, pb

            if paramAxisName == 'pd' or paramAxisName == 'pb':
                if paramAxisName == 'pd':
                    mDataPoints = data['md']
                elif paramAxisName == 'pb':
                    mDataPoints = data['mb']

                nDataPoints = data['n']

                # how to read n, to compute pd?

                for j in range(numDivisions):
                    if j not in divisionsToRead:
                        continue

                    startIndex = j * numSamples
                    endIndex = ((j+1) * numSamples)

                    n = nDataPoints[startIndex]
                    mMax = int(n * (n-1) / 2)

                    mSamples = mDataPoints[startIndex : endIndex]
                    pSamples = list(map(lambda m: round(m / mMax, 3), mSamples))

                    if averageSamples:
                        average = round(sum(pSamples) / numSamples, 3)
                        dataPoints[k].append(average)
                    else:
                        dataPoints[k].extend(pSamples.tolist())
            else:
                axisDataPoints = data[paramAxisName]

                for j in range(numDivisions):
                    if j not in divisionsToRead:
                        continue

                    startIndex = j * numSamples
                    endIndex = ((j+1) * numSamples)
                    samples = axisDataPoints[startIndex : endIndex]

                    if averageSamples:
                        average = round(sum(samples) / numSamples, 3)
                        dataPoints[k].append(average)
                    else:
                      dataPoints[k].extend(samples.tolist())

    if sort:
        tuples = []

        for i in range(len(dataPoints[0])):
            x = dataPoints[0][i]
            y = dataPoints[1][i]

            tuples.append((x,y))

        tuples.sort(key=lambda tup: tup[0])

        dataPoints[0] = list(map(lambda tup: tup[0], tuples))
        dataPoints[1] = list(map(lambda tup: tup[1], tuples))

    return dataPoints


def drawPlot(algId, dataPoints, specs):
    labelFontsize = specs['labelFontsize']
    averageSamples = specs['averageSamples']
    smoothCurve = specs['smoothCurve']
    plotStyle = specs['plotStyle']
    regression = specs['regression']
    xParam = specs['x']
    yParam = specs['y']

    redColor = '#f00'
    blueColor = '#2D7BB1'
    greenColor = '#5CB769'

    currentAlg = algMap[algId]

    if algId == algListGMP.id_:
        plotColor = redColor
    elif algId == algListCIBF.id_:
        plotColor = greenColor
    elif algId == algListCI.id_:
        plotColor = blueColor
    
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
    
    if plotStyle == 'scatter':
        plt.scatter(xData, yData, color=plotColor, label=currentAlg.name)
    elif plotStyle == 'line':
        plt.plot(xData, yData, linestyle='--', color=plotColor, label=currentAlg.name)
    elif plotStyle == 'line_scatter':
        plt.plot(xData, yData, linestyle='--', marker='o', color=plotColor, label=currentAlg.name)

    xLabel = pu.paramNameToAxisLabel(xParam, averageSamples)
    yLabel = pu.paramNameToAxisLabel(yParam, averageSamples)

    plt.xlabel(xLabel, fontsize=labelFontsize)
    plt.ylabel(yLabel, fontsize=labelFontsize)
        
    setAxisBoundaries(xParam, yParam)


def setAxisBoundaries(xParam, yParam):
    if xParam == 'n':
        plt.xticks(range(0,110,10))
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
        plt.ylim(1,3600)
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
    # graphNames = {
    #     'sm': ['asia', 'cancer', 'earthquake', 'sachs', 'survey'],
    #     'md': ['alarm', 'barley', 'child', 'insurance', 'mildew', 'water'],
    #     'lg': ['hailfinder', 'win95pts']
    # }

    # graphSizes = ['sm', 'md', 'lg']
    # prefixes = ['_ci', '_bf', '_gmp']
    basePath = 'experiments/a_bnlearn'
    extension = '.csv'

    parsedData = dict()
    # parsedData[algListGMP.id_] = []
    # parsedData[algListCIBF.id_] = []
    # parsedData[algListCI.id_] = []

    specs = {
        'x': 's',
        'y': 'CI',
        'numDivisions': 10,
        'labelFontsize': 16,
        'plotStyle': 'scatter',
        'imageFormat': 'png',
        'averageSamples': True,
        'smoothCurve': False
    }

    # for size in graphNames:
    #     names = graphNames[size]

    #     if size == 'sm':
    #         prefixesToCheck = prefixes
    #     elif size == 'md':
    #         prefixesToCheck = prefixes[0:2]
    #     elif size == 'lg':
    #         prefixesToCheck = [prefixes[0]]

    #     for name in names:
    #         for prefix in prefixesToCheck:
    #             filePath = basePath + '/' + size + '/' + name + prefix + extension

    #             try:
    #                 with open(filePath, 'r') as f:
    #                     r = csv.reader(f)
    #                     lines = list(r)

    #                     if prefix == '_ci':
    #                         algId = algListCI.id_
    #                     elif prefix == '_bf':
    #                         algId = algListCIBF.id_
    #                     elif prefix == '_gmp':
    #                         algId = algListGMP.id_
                        
    #                     data = pu.parseData(algId, lines)
    #                     parsedData[algId].append(data)

    #                     f.close()
    #             except:
    #                 line = 'Please specify the input file correctly.'
    #                 print(filePath)

    plt.figure(dpi=300)

    for algId in parsedData:
        datas = parsedData[algId]
        
        dataPoints = getDataPoints(algId, datas, specs)
        drawPlot(algId, dataPoints, specs)

    plt.legend()
    # plt.show()

    savePlotToFile(specs['imageFormat'])
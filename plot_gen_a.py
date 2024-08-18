# import sys
import csv

import numpy as np
# from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
# import matplotlib.colors as mcolors
from scipy.optimize import curve_fit
from scipy.interpolate import make_interp_spline

from src.testable_implications.ci_defs import algMap, algListGMP, algListCIBF, algListCI
from src.experiment.plot_utils import PlotUtils as pu

doPlotCIs = False

def funcExp(x, a, b, c):
    return a * np.exp(b * x) + c

def funcLog(x, a, b):
    return a + b * np.log(x)

def getDataPoints(algId, datas, specs, uIndices=range(0,10)):
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

            if paramAxisName == 'proj':
                for j in range(numDivisions):
                    if j not in uIndices:
                        continue

                    startIndex = j * numSamples
                    endIndex = ((j+1) * numSamples)

                    if averageSamples:
                        dataPoints[k].append(j * 10)
                    else:
                        dataPoints[k].extend([j * 10] * numSamples)
            elif paramAxisName == 'u_clique':
                for j in range(numDivisions):
                    if j not in uIndices:
                        continue

                    startIndex = j * numSamples
                    endIndex = ((j+1) * numSamples)

                    if averageSamples:
                        dataPoints[k].append(j * 0.1)
                    else:
                        dataPoints[k].extend([j * 0.1] * numSamples)
            else:
                axisDataPoints = data[paramAxisName]

                for j in range(numDivisions):
                    if j not in uIndices:
                        continue

                    startIndex = j * numSamples
                    endIndex = ((j+1) * numSamples)
                    samples = axisDataPoints[startIndex : endIndex]

                    # in case for log plots, add epsilon to runtime
                    if paramAxisName == 'runtime':
                        samples = np.array(list(map(lambda t: 1.2 if t <= 1.0 else t, samples)))

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

    global doPlotCIs

    if doPlotCIs:
        if algId == algListCIBF.id_:
            return

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
        splineModel = make_interp_spline(xData, yData)
        xSplines = np.linspace(min(xData), max(xData), 500)
        ySplines = splineModel(xSplines)
        xData = xSplines
        yData = ySplines
    
    # if plotStyle == 'scatter':
    #     plt.scatter(xData, yData, color=plotColor, label=currentAlg.name)
    # elif plotStyle == 'line':
    #     plt.plot(xData, yData, linestyle='--', color=plotColor, label=currentAlg.name)
    # elif plotStyle == 'line_scatter':
    #     plt.plot(xData, yData, linestyle='--', marker='o', color=plotColor, label=currentAlg.name)

    xLabel = pu.paramNameToAxisLabel(xParam, averageSamples)
    yLabel = pu.paramNameToAxisLabel(yParam, averageSamples)

    plt.xlabel(xLabel, fontsize=labelFontsize)
    plt.ylabel(yLabel, fontsize=labelFontsize)

    if regression:
        xArray = np.array(xData)
        yArray = np.array(yData)

        mask = ~np.isnan(xArray) & ~np.isnan(yArray)
        validX = xArray[mask]
        validY = yArray[mask]

        minN = 0
        # use 95 for plot_a
        # use 100 for plot_b
        maxN = 95
        numSamples = 100
        xDots = np.linspace(minN, maxN, numSamples)
        polyModel = np.poly1d(np.polyfit(validX, validY, 1))

        if doPlotCIs:
            if algId == algListGMP.id_:
                minNRegression = 0
                maxNRegression = 10
                indices = np.where(((validX >= minNRegression) & (validX <= maxNRegression)))
                filteredX = validX[indices]
                filteredY = validY[indices]
                popt, pcov = curve_fit(funcExp, filteredX, filteredY)

                # use maxN to a maximum of observed n
                # maxN = 20
                maxN = np.amax(validX)
                xDots = np.linspace(minN, maxN, numSamples)

                plt.plot(xDots, funcExp(xDots, *popt), color=plotColor, label=currentAlg.name)
            elif algId == algListCI.id_:
                # alternating two colors in line
                # plot both ListCIBF + ListCI: [0,35]
                minN = 0
                maxN = 35
                xDots = np.linspace(minN, maxN, numSamples)

                plt.plot(xDots, polyModel(xDots), color=greenColor, linestyle='--', dashes=(10,1), label=algMap[algListCIBF.id_].name)
                plt.plot(xDots, polyModel(xDots), color=plotColor, linestyle='-', dashes=(5,4), label=currentAlg.name)

                # plot only ListCI: [35,80]
                minN = maxN
                # maxN = 80
                maxN = np.amax(validX)
                xDots = np.linspace(minN, maxN, numSamples)
                plt.plot(xDots, polyModel(xDots), color=plotColor, linestyle='-', dashes=(5,4))

                # plt.plot(xDots, polyModel(xDots), color=greenColor, label=algMap[algListCIBF.id_].name)
                # plt.plot(xDots, polyModel(xDots), color=plotColor, label=currentAlg.name)
        else:
            if algId == algListGMP.id_:
                popt, pcov = curve_fit(funcExp, validX, validY)

                # maxN = 10
                maxN = np.amax(validX)
                xDots = np.linspace(minN, maxN, numSamples)

                plt.plot(xDots, funcExp(xDots, *popt), color=plotColor, label=currentAlg.name)
            elif algId == algListCIBF.id_:
                # ListCIBF curve: [0,40]
                minNRegression = 0
                maxNRegression = 40

                indices = np.where(((validX >= minNRegression) & (validX <= maxNRegression)))
                filteredX = validX[indices]
                filteredY = validY[indices]

                # polyModel = np.poly1d(np.polyfit(filteredX, filteredY, 2))
                # plt.plot(xDots, polyModel(xDots), color=plotColor, label=currentAlg.name)

                popt, pcov = curve_fit(funcExp, filteredX, filteredY)

                minN = 0
                # maxN = 50
                maxN = np.amax(validX)
                xDots = np.linspace(minN, maxN, numSamples)

                plt.plot(xDots, funcExp(xDots, *popt), color=plotColor, label=currentAlg.name)
            else:
                # ListCI curve: [0,80]
                minN = 0
                # maxN = 80
                maxN = np.amax(validX)
                xDots = np.linspace(minN, maxN, numSamples)
                plt.plot(xDots, polyModel(xDots), color=plotColor, label=currentAlg.name)
        

def setAxisBoundaries(ax, xParam, yParam):
    if xParam == 'n':
        ranges = range(0,110,10)
        plt.xticks(ranges)

        # labels = list(map(lambda x: str(x), ranges))
        # ax.set_xticklabels(labels, minor=False)
    elif xParam == 'proj':
        plt.xticks(range(0,100,10))
    elif xParam == 'u_clique':
        ranges = range(0,100,10)
        plt.xticks(list(map(lambda x: x/100.0, ranges)))
    elif xParam == 's':
        plt.xticks(range(0,55,5))

    if yParam == 's':
        plt.yticks(range(0,45,5))
    elif yParam == 'runtime':
        # plt.ylim(1,1e5)
        plt.ylim(1,3600)
        plt.yscale('log')
    elif yParam == 'CI':
        plt.ylim(1,1e5)
        # plt.ylim(1,3600)
        plt.yscale('log')


def savePlotToFile(imageFormat='png'):
    if imageFormat == 'png':
        plt.savefig('a.png')
    elif imageFormat == 'pdf':
        plt.savefig('a.pdf')


if __name__ == '__main__':
    graphNames = {
        'sm': ['asia', 'cancer', 'earthquake', 'sachs', 'survey'],
        'md': ['alarm', 'barley', 'child', 'insurance', 'mildew', 'water'],
        'lg': ['hailfinder', 'win95pts']
        # 'lg': ['win95pts']
        # 'lg': []
    }

    graphSizes = ['sm', 'md', 'lg']
    prefixes = ['_ci', '_bf', '_gmp']
    # basePath = 'experiments/a_bnlearn/mac/record_timeout'
    # basePath = 'experiments/a_bnlearn/mac/more_timeout'
    basePath = 'experiments/a_bnlearn/mac/1_10_criterion'
    # basePath = 'experiments/a_bnlearn/gpu'
    extension = '.csv'

    parsedData = dict()
    parsedData[algListGMP.id_] = []
    parsedData[algListCIBF.id_] = []
    parsedData[algListCI.id_] = []

    specs = {
        'x': 'n',
        'y': 'runtime',
        'numDivisions': 10,
        'labelFontsize': 16,
        'plotStyle': 'scatter',
        'imageFormat': 'png',
        'averageSamples': False,
        'smoothCurve': False,
        'sort': False,
        'regression': True
    }

    doPlotCIs = True

    if doPlotCIs:
        specs['y'] = 'CI'

    # 1 means U = 0.1, min = 0, max = 9
    # uIndices = [1,2,3,4,5]
    uIndices = range(0,10)

    for size in graphNames:
        names = graphNames[size]

        if size == 'sm':
            prefixesToCheck = prefixes
        elif size == 'md':
            prefixesToCheck = prefixes[0:2]
        elif size == 'lg':
            prefixesToCheck = [prefixes[0]]
        
        for name in names:
            for prefix in prefixesToCheck:
                filePath = basePath + '/' + size + '/' + name + prefix + extension

                try:
                    with open(filePath, 'r') as f:
                        r = csv.reader(f)
                        lines = list(r)

                        if prefix == '_ci':
                            algId = algListCI.id_
                        elif prefix == '_bf':
                            algId = algListCIBF.id_
                        elif prefix == '_gmp':
                            algId = algListGMP.id_
                        
                        data = pu.parseData(algId, lines)
                        parsedData[algId].append(data)

                        f.close()
                except Exception as e:
                    line = 'Please specify the input file correctly.'
                    # print(filePath)
                    print(e)

    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(1,1,1)

    for algId in parsedData:
        datas = parsedData[algId]
        
        dataPoints = getDataPoints(algId, datas, specs, uIndices)
        drawPlot(algId, dataPoints, specs)

    setAxisBoundaries(ax, specs['x'], specs['y'])

    plt.legend()
    # plt.show()

    savePlotToFile(specs['imageFormat'])
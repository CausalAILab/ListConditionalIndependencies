import sys
import csv

from os import listdir
from os.path import isfile, join

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

from src.testable_implications.ci_defs import algListCI, algListCIBF
from src.experiment.plot_utils import PlotUtils as pu

defaultRounding = 3

numNodes = []

def getDataPoints(data, specs):
    numDivisions = specs['numDivisions']
    averageSamples = specs['averageSamples']
    sort = specs['sort']
    xParam = specs['x']
    yParam = specs['y']
    axes = [xParam, yParam]

    dataPoints = [[], []]
    numSamples = data['numSamples']

    # collect n, assumes n is the same for all samples in one file
    nDataPoints = data['n']
    n = int(nDataPoints[0])

    if not np.isnan(n):
        numNodes.append(n)

    for k in range(len(axes)):
        paramAxisName = axes[k]

        # handle pd, pb
        if paramAxisName == 'pd' or paramAxisName == 'pb':
            if paramAxisName == 'pd':
                mDataPoints = data['md']
            elif paramAxisName == 'pb':
                mDataPoints = data['mb']

            for j in range(numDivisions):
                startIndex = j * numSamples
                endIndex = ((j+1) * numSamples)

                # skip division with nan entries
                n = nDataPoints[startIndex]

                if np.isnan(n):
                    continue

                n = int(n)
                mMax = int(n * (n-1) / 2)

                mSamples = mDataPoints[startIndex : endIndex]
                pSamples = list(map(lambda m: round(m / mMax, defaultRounding), mSamples))

                if averageSamples:
                    average = round(sum(pSamples) / numSamples, defaultRounding)
                    dataPoints[k].append(average)
                else:
                    dataPoints[k].extend(pSamples.tolist())
        # assumes data comes from listCIBF
        elif paramAxisName == 'ivCI':
            for j in range(numDivisions):
                startIndex = j * numSamples
                endIndex = ((j+1) * numSamples)

                masSamples = data['Splus'][startIndex : endIndex]
                ciSamples = data['CI'][startIndex : endIndex]

                if averageSamples:
                    masAverage = round(sum(masSamples) / numSamples, defaultRounding)
                    ciAverage = round(sum(ciSamples) / numSamples, defaultRounding)

                    dataPoints[k].append(masAverage - ciAverage)
                else:
                    invalidCIs = []

                    for i in range(len(ciSamples)):
                        mas = masSamples[i]
                        ci = ciSamples[i]

                        invalidCIs.append(mas - ci)

                    dataPoints[k].extend(invalidCIs)
        else:
            axisDataPoints = data[paramAxisName]

            for j in range(numDivisions):
                startIndex = j * numSamples
                endIndex = ((j+1) * numSamples)

                # skip division with nan entries
                n = nDataPoints[startIndex]

                if np.isnan(n):
                    continue

                samples = axisDataPoints[startIndex : endIndex]

                if averageSamples:
                    average = round(sum(samples) / numSamples, defaultRounding)
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


def drawPlot(plotType, datas, specs):
    labelFontsize = specs['labelFontsize']
    averageSamples = specs['averageSamples']
    smoothCurve = specs['smoothCurve']
    plotStyle = specs['plotStyle']
    # regression = specs['regression']
    numColorDivisions = specs['numColorDivisions']
    xParam = specs['x']
    yParam = specs['y']

    colors = pu.getColorPalette(numColorDivisions)

    for i in range(len(datas)):
        dataPoints = datas[i]
    
        xData = dataPoints[0]
        yData = dataPoints[1]
        
        if smoothCurve:
            # filter valid data points
            xArray = np.array(xData)
            yArray = np.array(yData)

            mask = ~np.isnan(xArray) & ~np.isnan(yArray)

            validX = xArray[mask]
            validY = yArray[mask]

            splineModel = make_interp_spline(validX, validY)
            xSplines = np.linspace(min(validX), max(validX), 500)
            ySplines = splineModel(xSplines)

            xData = xSplines
            yData = ySplines

        color = colors[i % len(colors)]

        # custom label: n = x
        n = numNodes[i]
        label = 'n = ' + str(n)

        # n20r, n25r, n30r
        # if i == 3 or i == 5 or i == 7:
        #     label = None

        # if i == 2 or i == 3:
        #     color = colors[2]
        # if i == 4 or i == 5:
        #     color = colors[3]
        # if i == 6 or i == 7:
        #     color = colors[4]

        # if yParam == 'ivCI':
        #     label = 'n = ' + str(n) + ' (invalid CIs)'
        
        if plotStyle == 'scatter':
            if label is not None:
                plt.scatter(xData, yData, color=color, label=label)
            else:
                plt.scatter(xData, yData, color=color)
        elif plotStyle == 'line_solid':
            if label is not None:
                plt.plot(xData, yData, linestyle='solid', color=color, label=label)
            else:
                plt.plot(xData, yData, linestyle='solid', color=color)
        elif plotStyle == 'line_dotted':
            if label is not None:
                plt.plot(xData, yData, linestyle='dotted', color=color, label=label)
            else:
                plt.plot(xData, yData, linestyle='dotted', color=color)
        elif plotStyle == 'line_scatter':
            if label is not None:
                plt.plot(xData, yData, linestyle='solid', marker='o', color=color, label=label)
            else:
                plt.plot(xData, yData, linestyle='solid', marker='o', color=color)

    xLabel = pu.paramNameToAxisLabel(xParam, averageSamples)
    yLabel = pu.paramNameToAxisLabel(yParam, averageSamples)

    plt.xlabel(xLabel, fontsize=labelFontsize)
    plt.ylabel(yLabel, fontsize=labelFontsize)
            
    setAxisBoundaries(plotType, xParam, yParam)


def savePlotToFile(plotType, imageFormat='png'):
    fileName = 'plot_' + plotType + '.' + imageFormat

    if imageFormat == 'png' or imageFormat == 'pdf':
        plt.savefig(fileName)


def setAxisBoundaries(plotType, xParam, yParam):
    if yParam == 'runtime':
        plt.ylim(1,1e5)
        plt.yscale('log')
    if yParam == 'CI' or yParam == 'ivCI':
        plt.ylim(1,1e6)
        plt.yscale('log')

    if 's' not in plotType:
        # pb: 1a, 2a, 3a, 4a, 1v, 1r
        if 'a' in plotType or 'v' in plotType:
            ranges = range(0,110,10)
            plt.xticks(list(map(lambda x: x/100.0, ranges)))
        if 'r' in plotType:
            ranges = range(0,110,10)
            plt.xticks(list(map(lambda x: x/100.0, ranges)))
        # mb: 1b, 2b
        elif 'b' in plotType:
            if plotType == '1b':
                plt.xticks(range(0,45,5))
            if plotType == '2b':
                plt.xticks(range(0,55,5))
    else:
        # s: xxs
        if plotType == '1as':
            plt.xticks(range(0,22,2))
        elif plotType == '1bs' or plotType == '2as':
            plt.xticks(range(0,35,5))
        elif plotType == '2bs':
            plt.xticks(range(0,55,5))
        elif plotType == '3as':
            plt.xticks(range(0,55,5))
        elif plotType == '4as':
            plt.xticks(range(0,65,5))
    # CI vs. runtime
    # plt.xlim(1e1,1e5)
    # plt.xscale('log')

def getPlotSpecs(plotType):
    specs = {
        'x': 'n',
        'y': 'CI',
        'numDivisions': 10,
        'numColorDivisions': 7,
        'labelFontsize': 16,
        'plotStyle': 'line_solid',
        'imageFormat': 'pdf',
        'averageSamples': True,
        'smoothCurve': False,
        'regression': False,
        'sort': False
    }

    if 's' not in plotType:
        if 'a' in plotType or 'r' in plotType:
            specs['x'] = 'pb'
            
            if plotType == '1a':
                specs['numDivisions'] = 20
        elif 'b' in plotType:
            specs['x'] = 'mb'
    else:
        specs['x'] = 's'

        if plotType == '1as':
            specs['numDivisions'] = 20

    if '2a' in plotType:
        specs['numDivisions'] = 12
    elif '2b' in plotType:
        specs['numDivisions'] = 14
    elif '3a' in plotType:
        specs['numDivisions'] = 11

    if 'v' in plotType:
        specs['x'] = 'pb'
    # CI vs. runtime
    # specs['x'] = 'CI'
    # specs['y'] = 'runtime'
    return specs


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please specify input file paths correctly.')

        sys.exit()

    plotType = sys.argv[1]
    supportedPlotTypes = ['1a', '1as', '1b', '1bs', '1v', '1r', '2a', '2as', '2b', '2bs', '3a', '3as', '4a', '4as']

    if plotType not in supportedPlotTypes:
        print('Please specify a correct plot type (e.g., 1a).')

    specs = getPlotSpecs(plotType)
    
    basePath = 'experiments/overleaf/plot'
    # remove string 's' for reading data
    directoryPath = basePath + plotType.replace('s', '') + '/'
    fileNames = [f for f in listdir(directoryPath) if isfile(join(directoryPath, f))]
    fileNames.sort()
    
    parsedData = []
    
    for fileName in fileNames:
        if fileName.startswith('.'):
            continue

        filePath = directoryPath + fileName
        
        try:
            with open(filePath, 'r') as f:
                r = csv.reader(f)
                lines = list(r)

                if 'v' in plotType:
                    data = pu.parseData(algListCIBF.id_, lines)
                else:
                    data = pu.parseData(algListCI.id_, lines)
                parsedData.append(data)

                f.close()
        except Exception as e:
            # line = 'Please specify the input file correctly.'
            print(filePath)

    plt.figure(dpi=300)

    if 'v' in plotType:
        # yParams = ['CI', 'ivCI']
        yParams = ['ivCI']

        for y in yParams:
            specs['y'] = y

            processedData = []

            for data in parsedData:
                dataPoints = getDataPoints(data, specs)
                processedData.append(dataPoints)

            # if y == 'ivCI':
            #     specs['plotStyle'] = 'line_dotted'

            drawPlot(plotType, processedData, specs)
    else:
        processedData = []

        for data in parsedData:
            dataPoints = getDataPoints(data, specs)
            processedData.append(dataPoints)

        drawPlot(plotType, processedData, specs)
    
    plt.legend()
    # plt.show()

    savePlotToFile(plotType, specs['imageFormat'])
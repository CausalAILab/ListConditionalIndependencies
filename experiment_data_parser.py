import sys
import csv
import datetime
import time

import matplotlib.pyplot as plt
import numpy as np

# line 0: graph names
# line 1: nodes
# line 2: edges
# line 3-4, 5-6, 7-8
# for each 2 lines: 1)runtime of algorithm [ListGMP, ListCIBF, ListCI] 2) number of CIs

def parseData(lines):
    names = lines[0]
    nodes = lines[1]
    edges = lines[2]

    data = {
        'names': names,
        'nodes': list(map(lambda x: int(x), nodes)),
        'edges': list(map(lambda x: int(x), edges)),
    }

    startIndex = 3
    numAlgorithms = 3

    for i in range(numAlgorithms):
        runtimeIndex = startIndex + (i * 2)
        CIIndex = runtimeIndex + 1

        runtimesData = lines[runtimeIndex]
        numCIsData = lines[CIIndex]
        runtimes = []
        numCIs = []

        for j in range(len(runtimesData)):
            durationString = runtimesData[j]
            numCIString = numCIsData[j]

            # convert durating string '00:00:00' to seconds
            try:
                x = time.strptime(durationString,'%H:%M:%S')
                seconds = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()

                # round up to avoid undefined value in log-log plot
                if seconds == 0.0:
                    seconds = seconds + 1

                runtimes.append(seconds)
            except:
                runtimes.append(np.nan)

            try:
                numCI = int(numCIString)
                numCIs.append(numCI)
            except:
                numCIs.append(np.nan)
        
        parsedData = {
            'runtime': np.array(runtimes),
            'CI': np.array(numCIs)
        }

        if i == 0:
            data['ListGMP'] = parsedData
        elif i == 1:
            data['ListCIBF'] = parsedData
        elif i == 2:
            data['ListCI'] = parsedData

    return data

def drawPlot(data):
    # print(data)
    nodes = data['nodes']
    npNodes = np.array(nodes)
    npListGMP = np.array(data['ListGMP']['runtime'])
    npListCIBF = np.array(data['ListCIBF']['runtime'])
    npListCI = np.array(data['ListCI']['runtime'])

    plt.plot(npNodes, npListGMP, linestyle='--', marker='o', color='r', label='ListGMP')
    plt.plot(npNodes, npListCIBF, linestyle='--', marker='o', color='b', label='ListCIBF')
    plt.plot(npNodes, npListCI, linestyle='--', marker='o', color='g', label='ListCI')
    # plt.loglog(npNodes, npListGMP, linestyle='--', marker='o', color='r', label='ListGMP')
    # plt.loglog(npNodes, npListCIBF, linestyle='--', marker='o', color='b', label='ListCIBF')
    # plt.loglog(npNodes, npListCI, linestyle='--', marker='o', color='g', label='ListCI')

    # set y axis as log
    plt.yscale('log')

    # set boundaries of axis values
    # ax = plt.gca()
    # ax.set_xlim([0, 250])
    # ax.set_ylim([0, 4000])
    
    labelFontsize = 16
    plt.xlabel('Number of variables', fontsize=labelFontsize)
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
# Plotting flows
# flows[0]: time
# flows[1]: number of flows on path 1
# flows[2]: number of flows on path 2
# flows[3]: normalized number of flows on path 1
# flows[4]: normalized number of flows on path 2
# flows[5][0]: attacker first flow path
# flows[5][1]: attacker second flow path (if it exists)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from parseFlows import *
from parseXml import *


def plotFlows(flows, xrange, plotDetails):
    fig, ax = plt.subplots(figsize=(22, 12))
    ax.set_xlim(xrange[0], xrange[1])
    ax.set_ylim(0, int(plotDetails.get('Servers'))+1)

    for portId, flow in flows[1].items():
        ax.plot(flows[0], flow, 'C' + str(portId), label='Path ' + str(portId))
    # ax.plot(flows[0], flows[1], 'C1', label='Path1 (' + plotDetails.get('pathOneCap') + 'Gbps)')
    # ax.plot(flows[0], flows[2], 'C2', label='Path2 (' + plotDetails.get('pathTwoCap') + 'Gbps)')
    ax.legend()
    ax.set_title(plotDetails.get('title'), color='C0')
    plt.ylabel('Number of flows')
    plt.xlabel('Time (ms)')
    plt.show()
    
def plotNormalizedFlows(flows, xrange, plotDetails):
    fig, ax = plt.subplots(figsize=(22, 12))
    ax.set_xlim(xrange[0], xrange[1])
    ax.set_ylim(0, int(plotDetails.get('Servers'))+1)
    for portId, flow in flows[2].items():
        ax.plot(flows[0], flow, 'C' + str(portId), label='Path ' + str(portId))
    # ax.plot(flows[0], flows[3], 'C1', label='Path1 (' + plotDetails.get('pathOneCap') + 'Gbps)')
    # ax.plot(flows[0], flows[4], 'C2', label='Path2 (' + plotDetails.get('pathTwoCap') + 'Gbps)')
    ax.legend()
    ax.set_title('Normalized Flows: ' + plotDetails.get('title'), color='C0')
    plt.ylabel('Numer of flows')
    plt.xlabel('Time (ms)')
    plt.show()
    
def plotNormalizedFlowsPorts(flows, xrange, plotDetails, ports):
    fig, ax = plt.subplots(figsize=(22, 12))
    ax.set_xlim(xrange[0], xrange[1])
    ax.set_ylim(0, int(plotDetails.get('Servers'))+1)
    for portId, flow in flows[2].items():
        if portId in ports:
            ax.plot(flows[0], flow, 'C' + str(portId), label='Path ' + str(portId))
    # ax.plot(flows[0], flows[3], 'C1', label='Path1 (' + plotDetails.get('pathOneCap') + 'Gbps)')
    # ax.plot(flows[0], flows[4], 'C2', label='Path2 (' + plotDetails.get('pathTwoCap') + 'Gbps)')
    ax.legend()
    ax.set_title('Normalized Flows: ' + plotDetails.get('title'), color='C0')
    plt.ylabel('Numer of flows')
    plt.xlabel('Time (ms)')
    plt.show()  
        
def plotAllFlows(flows, xrange, plotDetails):
    plotFlows(flows, xrange, plotDetails)
    plotNormalizedFlows(flows, xrange, plotDetails)
    
# Plot a diagram showing which port each attacker flow has selected.
def plotAttacker(flows, xrange, plotDetails):
    fig, ax = plt.subplots(figsize=(22, 12))
    ax.set_xlim(xrange[0], xrange[1])
    #TODO: dynamically set the number of ports
    ax.set_ylim(int(plotDetails.get('Servers')), int(plotDetails.get('Servers'))+int(plotDetails.get('Paths'))+1)
    for idx, (attackerFlow, selectedPort) in enumerate(flows[3].items()):
        ax.plot(flows[0], selectedPort, 'C'+str(idx+1), label='Attacker ' + str(idx))
    ax.legend()
    ax.set_title(plotDetails.get('title'), color='C0')
    plt.ylabel('Selected Port')
    plt.xlabel('Time (ms)')
    plt.show()
    
# Plotting queues
# pi = ports.get(i): info about port i
# pi[0]: time
# pi[1]: txUtilization
# pi[2]: packets in queue
# TODO: update to work over multiple nodes.
def plotQueue(ports, xrange, plotDetails):
    for idx, (port, info) in enumerate(ports.items()):
        fig, ax = plt.subplots(figsize=(22, 12))
        ax.set_xlim(xrange[0], xrange[1])
        ax.set_ylim(0, int(plotDetails.get('Buffer'))+1)
        fig, ax = plt.subplots(figsize=(22, 12))
        port1 = ports.get('1')
        port2 = ports.get('2')
        ax.set_xlim(xrange[0], xrange[1])
        ax.set_ylim(0, 900)
        ax.plot(info[0], info[2], 'C1', label='Path' + port)
        # '(' + plotDetails.get('pathOneCap') + 'Gbps)')
        ax.legend()
        ax.set_title(plotDetails.get('title'), color='C0')
        plt.ylabel('Number of packets on queue')
        plt.xlabel('Time (ms)')
        plt.show()
    
def plotTxUtil(ports, xrange, plotDetails):
    for idx, (port, info) in enumerate(ports.items()):
        fig, ax = plt.subplots(figsize=(22, 12))
        ax.set_xlim(xrange[0], xrange[1])
        ax.set_ylim(0, 3)
        fig, ax = plt.subplots(figsize=(22, 12))
        port1 = ports.get('1')
        port2 = ports.get('2')
        ax.set_xlim(xrange[0], xrange[1])
        ax.set_ylim(0, 900)
        ax.plot(info[0], info[2], 'C1', label='Path' + port)
        # '(' + plotDetails.get('pathOneCap') + 'Gbps)')
        ax.legend()
        ax.set_title(plotDetails.get('title'), color='C0')
        plt.ylabel('Link Utilization')
        plt.xlabel('Time (ms)')
        plt.show()


def plotTxFlowUtilAux(port, xrange, plotDetails):
    fig, ax = plt.subplots(figsize=(22, 12))
    ax.set_xlim(xrange[0], xrange[1])
    ax.set_ylim(0, 2)
    for i, (flowId, flow) in enumerate(port[3].items()):
        ax.plot(port[0], flow, 'C' + str(i), label='FlowId:' + flowId)
    ax.legend()
    ax.set_title(plotDetails.get('title'), color='C0')
    plt.ylabel('Per Flow Link Utilization')
    plt.xlabel('Time (ms)')
    plt.show()
    
def plotTxFlowUtil(ports, xrange, plotDetails):
    plotTxFlowUtilAux(ports.get('1'), xrange, plotDetails)
    plotTxFlowUtilAux(ports.get('2'), xrange, plotDetails)
  

def computeCapacities(servers, paths, fastPaths, fastCap, slowCap):
    capacities = {}
    for i in range(0, paths):
        if (i < fastPaths):
            capacities.update({(servers+i+1):fastCap})
        else:
            capacities.update({(servers+i+1):slowCap})
    return capacities

def getPlotDetails(filename):
    components    = filename.split('-')
    fastPathCap   = components[2]
    slowPathCap   = components[3]
    fastPathNum   = components[4]
    buffer        = components[5]
    servers       = components[6]
    paths         = components[7]
    time          = components[8]
    transportProt = components[9]
    flowLetGap    = components[10]
    largeFlowSize = components[11]
    smallFlowSize = components[12]
    largeFlows    = components[13]
    attacker      = "No attacker" if components[14] == "no_attacker" else "Attacker"
    rate          = components[15]
    startTime     = components[16]
    offTime       = components[17]
    onTime        = components[18]
    packetSize    = components[19]
    attackerProt  = components[20]
    app           = components[21]
    attackerFlows = components[23]
    attackerFlowSize = components[24].split('.')[0]
    attackerStr   = "No attacker" if attacker == "No attacker" else  app + " attacker with offTime = " + offTime + ", onTime = " + onTime + ", startTime: " + startTime + ", flows: " + attackerFlows + ", rate: " + rate + ", attacker flow size= " + attackerFlowSize + ", attacker prot:" + attackerProt 
    
    capacities = computeCapacities(int(servers),int(paths),int(fastPathNum),int(fastPathCap),int(slowPathCap))
    
    title = "Number of paths: " + paths + ", fast path: " + fastPathCap + ", slow path: " + slowPathCap + ", flowlet gap = " + flowLetGap + ", Large/Small flows size = " + largeFlowSize +"/"+smallFlowSize + ", " + attackerStr + ", buffer=" + buffer
    return {'title':title, 
            'offTime':offTime,
            'onTime':onTime,  
            'FastCap':fastPathCap, 
            'SlowCap':slowPathCap,
            'FastPaths':fastPathNum,
            'Servers':servers, 
            'Paths':paths,
            'AttackerRate':rate, 
            'AttackerFlows':attackerFlows, 
            'flowlet':flowLetGap,
            'LargeFlowSize':largeFlowSize,
            'SmallFlowSize':smallFlowSize,
            'LargeFlows':largeFlows,
            'AttackerProt':attackerProt,
            'Buffer':buffer,
            'capacities':capacities
           }

def printFctStats(res):
    print ("Sender Avg FCT: %.4f" % res.get('sender_avg_fct'))
    print ("Sender Above Median Avg FCT: %.4f" % res.get('sender_above_median_avg_fct'))
    print ("Sender Below Median Avg FCT: %.4f" % res.get('sender_below_median_avg_fct'))
    print ("Sender Median FCT: %.4f" % res.get('sender_median_fct'))
    print ("Sender Variance FCT: %.4f" % res.get('sender_variance_fct'))
    print ("Avg FCT: %.4f" % res.get('avg_fct'))
    print ("Large Flows Avg FCT: %.4f" % res.get('large_flow_avg_fct', -1.0))
    print ("Small Flows Avg FCT: %.4f" % res.get('small_flow_avg_fct', -1.0))
    print ("Attacker Avg FCT: %.4f" % res.get('attacker_avg_fct', -1.0))
    
def printFlowBalance(log, window):
    capacities = log[2].get('capacities')
    time = log[0][0]
    flowsPerPort = log[0][2] #normalized flows per port
    balance = measureBalance(window, time, flowsPerPort, capacities)
    print("Average Flows Cab Distance: " + str(balance.get('cab')))
    print("Average Flows Chebysev Distance: " + str(balance.get('chebysev')))
    
    
def parseSimulationFiles(name):
    flows_file = name + ".flow"
    link_file = name + ".out"
    xml_file = name + ".xml"
    parse_flows = readLog(flows_file)
    parse_queues = readQueueLog(link_file) # if no queue is present
    parse_xml = computeFct(xml_file)
    return (parse_flows, parse_queues, getPlotDetails(name), parse_xml)


def plotSimulationRange(log, xrange):
    if log[3].get('offTime') == '0':
        print("\x1b[31m\"Baseline\"\x1b[0m")
    print(log[2].get('title'))
    printFlowBalance(log, xrange)
    printFctStats(log[3])
    plotAllFlows(log[0], xrange, log[2])
    plotAttacker(log[0], xrange, log[2])
    #plotQueue(log[1], xrange, log[2])
    #plotTxUtil(log[1], xrange, log[2])
  #  plotTxFlowUtil(log[1], xrange, log[2])

def plotSimulation(log):
    plotSimulationRange(log, (0, 4200))

def getCongaPlotDetails(filename):
    components    = filename.split('-')
    scheme        = components[9]
    size          = components[4]
    load          = components[5]
    attacker      = "No attacker" if components[7] == "no_attacker" else "Attacker"
    if scheme == "ecmp":
        flowLetGap  = "-"
        rate  = components[17]
        offTime = components[15]
        onTime = components[16]
        attackerProt = components[14]
        buffer = components[19]
    else:
        flowLetGap    = components[11]
        rate          = components[18]
        offTime       = components[16]
        onTime        = components[17]
        attackerProt  = components[15]
        buffer        = components[20]
    attackerStr   = "No attacker" if attacker == "No attacker" else " attacker with offTime = " + offTime + ", onTime = " + onTime + ", rate: " + rate + ", attacker prot:" + attackerProt 
    
    title = "Number of leaves/spines: " + size + ", flowlet gap = " + flowLetGap + ", load = " + load + ", " + attackerStr + ", buffer=" + buffer
    return {'title':title, 
            'offTime':offTime,
            'onTime':onTime,
            'load':load,
            'AttackerRate':rate, 
            'flowlet':flowLetGap,
            'AttackerProt':attackerProt,
            'scheme':scheme
           }

def parseCongaSimulationFiles(name):
    xml_file = name + ".xml"
    link_file = name + "-link-utility.out"
    parse_xml =  computeFct(xml_file)
    parse_queues = readQueueLog(link_file) # if no queue is present
    return (getCongaPlotDetails(name), parse_xml, parse_queues)



### Plot link info

def switchImbalance(ports):
    util = {k: info[1] for k, info in ports.items()}
    result = []
    for y in zip(*util.values()):
        minimum = min(y)
        maximum = max(y)
        avg = mean(y)
        result.append((maximum-minimum)/avg if avg != 0 else 0)
    return result

def plotImbalance(sims, switchName):
    fig, ax = plt.subplots(figsize=(22, 12))
    for i, sim in enumerate(sims):
        data = switchImbalance(sim[2].get(switchName, []))
        data_sorted = np.sort(data)

        # calculate the proportional values of samples
        p = 1. * np.arange(len(data)) / (len(data) - 1)

        ax.plot(data_sorted, p, 'C' + str(i), label='sim(' + str(i) +')')
    ax.legend()
    plt.xlabel('Utilization Imbalance')
    plt.ylabel('$p$')
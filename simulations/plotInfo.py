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
    ax.set_ylim(0, int(plotDetails.get('servers'))+1)
    ax.plot(flows[0], flows[1], 'C1', label='Path1 (' + plotDetails.get('pathOneCap') + 'Gbps)')
    ax.plot(flows[0], flows[2], 'C2', label='Path2 (' + plotDetails.get('pathTwoCap') + 'Gbps)')
    ax.legend()
    ax.set_title(plotDetails.get('title'), color='C0')
    plt.ylabel('Number of flows')
    plt.xlabel('Time (ms)')
    plt.show()
    
def plotNormalizedFlows(flows, xrange, plotDetails):
    fig, ax = plt.subplots(figsize=(22, 12))
    ax.set_xlim(xrange[0], xrange[1])
    ax.set_ylim(0, int(plotDetails.get('servers'))+1)
    ax.plot(flows[0], flows[3], 'C1', label='Path1 (' + plotDetails.get('pathOneCap') + 'Gbps)')
    ax.plot(flows[0], flows[4], 'C2', label='Path2 (' + plotDetails.get('pathTwoCap') + 'Gbps)')
    ax.legend()
    ax.set_title('Normalized Flows: ' + plotDetails.get('title'), color='C0')
    plt.ylabel('Numer of flows')
    plt.xlabel('Time (ms)')
    plt.show()
    
# Not used
def plotBalance(flows, xrange, plotDetails):
    fig, ax = plt.subplots(figsize=(22, 12))
    ax.set_xlim(xrange[0], xrange[1])
    ax.set_ylim(0, int(plotDetails.get('servers'))+1)
    ax.plot(flows[0], [a-b for a, b in zip(flows[4], flows[3])], 'C6', label='Flow balance')
    ax.legend()
    ax.set_title('Flow Balance: ' + plotDetails.get('title'), color='C0')
    plt.ylabel('Numer of flows')
    plt.xlabel('Time (ms)')
    plt.show()
    
def plotAllFlows(flows, xrange, plotDetails):
    plotFlows(flows, xrange, plotDetails)
    plotNormalizedFlows(flows, xrange, plotDetails)
    
def plotAttacker(flows, xrange, plotDetails):
    if 0 < len(flows[5]):
        fig, ax = plt.subplots(figsize=(22, 12))
        ax.set_xlim(xrange[0], xrange[1])
        ax.set_ylim(0, 3)
        ax.plot(flows[0], flows[5][0], 'C4', label='Attacker 1')
        if 1 < len(flows[5]):
            ax.plot(flows[0], flows[5][1], 'C5', label='Attacker 2')
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
# pi[3]: txUtilization per flow
def plotQueue(ports, xrange, plotDetails):
    fig, ax = plt.subplots(figsize=(22, 12))
    port1 = ports.get('1')
    port2 = ports.get('2')
    ax.set_xlim(xrange[0], xrange[1])
    ax.set_ylim(0, 900)
    ax.plot(port1[0], port1[2], 'C1', label='Path1 (' + plotDetails.get('pathOneCap') + 'Gbps)')
    ax.plot(port2[0], port2[2], 'C2', label='Path2 (' + plotDetails.get('pathTwoCap') + 'Gbps)')
    ax.legend()
    ax.set_title(plotDetails.get('title'), color='C0')
    plt.ylabel('Number of packets on queue')
    plt.xlabel('Time (ms)')
    plt.show()
    
def plotTxUtil(ports, xrange, plotDetails):
    fig, ax = plt.subplots(figsize=(22, 12))
    port1 = ports.get('1')
    port2 = ports.get('2')
    ax.set_xlim(xrange[0], xrange[1])
    ax.set_ylim(0, 2)
    ax.plot(port1[0], port1[1], 'C1', label='Path1 (' + plotDetails.get('pathOneCap') + 'Gbps)')
    ax.plot(port2[0], port2[1], 'C2', label='Path2 (' + plotDetails.get('pathTwoCap') + 'Gbps)')
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
    

def getPlotDetails(filename):
    components    = filename.split('-')
    pathOneCap    = components[2]
    pathTwoCap    = components[3]
    buffer        = components[4]
    servers       = components[5]
    time          = components[6]
    flowLetGap    = components[8]
    flowSize      = components[9]
    attacker      = "No attacker" if components[10] == "no_attacker" else "Attacker"
    rate          = components[11]
    startTime     = components[12]
    offTime       = components[13]
    onTime        = components[14]
    packetSize    = components[15]
    protocol      = components[16]
    app           = components[17]
    attackerFlows = components[19]
    attackerFlowSize = components[20].split('.')[0]
    attackerStr   = "No attacker" if attacker == "No attacker" else  app + " attacker with offTime = " + offTime + ", onTime = " + onTime + ", startTime: " + startTime + ", flows: " + attackerFlows + ", rate: " + rate + ", attacker flow= " + attackerFlowSize + ", " + protocol 
    
    title = "Flowlet gap = " + flowLetGap + ", Flow size = " + flowSize + ", " + attackerStr + ", buffer=" + buffer
    return {'title':title, 'onTime':onTime, 'offTime':offTime, 'pathOneCap':pathOneCap, 'pathTwoCap':pathTwoCap, 'servers':servers, 'rate':rate, 'attackerFlows':attackerFlows, 'flowlet':flowLetGap}

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
    capacities = {'1':float(log[2].get('pathOneCap')), '2':float(log[2].get('pathTwoCap'))}
    balance = measureBalance(window, log[0][0], {'1':log[0][3], '2':log[0][4]}, capacities)
    print("Average Flows Cab Distance: " + str(balance.get('cab')))
    print("Average Flows Chebysev Distance: " + str(balance.get('chebysev')))
    
    
def parseSimulationFiles(name):
    flows_file = name + ".flow"
    link_file = name + ".out"
    xml_file = name + ".xml"
    parse_flows = readLog(flows_file)
    parse_queues = readQueueLog(link_file)
    parse_xml = computeFct(xml_file)
    return (parse_flows, parse_queues, getPlotDetails(name), parse_xml)

def plotSimulationRange(log, xrange):
    if log[3].get('offTime') == '0':
        print("\x1b[31m\"Baseline\"\x1b[0m")
    print(log[2].get('title'))
    printFlowBalance(log, xrange)
    printFctStats(log[3])
    plotAllFlows(log[0], xrange, log[2])
    plotQueue(log[1], xrange, log[2])
    plotTxUtil(log[1], xrange, log[2])
  #  plotTxFlowUtil(log[1], xrange, log[2])
    plotAttacker(log[0], xrange, log[2])


def plotSimulation(log):
    plotSimulationRange(log, (0, 4200))
    
def bestAvgFct(log):
    return log[3].get('avg_fct')

def worstSenderAvgFct(log):
    return -log[3].get('sender_avg_fct')

def show(df):
    return df.style.apply(lambda x: ['background: #d65f5f' if int(x['offTime']) == 0 else '' for i in x], axis=1)

def buildPandaRow(window, sim):
    keys = ['onTime', 'offTime', 'servers', 'rate', 'attackerFlows', 'flowlet']
    result = { k: sim[2][k] for k in keys }
    
    capacities = {'1':float(sim[2].get('pathOneCap')), '2':float(sim[2].get('pathTwoCap'))}
    balance = measureBalance(window, sim[0][0], {'1':sim[0][3], '2':sim[0][4]}, capacities)
    result.update({'LoadBalance':balance.get('cab')})
    result.update({'SenderAvgFct':sim[3].get('sender_avg_fct')})
    result.update({'SenderVarianceFct':sim[3].get('sender_variance_fct')})
    result.update({'AttackerSendPackets':int(sim[3].get('attacker_tx_packets'))})
    result.update({'AttackerWasteRatio':float(sim[3].get('attacker_lost_packets'))/float(sim[3].get('attacker_tx_packets'))})
    # result.update({'AttackerLostPackets':int(sim[3].get('attacker_lost_packets'))})
    # result.update({'AttackerReceivedPackets':sim[3].get('attacker_rx_packets')})
    return result

def buildPanda(window, simulations):
    df = pd.DataFrame([buildPandaRow(window, sim) for sim in simulations])
    return df

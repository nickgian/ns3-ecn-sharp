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



def interactive_legend(ax=None):
    if ax is None:
        ax = plt.gca()
    if ax.legend_ is None:
        ax.legend()

    return InteractiveLegend(ax.get_legend())

class InteractiveLegend(object):
    def __init__(self, legend):
        self.legend = legend
        self.fig = legend.axes.figure

        self.lookup_artist, self.lookup_handle = self._build_lookups(legend)
        self._setup_connections()

        self.update()

    def _setup_connections(self):
        for artist in self.legend.texts + self.legend.legendHandles:
            artist.set_picker(10) # 10 points tolerance

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def _build_lookups(self, legend):
        labels = [t.get_text() for t in legend.texts]
        handles = legend.legendHandles
        label2handle = dict(zip(labels, handles))
        handle2text = dict(zip(handles, legend.texts))

        lookup_artist = {}
        lookup_handle = {}
        for artist in legend.axes.get_children():
            if artist.get_label() in labels:
                handle = label2handle[artist.get_label()]
                lookup_handle[artist] = handle
                lookup_artist[handle] = artist
                lookup_artist[handle2text[handle]] = artist

        lookup_handle.update(zip(handles, handles))
        lookup_handle.update(zip(legend.texts, handles))

        return lookup_artist, lookup_handle

    def on_pick(self, event):
        handle = event.artist
        if handle in self.lookup_artist:

            artist = self.lookup_artist[handle]
            artist.set_visible(not artist.get_visible())
            self.update()

    def on_click(self, event):
        if event.button == 3:
            visible = False
        elif event.button == 2:
            visible = True
        else:
            return

        for artist in self.lookup_artist.values():
            artist.set_visible(visible)
        self.update()

    def update(self):
        for artist in self.lookup_artist.values():
            handle = self.lookup_handle[artist]
            if artist.get_visible():
                handle.set_visible(True)
            else:
                handle.set_visible(False)
        self.fig.canvas.draw()




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
# pi[3]: txUtilization per flow
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
    #parse_queues = readQueueLog(link_file)
    parse_queues = []
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
    
def bestAvgFct(log):
    return log[3].get('avg_fct')

def worstSenderAvgFct(log):
    return -log[3].get('sender_avg_fct')


def getBaseLine(df):
    return df.loc[(df['offTime'] == '0') & (df['AttackerProt'] == 'Tcp')]

def isMore(base, cur, thresh):
    return cur >= base*(1+thresh)

def show(df, caption):
    base = getBaseLine(df)
    return df.style.\
        set_caption(caption).\
        format({'AttackerSendPackets': "{:,}"}).\
        format({'BufferDroppedPackets': "{:,}"}).\
        apply(lambda x:[('background-color: #E6584F' if isMore(float(base.SenderAvgFct),float(v),0.2) else \
                         ('background-color: #FAE4A1' if isMore(float(base.SenderAvgFct),float(v),0.10) else \
                          ('background-color:#61B65F' if isMore(float(v), float(base.SenderAvgFct),0.0) else ''))) for v in x], subset=['SenderAvgFct']).\
        apply(lambda x: ['background: #71A6D1' if int(x['offTime']) == 0 else '' for i in x], axis=1)


# sim[0]: parseFlows
    #sim[0][0]: time, sim[0][1]: portToFlows, sim[0][2]: normalizedPortsToFlows, sim[0][3]: attackerFlowsToPorts
#sim[1]: queue and link utilization info
#sim[2]: plot info
#sim[3]: flow completion info
def buildPandaRow(window, sim):
    keys = ['offTime','onTime', 'AttackerRate', 'AttackerFlows', 'flowlet','AttackerProt']
    result = { k: sim[2][k] for k in keys }
    
    capacities = sim[2].get('capacities')
    time = sim[0][0]
    flowsPerPort = sim[0][2] #normalized flows per port
    balance = measureBalance(window, time, flowsPerPort, capacities)
    changes = avgFlowChanges(window, time, flowsPerPort)
    result.update({'LoadBalanceSum':float(balance.get('cab'))})
    result.update({'LoadBalanceMax':float(balance.get('chebysev'))})
    result.update({'LoadBalanceAvg':float(balance.get('avgDistance'))})
    result.update({'FlowChanges':float(changes.get('flowChanges'))})
    result.update({'SenderAvgFct':float(sim[3].get('sender_avg_fct'))})
    result.update({'BufferDroppedPackets':int(sim[3].get('packetsDropped'))})
#     result.update({'SenderVarianceFct':sim[3].get('sender_variance_fct')})
#     result.update({'AttackerSendPackets':int(sim[3].get('attacker_tx_packets'))})
    result.update({'AttackerLargeAvgFct':float(sim[3].get('attacker_large_avg_fct'))})
#     result.update({'AttackerWasteRatio':float(sim[3].get('attacker_lost_packets'))/float(sim[3].get('attacker_tx_packets'))})
    result.update({'AttackerLostPackets':int(sim[3].get('attacker_lost_packets'))})
    # result.update({'AttackerReceivedPackets':sim[3].get('attacker_rx_packets')})
    return result

def buildPanda(window, simulations):
    df = pd.DataFrame([buildPandaRow(window, sim) for sim in simulations])
    return df


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
    xml_file = name
    parse_xml = computeFct(xml_file)
    return (getCongaPlotDetails(name), parse_xml)


def showConga(df, caption):
    base = getBaseLine(df)
    return df.style.\
        set_caption(caption).\
        format({'AttackerSendPackets': "{:,}"}).\
        format({'BufferDroppedPackets': "{:,}"}).\
        apply(lambda x:[('background-color: #E6584F' if isMore(float(base.AvgFct),float(v),0.25) else \
                         ('background-color: #FAE4A1' if isMore(float(base.AvgFct),float(v),0.15) else \
                          ('background-color:#61B65F' if isMore(float(v), float(base.AvgFct),0.0) else ''))) for v in x], subset=['AvgFct']).\
        apply(lambda x:[('background-color: #E6584F' if isMore(float(base.SmallAvgFct),float(v),0.20) else \
                         ('background-color: #FAE4A1' if isMore(float(base.SmallAvgFct),float(v),0.10) else \
                          ('background-color:#61B65F' if isMore(float(v), float(base.SmallAvgFct),0.0) else ''))) for v in x], subset=['SmallAvgFct']).\
        apply(lambda x:[('background-color: #E6584F' if isMore(float(base.LargeAvgFct),float(v),0.20) else \
                         ('background-color: #FAE4A1' if isMore(float(base.LargeAvgFct),float(v),0.10) else \
                          ('background-color:#61B65F' if isMore(float(v), float(base.LargeAvgFct),0.0) else ''))) for v in x], subset=['LargeAvgFct']).\
        apply(lambda x: ['background: #71A6D1' if int(x['offTime']) == 0 else '' for i in x], axis=1)



def buildCongaPandaRow(sim):
    keys = ['offTime','onTime', 'load', 'AttackerRate', 'flowlet','AttackerProt']
    result = { k: sim[0][k] for k in keys }
    
    #result.update({'SenderAvgFct':float(sim[1].get('sender_avg_fct'))})
    #result.update({'SenderVarianceFct':sim[1].get('sender_variance_fct')})
    #result.update({'SenderSmallAvgFct':float(sim[1].get('sender_small_avg_fct'))})
    #result.update({'SenderLargeAvgFct':float(sim[1].get('sender_large_avg_fct'))})
    result.update({'AvgFct':float(sim[1].get('avg_fct'))})
    #result.update({'SenderVarianceFct':sim[1].get('sender_variance_fct')})
    result.update({'SmallAvgFct':float(sim[1].get('small_flow_avg_fct', 0.0))})
    result.update({'Tail99':float(sim[1].get('small_flow_tail_99', 0.0))})
    result.update({'LargeAvgFct':float(sim[1].get('large_flow_avg_fct'))})
    result.update({'BufferDroppedPackets':int(sim[1].get('packetsDropped'))})
    result.update({'AttackerSendPackets':int(sim[1].get('attacker_tx_packets'))})
    result.update({'AttackerLargeAvgFct':float(sim[1].get('attacker_large_avg_fct'))})

    result.update({'AvgThroughput':int(sim[1].get('avg_bitrate', 0))/1000000 })
    result.update({'SmallAvgThroughput':int(sim[1].get('small_avg_bitrate', 0))/1000000})
    result.update({'LargeAvgThroughput':int(sim[1].get('large_avg_bitrate', 0))/1000000})

    #result.update({'AttackerWasteRatio':float(sim[1].get('attacker_lost_packets'))/float(sim[1].get('attacker_tx_packets'))})
    # result.update({'AttackerLostPackets':int(sim[3].get('attacker_lost_packets'))})
    # result.update({'AttackerReceivedPackets':sim[3].get('attacker_rx_packets')})
    return result

def buildCongaPanda(simulations):
    df = pd.DataFrame([buildCongaPandaRow(sim) for sim in simulations])
    return df
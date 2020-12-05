from __future__ import division
import sys
import os
import itertools
import math
from statistics import median, variance, mean
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

def parse_time_ns(tm):
    if tm.endswith('ns'):
        return int(tm[:-4])
    raise ValueError(tm)



class FiveTuple(object):
    __slots__ = ['sourceAddress', 'destinationAddress', 'protocol', 'sourcePort', 'destinationPort']
    def __init__(self, el):
        self.sourceAddress = el.get('sourceAddress')
        self.destinationAddress = el.get('destinationAddress')
        self.sourcePort = int(el.get('sourcePort'))
        self.destinationPort = int(el.get('destinationPort'))
        self.protocol = int(el.get('protocol'))

class Histogram(object):
    __slots__ = 'bins', 'nbins', 'number_of_flows'
    def __init__(self, el=None):
        self.bins = []
        if el is not None:
            #self.nbins = int(el.get('nBins'))
            for bin in el.findall('bin'):
                self.bins.append( (float(bin.get("start")), float(bin.get("width")), int(bin.get("count"))) )

class Flow(object):
    __slots__ = ['flowId', 'delayMean', 'packetLossRatio', 'rxBitrate', 'txBitrate',
                 'fiveTuple', 'packetSizeMean', 'probe_stats_unsorted',
                 'hopCount', 'flowInterruptionsHistogram', 'rx_duration', 'fct', 'txBytes', 'txPackets', 'lostPackets', 'rxPackets', 'packetsDropped']
    def __init__(self, flow_el):
        self.flowId = int(flow_el.get('flowId'))
        rxPackets = int(flow_el.get('rxPackets'))
        txPackets = int(flow_el.get('txPackets'))
        tx_duration = float(int(flow_el.get('timeLastTxPacket')[:-4]) - int(flow_el.get('timeFirstTxPacket')[:-4]))*1e-9
        rx_duration = float(int(flow_el.get('timeLastRxPacket')[:-4]) - int(flow_el.get('timeFirstRxPacket')[:-4]))*1e-9
        fct = float(int(flow_el.get('timeLastRxPacket')[:-4]) - int(flow_el.get('timeFirstTxPacket')[:-4]))*1e-9
        txBytes = int(flow_el.get('txBytes'))

        self.txBytes = txBytes
        self.txPackets = txPackets
        self.rx_duration = rx_duration
        self.rxPackets = rxPackets
        self.packetsDropped = 0
        if fct > 0:
            self.fct = fct
        else:
            self.fct = None
        self.probe_stats_unsorted = []
        if rxPackets:
            self.hopCount = float(flow_el.get('timesForwarded')) / rxPackets + 1
        else:
            self.hopCount = -1000
        if rxPackets:
            self.delayMean = float(flow_el.get('delaySum')[:-4]) / rxPackets * 1e-9
            self.packetSizeMean = float(flow_el.get('rxBytes')) / rxPackets
        else:
            self.delayMean = None
            self.packetSizeMean = None
        if rx_duration > 0:
            self.rxBitrate = int(flow_el.get('rxBytes'))*8 / rx_duration
        else:
            self.rxBitrate = None
        if tx_duration > 0:
            self.txBitrate = int(flow_el.get('txBytes'))*8 / tx_duration
        else:
            self.txBitrate = None
        lost = float(flow_el.get('lostPackets'))
        self.lostPackets = lost
        #print "rxBytes: %s; txPackets: %s; rxPackets: %s; lostPackets: %s" % (flow_el.get('rxBytes'), txPackets, rxPackets, lost)
        if rxPackets == 0:
            self.packetLossRatio = None
        else:
            self.packetLossRatio = (lost / (rxPackets + lost))

        interrupt_hist_elem = flow_el.find("flowInterruptionsHistogram")
        if interrupt_hist_elem is None:
            self.flowInterruptionsHistogram = None
        else:
            self.flowInterruptionsHistogram = Histogram(interrupt_hist_elem)


class ProbeFlowStats(object):
    __slots__ = ['probeId', 'packets', 'bytes', 'delayFromFirstProbe']

class Simulation(object):
    def __init__(self, simulation_el):
        self.flows = []
        FlowClassifier_el, = simulation_el.findall("Ipv4FlowClassifier")
        flow_map = {}
        for flow_el in simulation_el.findall("FlowStats/Flow"):
            flow = Flow(flow_el)
            flow_map[flow.flowId] = flow
            self.flows.append(flow)
            for elt in flow_el.findall("packetsDropped"):
                if elt.attrib.get('reasonCode') == '3':
                    flow.packetsDropped = int(elt.attrib.get('number'))

        for flow_cls in FlowClassifier_el.findall("Flow"):
            flowId = int(flow_cls.get('flowId'))
            flow_map[flowId].fiveTuple = FiveTuple(flow_cls)

        for probe_elem in simulation_el.findall("FlowProbes/FlowProbe"):
            probeId = int(probe_elem.get('index'))
            for stats in probe_elem.findall("FlowStats"):
                flowId = int(stats.get('flowId'))
                s = ProbeFlowStats()
                s.packets = int(stats.get('packets'))
                s.bytes = int(stats.get('bytes'))
                s.probeId = probeId
                if s.packets > 0:
                    s.delayFromFirstProbe =  parse_time_ns(stats.get('delayFromFirstProbeSum')) / float(s.packets)
                else:
                    s.delayFromFirstProbe = 0
                flow_map[flowId].probe_stats_unsorted.append(s)
                # for packetDrops in stats.findall("packetsDropped"):
                #     if int(packetDrops.get('reasonCode')) == 3:
                #         flow_map[flowId].packetsDropped += int(packetDrops.get('number'))

class Compromised(object):
    def __init__(self, servers):
        self.hosts = set()
        for host in servers:
            hostIp = host.get('server')
            self.hosts.add(hostIp)

def isSender(sourceAddress):
    return sourceAddress.split('.')[2] == '2'

def computeFct(file):
    file_obj = open(file)
    #print "Reading XML file ",

    sys.stdout.flush()
    level = 0
    sim_list = []
    compromisedHosts = set()

    tree = ElementTree.parse(file_obj)

    compromisedHosts = Compromised(tree.findall("Compromised")).hosts

    
    sim = Simulation(tree.find("FlowMonitor"))
    sim_list.append(sim)
    

    total_fct = 0
    flow_count = 0
    large_flow_total_fct = 0
    large_flow_count = 0
    small_flow_total_fct = 0
    small_flow_count = 0

    worst_fct = 0
    best_fct = 0

    total_flow_tx = 0
    total_dropped_packets = 0
    total_lost_packets = 0
    total_packets = 0
    total_rx_packets = 0

    # Keeping track only of the flows generated by the sending servers.
    worst_fct_sender = 0
    total_flow_count_sender = 0
    total_fct_sender = 0
    large_flow_total_fct_sender = 0
    large_flow_count_sender = 0
    small_flow_total_fct_sender = 0
    small_flow_count_sender = 0
    total_flow_tx_sender = 0
    total_lost_packets_sender = 0
    total_packets_sender = 0
    total_rx_packets_sender = 0

    attacker_fct = 0
    attacker_flows = 0
    attacker_large_flow_total_fct = 0
    attacker_large_flow_count = 0
    attacker_small_flow_total_fct = 0
    attacker_small_flow_count = 0
    attacker_total_packets = 0
    attacker_total_rx_packets = 0
    attacker_total_lost_packets = 0
    attacker_dropped_packets = 0

    flow_bitrates = []
    small_flow_bitrates = []
    large_flow_bitrates = []

    flow_freq = {}
    flow_fct = {}
    sender_flow_fct = {}
    small_flow_list = []
    
    for sim in sim_list:
        for flow in sim.flows:
            if flow.fct == None or flow.txBitrate == None or flow.rxBitrate == None:
                continue
            t = flow.fiveTuple
            if t.sourceAddress in compromisedHosts:
                attacker_fct += flow.fct
                attacker_flows += 1
                attacker_total_packets += flow.txPackets
                attacker_total_rx_packets += flow.rxPackets
                attacker_total_lost_packets += flow.lostPackets
                attacker_dropped_packets += flow.packetsDropped
                if flow.txBytes > 10000000:
                    attacker_large_flow_count += 1
                    attacker_large_flow_total_fct += flow.fct
                if flow.txBytes < 100000:
                    attacker_small_flow_count += 1
                    attacker_small_flow_total_fct += flow.fct
            else:
                flow_count += 1
                total_fct += flow.fct
                total_packets += flow.txPackets
                total_lost_packets += flow.lostPackets
                total_dropped_packets += flow.packetsDropped
                total_rx_packets += flow.rxPackets
                total_flow_tx += flow.txBytes
                flow_bitrates.append(flow.txBitrate)
                if flow.txBytes > 10000000:
                    large_flow_count += 1
                    large_flow_total_fct += flow.fct
                    large_flow_bitrates.append(flow.txBitrate)
                if flow.txBytes < 100000:
                    small_flow_count += 1
                    small_flow_total_fct += flow.fct
                    small_flow_bitrates.append(flow.txBitrate)
                    small_flow_list.append(flow)
                if flow.fct > worst_fct:
                    worst_fct = flow.fct
                # Logging sender flow details
                if isSender(t.sourceAddress):
                    total_flow_count_sender += 1
                    total_fct_sender += flow.fct
                    total_flow_tx_sender += flow.txBytes
                    total_lost_packets_sender += flow.lostPackets
                    total_packets_sender += flow.txPackets
                    total_rx_packets_sender += flow.rxPackets
                    if flow.txBytes > 10000000:
                        large_flow_count_sender += 1
                        large_flow_total_fct_sender += flow.fct
                    if flow.txBytes < 100000:
                        small_flow_count_sender += 1
                        small_flow_total_fct_sender += flow.fct
                    if flow.fct > worst_fct_sender:
                        worst_fct_sender = flow.fct
            if t.sourceAddress not in flow_freq:
                flow_freq[t.sourceAddress] = 1
            else:
                flow_freq[t.sourceAddress] = (flow_freq[t.sourceAddress] + 1)
            if t.sourceAddress not in flow_fct:
                flow_fct[t.sourceAddress] = [flow.fct]
                if isSender(t.sourceAddress):
                    sender_flow_fct[t.sourceAddress] = [flow.fct]
            else:
                flow_fct[t.sourceAddress].insert(0,flow.fct)
                if isSender(t.sourceAddress):
                    sender_flow_fct[t.sourceAddress].insert(0,flow.fct)


    results = {}
    sender_fct_ordered = list(itertools.chain.from_iterable(sender_flow_fct.values()))
    sender_fct_ordered.sort()
    median_fct = median(sender_fct_ordered)
    variance_fct = variance(sender_fct_ordered)
    above_median = sender_fct_ordered[int(len(sender_fct_ordered)/2):]
    below_median = sender_fct_ordered[:int(len(sender_fct_ordered)/2)]
    # print(flow_freq)
    # print(flow_fct)
    

    if total_flow_count_sender != 0:
        results.update({'sender_median_fct' : median_fct,'sender_variance_fct': variance_fct,
                        'sender_above_median_avg_fct': mean(above_median),
                        'sender_below_median_avg_fct': mean(below_median)})
        results.update({'sender_avg_fct': total_fct_sender / total_flow_count_sender})        
        
    if large_flow_count_sender != 0:
        results.update({'sender_large_avg_fct': large_flow_total_fct_sender / large_flow_count_sender})

    if small_flow_count_sender != 0:
        results.update({'sender_small_avg_fct': small_flow_total_fct_sender / small_flow_count_sender})
    
    results.update({'avg_fct': (total_fct / flow_count)})
    results.update({'packetsDropped': total_dropped_packets})

    results.update({'avg_bitrate': mean(flow_bitrates)})
    
    if large_flow_count != 0:
        results.update({'large_flow_avg_fct':(large_flow_total_fct / large_flow_count)})
        results.update({'large_avg_bitrate': mean(large_flow_bitrates)})
   
    if small_flow_count != 0:
        small_flow_list.sort (key=lambda x: x.fct)
        index_99 = int(math.ceil(len(small_flow_list) * 0.99)) - 1
        results.update({'small_flow_tail_99': small_flow_list[index_99].fct})
        results.update({'small_flow_avg_fct':(small_flow_total_fct / small_flow_count)})
        results.update({'small_avg_bitrate': mean(small_flow_bitrates)})

    if attacker_flows > 0:
        results.update({'attacker_avg_fct':(attacker_fct / attacker_flows), 'attacker_tx_packets':attacker_total_packets, 'attacker_rx_packets':attacker_total_rx_packets, 'attacker_lost_packets':attacker_total_lost_packets})
    
    if attacker_large_flow_count > 0:
        results.update({'attacker_large_avg_fct':(attacker_large_flow_total_fct / attacker_large_flow_count)})
        
    #results.update({'attacker_dropped_packets':attacker_dropped_packets})
    return results

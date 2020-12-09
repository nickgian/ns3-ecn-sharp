import pandas as pd
import numpy as np
from statistics import median, variance, mean


# Utilities
def bestAvgFct(log):
    return log[3].get('avg_fct')

def worstSenderAvgFct(log):
    return -log[3].get('sender_avg_fct')


def getBaseLine(df):
    return df.loc[(df['offTime'] == '0') & (df['AttackerProt'] == 'Tcp')]

def isMore(base, cur, thresh):
    return cur >= base*(1+thresh)

## Aggregating queue information
# ports is a dictionary from portIdx to time, util, queue lists.
# Computes the average port utilization excluding samples where utilization is 0.
def perPortAvgUtilization(ports):
    result = {}
    for port, info in ports.items():
        result.update({port:mean([u for u in info[1] if u > 0.001])})
    return result

# switches contains a dictionary from switches to a dictionary from ports to info.
def perSwitchAvgUtilization(switches):
    result = {}
    for switch, ports in switches.items():
        result.update({switch: perPortAvgUtilization(ports)})
    return result

# Return the avg utilization across all ports, across all switches.
def networkAvgUtilization(switches):
    perSwitchList = []
    for ports in perSwitchAvgUtilization(switches).values():
        perSwitch = mean(list(ports.values()))
        perSwitchList.append(perSwitch)
    if perSwitchList == []:
        return -1
    else:
        return mean(perSwitchList)

# Panda tables generation

## For letflow-convergence simulations.

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
    result.update({'AttackerLargeAvgFct':float(sim[3].get('attacker_large_avg_fct'))})
    result.update({'AttackerLostPackets':int(sim[3].get('attacker_lost_packets'))})
#     result.update({'SenderVarianceFct':sim[3].get('sender_variance_fct')})
#     result.update({'AttackerSendPackets':int(sim[3].get('attacker_tx_packets'))})
#     result.update({'AttackerWasteRatio':float(sim[3].get('attacker_lost_packets'))/float(sim[3].get('attacker_tx_packets'))})

    # result.update({'AttackerReceivedPackets':sim[3].get('attacker_rx_packets')})
    return result

def buildPanda(window, simulations):
    df = pd.DataFrame([buildPandaRow(window, sim) for sim in simulations])
    return df


## For conga simulations 

def showConga(df, caption):
    base = getBaseLine(df)
    return df.style.\
        set_caption(caption).\
        format({'AttackerSendPackets': "{:,}"}).\
        format({'BufferDroppedPackets': "{:,}"}).\
        apply(lambda x:[('background-color: #E6584F' if isMore(float(base.AvgFct),float(v),0.20) else \
                         ('background-color: #FAE4A1' if isMore(float(base.AvgFct),float(v),0.10) else \
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
    
    result.update({'AvgFct':float(sim[1].get('avg_fct'))})
    result.update({'SmallAvgFct':float(sim[1].get('small_flow_avg_fct', 0.0))})
    result.update({'Tail99':float(sim[1].get('small_flow_tail_99', 0.0))})
    result.update({'LargeAvgFct':float(sim[1].get('large_flow_avg_fct'))})
    result.update({'BufferDroppedPackets':int(sim[1].get('packetsDropped'))})
    result.update({'AttackerSendPackets':int(sim[1].get('attacker_tx_packets'))})
    result.update({'AttackerLargeAvgFct':float(sim[1].get('attacker_large_avg_fct'))})
    result.update({'AvgUtilization':networkAvgUtilization(sim[2])})

    #result.update({'AttackerWasteRatio':float(sim[1].get('attacker_lost_packets'))/float(sim[1].get('attacker_tx_packets'))})
    # result.update({'AttackerLostPackets':int(sim[3].get('attacker_lost_packets'))})
    # result.update({'AttackerReceivedPackets':sim[3].get('attacker_rx_packets')})
    return result

def buildCongaPanda(simulations):
    df = pd.DataFrame([buildCongaPandaRow(sim) for sim in simulations])
    return df
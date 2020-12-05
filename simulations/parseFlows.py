import bisect
from itertools import tee
# Parsing Flow Information

def parseTime(s):
    return float(s[1:].replace("ms",""))
    
def parseFlowCount(s):
    ls = s.split(":",1)
    return (int(ls[0]), float(ls[1]))

def parseAttackerPort(s):
    ls = s.split("~",1)
    return (int(ls[0]), int(ls[1]))

def tryParseAttackerPort(s, i):
    try:
        return parseAttackerPort(s[i])
    except IndexError:
        return None
    except ValueError:
        return None

def tryParseFlowCount(s, i):
    try:
        return parseFlowCount(s[i])
    except IndexError:
        return None
    
# Remove attacker flows from port->number_of_flows diagram
def normalize(portIdx, portCnt, attackerPorts):
    for k, i in attackerPorts.items():
        if i == portIdx:
            portCnt = portCnt-1
    return portCnt

# Used to accumulate the set of ports used in the simulation.
seenPorts = set()

def parseLogLine(s):
    s = s.split(",")
    s = list(map(lambda x: x.strip(), s))
    time = parseTime(s[0])
    ports = {}
    attackerPorts = {} # map from flowId to assigned port.
    
    # Parse which ports attacker flows are routed to.
    idx = 1
    parsed = tryParseAttackerPort(s,idx)
    while parsed != None:
        attackerPorts.update({parsed[0]:parsed[1]})
        idx +=1
        parsed = tryParseAttackerPort(s, idx)

    parsed = tryParseFlowCount(s, idx)
    while parsed != None:
        seenPorts.add(parsed[0])
        ports.update({parsed[0]:parsed[1]})
        idx += 1
        parsed = tryParseFlowCount(s, idx)

    # attackerPort1 = tryParseAttackerPort(s, 1) # attacker flow 1
    # attackerPort2 = tryParseAttackerPort(s, 2) # attacker flow 2
    # if attackerPort1 == -1:
    #     s1 = tryParseFlowCount(s, 1)
    #     s2 = tryParseFlowCount(s, 2)
    #     ports.update({s1[0]:s1[1]})
    #     ports.update({s2[0]:s2[1]})
    # else:
    #     if attackerPort2 == -1:
    #         s1 = tryParseFlowCount(s, 2)
    #         s2 = tryParseFlowCount(s, 3)
    #         ports.update({s1[0]:s1[1]})
    #         ports.update({s2[0]:s2[1]})
    #         attackerPorts.insert(0, attackerPort1)
    #     else:
    #         s1 = tryParseFlowCount(s, 3)
    #         s2 = tryParseFlowCount(s, 4)
    #         ports.update({s1[0]:s1[1]})
    #         ports.update({s2[0]:s2[1]})
    #         attackerPorts.insert(0, attackerPort2)
    #         attackerPorts.insert(0, attackerPort1)
        
    normalizedPorts = {k: normalize(k, v, attackerPorts) for k, v in ports.items()}
    return (time, ports, normalizedPorts, attackerPorts)


def measureBalanceAvg(samples):
    acc = 0.0
    for s in samples:
        acc += s
    return (acc / len(samples))

# Computes the distance from the optimal assignment for one path:
# |(c/TotalCapacity) * totalFlows - f| 
# For a single time sample.
def cabDistance(capacity, flows, totalCapacity, totalFlows):
#     print(abs(capacity/totalCapacity * totalFlows - flows))
    return abs(capacity/totalCapacity * totalFlows - flows)

# time is a vector of floats
# flowsPerPort is a map from port number to a vector of floats
def measureBalance(window, time, flowsPerPort, capacities):
    minTime = window[0]
    maxTime = window[1]
    # Find the indices corresponding to the given time
    i = bisect.bisect_left(time, minTime)
    j = bisect.bisect_left(time, maxTime)
    numberOfFlows = sum([f[i] for f in flowsPerPort.values()]) #A single sample should suffice to compute the sum of flows
    totalCapacity = sum([c for c in capacities.values()])
    perPortDistance = []
    # Compute per port distance for every time sample.
    for port, flowsOnPort in flowsPerPort.items():
#         print(str(capacities.get(port)) +' flows: ' + str([f for f in flowsOnPort[i:j]]))
        perPortDistance.append([cabDistance(capacities.get(port, 0), f, totalCapacity, numberOfFlows) for f in flowsOnPort[i:j]])
    result = {}
    result.update({'cab': measureBalanceAvg([sum(i) for i in zip(*perPortDistance)])})
    result.update({'avgDistance': measureBalanceAvg([sum(i)/len(i) for i in zip(*perPortDistance)])})
    result.update({'chebysev': measureBalanceAvg([max(i) for i in zip(*perPortDistance)])})
    return result

# We only count reductions in number of flows to avoid double counting.
def countChanges(prev,curr):
    if curr < prev:
        return prev - curr
    else:
        return 0
    
def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def avgFlowChanges(window, time, flowsPerPort):
    minTime = window[0]
    maxTime = window[1]
    # Find the indices corresponding to the given time
    i = bisect.bisect_left(time, minTime)
    j = bisect.bisect_left(time, maxTime)
    perPortChanges = []
    for port, flowsOnPort in flowsPerPort.items():
        changes = []
        for prev, cur in pairwise(flowsOnPort[i:j]):
            changes.append(countChanges(prev, cur))
        perPortChanges.append(changes)
    result = {}
    result.update({'flowChanges': measureBalanceAvg([sum(i) for i in zip(*perPortChanges)])})
    return result
    
def parseLog(ls):
    timeAxis = []
    plots = {} # Mapping ports to lists of number of flows.
    normalizedPlots = {}
    # plotOne = []
    # plotTwo = []
    # normalizedPlotOne = []
    # normalizedPlotTwo = []
    attackerPorts = {}

    parsedLs = [parseLogLine(s) for s in ls]

    # Initialize plots and normalizedPlots
    for portId in seenPorts:
        plots.update({portId:[]})
        normalizedPlots.update({portId:[]})

    for parsedLine in parsedLs:
        timeAxis.append(parsedLine[0])
        # For every port->flows parsed, add them to existing log.
        for portId in seenPorts:
            samplesForPortId = plots.get(portId, [])
            samplesForPortId.append(parsedLine[1].get(portId, 0.0))
            normalizedSamplesForPortId = normalizedPlots.get(portId, [])
            normalizedSamplesForPortId.append(parsedLine[2].get(portId, 0.0))
            # plots.update({portId: plots.get(portId, []).append(})
            # normalizedPlots.update({portId: normalizedPlots.get(portId, []).append(parsedLine[2].get(portId, 0.0))})
        
        for flowId, p in parsedLine[3].items():
            try:
                current = attackerPorts.get(flowId)
                current.append(p)
            except:
                attackerPorts.update({flowId:[p]})
            # attackerPorts.update({flowId:})
            # porti = attackerPorts.get(i, [])
            # porti.append(parsedLine[3][i])
            # attackerPorts.update({i: porti})
    
    #adding missing samples from late-started flows
    samples = len(timeAxis)
    for flow, port in attackerPorts.items():
        if len(port) < samples:
            port = ([0.0] * (samples-len(port))) + port
            attackerPorts.update({flow: port})
    return (timeAxis, plots, normalizedPlots, attackerPorts)


def readLog(f):
    with open(f) as log_file:
        seenPorts = set ()
        return parseLog(log_file.readlines())
    
# Parsing Queue Information


def buildFlowUtils(flowTxUtil, flowSet):
    result = {}
    for flow in flowSet:
        result.update({flow:[]})

    for flowUtilMap in flowTxUtil:
        for flow in flowSet:
            util = flowUtilMap.get(flow, 0.0)
            fMap = result.get(flow, [])
            fMap.append(util)
    return result

def parseQueueLogLine(s):
    s = s.split(",")
    s = list(map(lambda x: x.strip(), s))
    time = parseTime(s[0])
    txUtil = float(s[1])
    queuePackets = float(s[2])
    flowTxUtil = {}
    flowSet = set()
    for string in s[7:]:
        flow = string.split(":")
        flowTxUtil.update({flow[0]:flow[1]})
        flowSet.add(flow[0])
    return (time, txUtil, queuePackets, flowSet, flowTxUtil)
    
def parseQueueLog(ls):
    ports = {}
    timeAxis = []
    txUtilPlot = []
    queuePlot = []
    flowTxUtilPlot = []
    flowSet = set() # Set of flow ids that have appeared throughout the simulation.
    firstIter = True
    portIdx = 0
    for s in ls:
        if s.strip().startswith('Port'):
            if not(firstIter): # if this is not the first iteration
                ports.update({portIdx: (timeAxis.copy(), txUtilPlot.copy(), queuePlot.copy(), flowTxUtilPlot.copy())}) #store the info
            else:
                firstIter = False
            portIdx = s.strip().split(' ')[1] #get the port id
            # and reset the time/tx/queue info.
            timeAxis = []
            txUtilPlot = []
            queuePlot = []
            flowTxUtilPlot = []
        else:
            # ignore empty lines and lines that declare the leaf 
            # (we only care about 1 leaf for now, needs fix for more involved networks)
            if not(len(s) == 0 or s.isspace() or s.startswith('Leaf')):
                parsedLine = parseQueueLogLine(s)
                timeAxis.append(parsedLine[0])
                txUtilPlot.append(parsedLine[1])
                queuePlot.append(parsedLine[2])
               # flowSet.update(parsedLine[3])
               # flowTxUtilPlot.append(parsedLine[4])
    #ports.update((pi, (v[0], v[1], v[2], buildFlowUtils(v[3], flowSet))) for pi,v in ports.items())
    return ports
        

def readQueueLog(f):
    with open(f) as log_file:
        return parseQueueLog(log_file.readlines())
    
    

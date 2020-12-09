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


# Per flow-stuff, deprecated.
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
    return (time, txUtil, queuePackets)
    
def parseQueueLog(ls):
    nodes = {} # map from node to ports
    ports = {} # map from ports to utilizations
    timeAxis = []
    txUtilPlot = []
    queuePlot = []
    firstIter = True
    portIdx = 0
    nodeIdx = ''
    for s in ls:
        if s.strip().startswith('Spine') or s.strip().startswith('Leaf'):
            # If a new spine is encountered and it's not the first one, then store previous logs.
            if not(firstIter):
                ports.update({portIdx: (timeAxis.copy(), txUtilPlot.copy(), queuePlot.copy())}) # add last port
                nodes.update({nodeIdx: ports.copy()}) #keep a copy of ports for the previous switch.
                # reset the ports and firstIter
                ports = {}
                firstIter = True

            # update node id
            node = s.strip().split(' ')
            nodeIdx = node[0] + node[1] # get the node id

        # If it's a port    
        elif s.strip().startswith('Port'):
            if not(firstIter): # if this is not the first port iterated for this switch
                ports.update({portIdx: (timeAxis.copy(), txUtilPlot.copy(), queuePlot.copy())}) #store the info for this port.
            else:
                firstIter = False # declare that we are past the first port, and start collecting info.
            portIdx = s.strip().split(' ')[1] #get the port id
            # and reset the time/tx/queue info since we are parsing info for a new port.
            timeAxis = []
            txUtilPlot = []
            queuePlot = []
        else:
            # ignore empty lines
            if not(len(s) == 0 or s.isspace()):
                parsedLine = parseQueueLogLine(s)
                timeAxis.append(parsedLine[0])
                txUtilPlot.append(parsedLine[1])
                queuePlot.append(parsedLine[2])

    # Add last switch info
    ports.update({portIdx: (timeAxis.copy(), txUtilPlot.copy(), queuePlot.copy())}) # add last port
    nodes.update({nodeIdx: ports}) #no need to copy for the last one
    return nodes
        

def readQueueLog(f):
    try:
        h = open(f)
    except OSError:
        return {}

    with h:
        return parseQueueLog(h.readlines())
        
    
    

/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */

#include "ipv4-letflow-routing.h"

#include <assert.h>

#include <algorithm>

#include "ns3/channel.h"
#include "ns3/flow-id-tag.h"
#include "ns3/log.h"
#include "ns3/net-device.h"
#include "ns3/node.h"
#include "ns3/simulator.h"

namespace ns3 {

NS_LOG_COMPONENT_DEFINE("Ipv4LetFlowRouting");

NS_OBJECT_ENSURE_REGISTERED(Ipv4LetFlowRouting);

Ipv4LetFlowRouting::Ipv4LetFlowRouting()
    : m_flowletTimeout(
          MicroSeconds(50)),  // The default value of flowlet timeout is small
                              // for experimental purpose
      m_ipv4(0),
      m_letFlowHistory(LetFlowHistory())

{
  assert(!m_letFlowHistory.enabled && "LetFlowHistory disabled by default.");
  NS_LOG_FUNCTION(this);
}

Ipv4LetFlowRouting::~Ipv4LetFlowRouting() { NS_LOG_FUNCTION(this); }

TypeId Ipv4LetFlowRouting::GetTypeId(void) {
  static TypeId tid = TypeId("ns3::Ipv4LetFlowRouting")
                          .SetParent<Object>()
                          .SetGroupName("Internet")
                          .AddConstructor<Ipv4LetFlowRouting>();

  return tid;
}

void Ipv4LetFlowRouting::AddRoute(Ipv4Address network, Ipv4Mask networkMask,
                                  uint32_t port) {
  NS_LOG_LOGIC(this << " Add LetFlow routing entry: " << network << "/"
                    << networkMask << " would go through port: " << port);
  LetFlowRouteEntry letFlowRouteEntry;
  letFlowRouteEntry.network = network;
  letFlowRouteEntry.networkMask = networkMask;
  letFlowRouteEntry.port = port;
  m_routeEntryList.push_back(letFlowRouteEntry);
}

std::vector<LetFlowRouteEntry> Ipv4LetFlowRouting::LookupLetFlowRouteEntries(
    Ipv4Address dest) {
  std::vector<LetFlowRouteEntry> letFlowRouteEntries;
  std::vector<LetFlowRouteEntry>::iterator itr = m_routeEntryList.begin();
  for (; itr != m_routeEntryList.end(); ++itr) {
    if ((*itr).networkMask.IsMatch(dest, (*itr).network)) {
      letFlowRouteEntries.push_back(*itr);
    }
  }
  return letFlowRouteEntries;
}

Ptr<Ipv4Route> Ipv4LetFlowRouting::ConstructIpv4Route(uint32_t port,
                                                      Ipv4Address destAddress) {
  Ptr<NetDevice> dev = m_ipv4->GetNetDevice(port);
  Ptr<Channel> channel = dev->GetChannel();
  uint32_t otherEnd = (channel->GetDevice(0) == dev) ? 1 : 0;
  Ptr<Node> nextHop = channel->GetDevice(otherEnd)->GetNode();
  uint32_t nextIf = channel->GetDevice(otherEnd)->GetIfIndex();
  Ipv4Address nextHopAddr =
      nextHop->GetObject<Ipv4>()->GetAddress(nextIf, 0).GetLocal();
  Ptr<Ipv4Route> route = Create<Ipv4Route>();
  route->SetOutputDevice(m_ipv4->GetNetDevice(port));
  route->SetGateway(nextHopAddr);
  route->SetSource(m_ipv4->GetAddress(port, 0).GetLocal());
  route->SetDestination(destAddress);
  return route;
}

void Ipv4LetFlowRouting::SetFlowletTimeout(Time timeout) {
  m_flowletTimeout = timeout;
}

Ptr<Ipv4Route> Ipv4LetFlowRouting::RouteOutput(Ptr<Packet> packet,
                                               const Ipv4Header &header,
                                               Ptr<NetDevice> oif,
                                               Socket::SocketErrno &sockerr) {
  NS_LOG_ERROR(
      this << " LetFlow routing is not support for local routing output");
  return 0;
}

bool Ipv4LetFlowRouting::RouteInput(
    Ptr<const Packet> p, const Ipv4Header &header, Ptr<const NetDevice> idev,
    UnicastForwardCallback ucb, MulticastForwardCallback mcb,
    LocalDeliverCallback lcb, ErrorCallback ecb) {
  NS_LOG_LOGIC(this << " RouteInput: " << p << "Ip header: " << header);

  NS_ASSERT(m_ipv4->GetInterfaceForDevice(idev) >= 0);

  Ptr<Packet> packet = ConstCast<Packet>(p);

  Ipv4Address destAddress = header.GetDestination();

  // LetFlow routing only supports unicast
  if (destAddress.IsMulticast() || destAddress.IsBroadcast()) {
    NS_LOG_ERROR(this << " LetFlow routing only supports unicast");
    std::cout<< "hits broadcast case";
    ecb(packet, header, Socket::ERROR_NOROUTETOHOST);
    return false;
  }

  // Check if input device supports IP forwarding
  uint32_t iif = m_ipv4->GetInterfaceForDevice(idev);
  if (m_ipv4->IsForwarding(iif) == false) {
    NS_LOG_ERROR(this << " Forwarding disabled for this interface");
    ecb(packet, header, Socket::ERROR_NOROUTETOHOST);
    return false;
  }

  // Packet arrival time
  Time now = Simulator::Now();

  // Log flows if logging is enabled.
  if (m_letFlowHistory.enabled) {
    // If the time between the last log and now is more than the logging
    // interval
    if (now - m_letFlowHistory.lastLog >= m_letFlowHistory.historyInterval) {
      std::vector<std::pair<Time, std::map<uint32_t, LetFlowFlowlet> > >
          *flowTables = &m_letFlowHistory.flowTableHistory;
      // Log current flowlet table
      flowTables->insert(flowTables->begin(),
                         std::make_pair(now, m_flowletTable));
      // Update last log time
      m_letFlowHistory.lastLog = now;
    }
  }

  // Extract the flow id
  uint32_t flowId = 0;
  FlowIdTag flowIdTag;
  bool flowIdFound = packet->PeekPacketTag(flowIdTag);
  if (!flowIdFound) {
    NS_LOG_ERROR(this << " LetFlow routing cannot extract the flow id");
    ecb(packet, header, Socket::ERROR_NOROUTETOHOST);
    return false;
  }
  flowId = flowIdTag.GetFlowId();

  Ipv4Address sourceAddress = header.GetSource();
  if (sourceAddress == m_attackerAddress) {
    m_attackerFlowId.insert(flowId);
  }

  std::vector<LetFlowRouteEntry> routeEntries =
      Ipv4LetFlowRouting::LookupLetFlowRouteEntries(destAddress);

  if (routeEntries.empty()) {
    NS_LOG_ERROR(this << " LetFlow routing cannot find routing entry");
    ecb(packet, header, Socket::ERROR_NOROUTETOHOST);
    return false;
  }

  uint32_t selectedPort;

  // If the flowlet table entry is valid, return the port
  std::map<uint32_t, struct LetFlowFlowlet>::iterator flowletItr =
      m_flowletTable.find(flowId);
  if (flowletItr != m_flowletTable.end()) {
    LetFlowFlowlet flowlet = flowletItr->second;
    if (now - flowlet.activeTime <= m_flowletTimeout) {
      // Do not forget to update the flowlet active time
      flowlet.activeTime = now;

      // Return the port information used for routing routine to select the port
      selectedPort = flowlet.port;

      Ptr<Ipv4Route> route =
          Ipv4LetFlowRouting::ConstructIpv4Route(selectedPort, destAddress);
      ucb(route, packet, header);

      m_flowletTable[flowId] = flowlet;

      return true;
    }
  }

  // Not hit. Random Select the Port
  int randPort = rand () % routeEntries.size();
  NS_LOG_LOGIC(this << "At Time: " << now.As(Time::MS) << " generated random number: " << 
                randPort << " for " << routeEntries.size() << " entries");
  selectedPort = routeEntries[randPort].port;

  LetFlowFlowlet flowlet;

  flowlet.port = selectedPort;
  flowlet.activeTime = now;

  Ptr<Ipv4Route> route =
      Ipv4LetFlowRouting::ConstructIpv4Route(selectedPort, destAddress);
  ucb(route, packet, header);

  m_flowletTable[flowId] = flowlet;

  return true;
}

void Ipv4LetFlowRouting::NotifyInterfaceUp(uint32_t interface) {}

void Ipv4LetFlowRouting::NotifyInterfaceDown(uint32_t interface) {}

void Ipv4LetFlowRouting::NotifyAddAddress(uint32_t interface,
                                          Ipv4InterfaceAddress address) {}

void Ipv4LetFlowRouting::NotifyRemoveAddress(uint32_t interface,
                                             Ipv4InterfaceAddress address) {}

void Ipv4LetFlowRouting::SetIpv4(Ptr<Ipv4> ipv4) {
  NS_LOG_LOGIC(this << "Setting up Ipv4: " << ipv4);
  NS_ASSERT(m_ipv4 == 0 && ipv4 != 0);
  m_ipv4 = ipv4;
}

void Ipv4LetFlowRouting::PrintRoutingTable(
    Ptr<OutputStreamWrapper> stream) const {}

void Ipv4LetFlowRouting::EnableLetFlowHistory(Ipv4Address attacker) {
  m_letFlowHistory.enabled = true;
  m_letFlowHistory.lastLog = Time(0);
  m_letFlowHistory.historyInterval = Time(MicroSeconds(50));
  m_attackerAddress = attacker;
}

LetFlowHistory Ipv4LetFlowRouting::GetLetFlowHistory() {
  return m_letFlowHistory;
}

// Returns a vector showing how many flows are on each port at every sample.
// First map is attacker flow id to port
// Seecond map is port to number of flows.
std::vector<std::pair<Time, std::pair<std::map<uint32_t, uint32_t>, std::map<uint32_t, int> > > >
Ipv4LetFlowRouting::ComputeNumberOfFlowsPerPort() {
  std::vector<std::pair<Time, std::map<uint32_t, LetFlowFlowlet> > >
      *tableHistory = &m_letFlowHistory.flowTableHistory;
  std::vector<std::pair<Time, std::pair<std::map<uint32_t, uint32_t>,
                                        std::map<uint32_t, int> > > >
      result;

  // Iterate over the history vector
  for (uint i = 0; i < tableHistory->size(); i++) {
    // Given a map from flowId to Flowlets, compute a map from port to frequency
    std::map<uint32_t, int> portFreq;
    std::map<uint32_t, uint32_t> attackerPorts;

    std::map<uint32_t, LetFlowFlowlet>::iterator it =
        (*tableHistory)[i].second.begin();
    while (it != (*tableHistory)[i].second.end()) {
      LetFlowFlowlet flowlet = it->second;
      uint32_t port = flowlet.port;

      // If the port is in the portFreq map, then increase flow frequency by 1
      std::map<uint32_t, int>::iterator portFreqIt = portFreq.find(port);
      if (portFreqIt != portFreq.end()) {
        portFreqIt->second = portFreqIt->second + 1;
      } else {
        // Otherwise initialize it to 1.
        portFreq.insert(std::pair<uint32_t, int>(port, 1));
      }
      if (m_attackerFlowId.count(it->first) != 0) {
        // If it->first is an attacker flow then add it's port to the result map.
        attackerPorts.insert(std::pair<uint32_t, int>(it->first, port));
      }
      it++;
    }
    // Store the new map in the result vector.
    result.insert(result.begin(),
                  std::make_pair((*tableHistory)[i].first,
                                 std::make_pair(attackerPorts, portFreq)));
  }
  return result;
}

void Ipv4LetFlowRouting::DoDispose(void) {
  m_ipv4 = 0;
  Ipv4RoutingProtocol::DoDispose();
}

}  // namespace ns3

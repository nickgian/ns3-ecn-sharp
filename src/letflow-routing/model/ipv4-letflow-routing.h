/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
#ifndef IPV4_LETFLOW_ROUTING_H
#define IPV4_LETFLOW_ROUTING_H

#include "ns3/data-rate.h"
#include "ns3/event-id.h"
#include "ns3/ipv4-header.h"
#include "ns3/ipv4-route.h"
#include "ns3/ipv4-routing-protocol.h"
#include "ns3/nstime.h"
#include "ns3/object.h"
#include "ns3/packet.h"

namespace ns3 {

struct LetFlowFlowlet {
  uint32_t port;
  Time activeTime;
};

struct LetFlowRouteEntry {
  Ipv4Address network;
  Ipv4Mask networkMask;
  uint32_t port;
};

struct LetFlowHistory {
  // A vector of how the flows are distributed over time.
  std::vector<std::pair<Time, std::map<uint32_t, LetFlowFlowlet> > >
      flowTableHistory;
  Time lastLog;
  bool enabled;
  // How often to log details about flows
  Time historyInterval;

  LetFlowHistory()
      : enabled(false),
        historyInterval(MicroSeconds(50))

  {}
};

class Ipv4LetFlowRouting : public Ipv4RoutingProtocol {
 public:
  Ipv4LetFlowRouting();
  ~Ipv4LetFlowRouting();

  static TypeId GetTypeId(void);

  void AddRoute(Ipv4Address network, Ipv4Mask networkMask, uint32_t port);

  /* Inherit From Ipv4RoutingProtocol */
  virtual Ptr<Ipv4Route> RouteOutput(Ptr<Packet> p, const Ipv4Header &header,
                                     Ptr<NetDevice> oif,
                                     Socket::SocketErrno &sockerr);
  virtual bool RouteInput(Ptr<const Packet> p, const Ipv4Header &header,
                          Ptr<const NetDevice> idev, UnicastForwardCallback ucb,
                          MulticastForwardCallback mcb,
                          LocalDeliverCallback lcb, ErrorCallback ecb);
  virtual void NotifyInterfaceUp(uint32_t interface);
  virtual void NotifyInterfaceDown(uint32_t interface);
  virtual void NotifyAddAddress(uint32_t interface,
                                Ipv4InterfaceAddress address);
  virtual void NotifyRemoveAddress(uint32_t interface,
                                   Ipv4InterfaceAddress address);
  virtual void SetIpv4(Ptr<Ipv4> ipv4);
  virtual void PrintRoutingTable(Ptr<OutputStreamWrapper> stream) const;

  virtual void DoDispose(void);

  std::vector<LetFlowRouteEntry> LookupLetFlowRouteEntries(Ipv4Address dest);
  Ptr<Ipv4Route> ConstructIpv4Route(uint32_t port, Ipv4Address destAddress);

  void SetFlowletTimeout(Time timeout);
  void EnableLetFlowHistory(Ipv4Address attacker);
  LetFlowHistory GetLetFlowHistory(void);

  // Returns  vector of time, port selected for attacker flow, and a map from
  // ports to flow counts.
  std::vector<std::pair<Time, std::pair<uint32_t, std::map<uint32_t, int> > > >
  ComputeNumberOfFlowsPerPort(void);

 private:
  // Flowlet Timeout
  Time m_flowletTimeout;

  // Ipv4 associated with this router
  Ptr<Ipv4> m_ipv4;

  // Flowlet Table: flowId to output port
  std::map<uint32_t, LetFlowFlowlet> m_flowletTable;

  // Route table
  std::vector<LetFlowRouteEntry> m_routeEntryList;

  // Log
  LetFlowHistory m_letFlowHistory;

  // Attacker's address for logging purposes
  Ipv4Address m_attackerAddress;

  // Attacker flow id
  uint32_t m_attackerFlowId;
};

}  // namespace ns3

#endif /* LETFLOW_ROUTING_H */

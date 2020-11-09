/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */

#include "ipv4-link-probe.h"

#include "link-monitor.h"
#include "ns3/config.h"
#include "ns3/flow-id-tag.h"
#include "ns3/ipv4-header.h"
#include "ns3/log.h"
#include "ns3/simulator.h"

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("Ipv4LinkProbe");

NS_OBJECT_ENSURE_REGISTERED (Ipv4LinkProbe);

TypeId
Ipv4LinkProbe::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::Ipv4LinkProbe")
      .SetParent<LinkProbe> ()
      .SetGroupName ("LinkMonitor");

  return tid;
}

Ipv4LinkProbe::Ipv4LinkProbe (Ptr<Node> node, Ptr<LinkMonitor> linkMonitor)
    :LinkProbe (linkMonitor),
     m_checkTime (MicroSeconds (50)),
     m_attackerAddress(Ipv4Address::GetZero())
{
  NS_LOG_FUNCTION (this);

  m_ipv4 = m_ipv4 = node->GetObject<Ipv4L3Protocol> ();

  // Notice, the interface at 0 is loopback, we simply ignore it
  for (uint32_t interface = 1; interface < m_ipv4->GetNInterfaces (); ++interface)
  {
    m_accumulatedTxBytes[interface] = 0;
    m_accumulatedDequeueBytes[interface] = 0;
    m_NPacketsInQueue[interface] = 0;
    m_NBytesInQueue[interface] = 0;
    m_NAttackerPacketsInQueue[interface] = 0;
    m_NPacketsInQueueDisc[interface] = 0;
    m_NBytesInQueueDisc[interface] = 0;

    std::map<uint32_t, std::pair<uint32_t, uint32_t> > flowTxMap;
    m_flowTx[interface] = flowTxMap;

    m_queueProbe[interface] = Create<Ipv4QueueProbe>();
    m_queueProbe[interface]->SetInterfaceId (interface);
    m_queueProbe[interface]->SetIpv4LinkProbe (this);

    std::ostringstream oss;
    oss << "/NodeList/" << node->GetId () << "/DeviceList/" << interface << "/TxQueue/Dequeue";
    Config::ConnectWithoutContext (oss.str (),
            MakeCallback (&Ipv4QueueProbe::DequeueLogger, m_queueProbe[interface]));

    std::ostringstream oss2;
    oss2 << "/NodeList/" << node->GetId () << "/DeviceList/" << interface << "/TxQueue/PacketsInQueue";
    Config::ConnectWithoutContext (oss2.str (),
            MakeCallback (&Ipv4QueueProbe::PacketsInQueueLogger, m_queueProbe[interface]));

    std::ostringstream oss3;
    oss3 << "/NodeList/" << node->GetId () << "/DeviceList/" << interface << "/TxQueue/BytesInQueue";
    Config::ConnectWithoutContext (oss3.str (),
            MakeCallback (&Ipv4QueueProbe::BytesInQueueLogger, m_queueProbe[interface]));

    std::ostringstream oss4;
    oss4 << "/NodeList/" << node->GetId () << "/$ns3::TrafficControlLayer/RootQueueDiscList/" << interface << "/PacketsInQueue";
    Config::ConnectWithoutContext (oss4.str (),
            MakeCallback (&Ipv4QueueProbe::PacketsInQueueDiscLogger, m_queueProbe[interface]));

    std::ostringstream oss5;
    oss5 << "/NodeList/" << node->GetId () << "/$ns3::TrafficControlLayer/RootQueueDiscList/" << interface << "/BytesInQueue";
    Config::ConnectWithoutContext (oss5.str (),
            MakeCallback (&Ipv4QueueProbe::BytesInQueueDiscLogger, m_queueProbe[interface]));
  }

  if (!m_ipv4->TraceConnectWithoutContext ("Tx",
              MakeCallback (&Ipv4LinkProbe::TxLogger, this)))
  {
    NS_FATAL_ERROR ("trace fail");
  }

}

Ipv4LinkProbe::Ipv4LinkProbe (Ptr<Node> node, Ptr<LinkMonitor> linkMonitor, Ipv4Address attackerAddress)
    :LinkProbe (linkMonitor),
     m_checkTime (MicroSeconds (50)),
     m_attackerAddress (attackerAddress)
{
  NS_LOG_FUNCTION (this);

  m_ipv4 = m_ipv4 = node->GetObject<Ipv4L3Protocol> ();

  // Notice, the interface at 0 is loopback, we simply ignore it
  for (uint32_t interface = 1; interface < m_ipv4->GetNInterfaces (); ++interface)
  {
    m_accumulatedTxBytes[interface] = 0;
    m_accumulatedDequeueBytes[interface] = 0;
    m_NPacketsInQueue[interface] = 0;
    m_NBytesInQueue[interface] = 0;
    m_NAttackerPacketsInQueue[interface] = 0;
    m_NPacketsInQueueDisc[interface] = 0;
    m_NBytesInQueueDisc[interface] = 0;
    std::map<uint32_t, std::pair<uint32_t, uint32_t> > flowTxMap;
    m_flowTx[interface] = flowTxMap;

    m_queueProbe[interface] = Create<Ipv4QueueProbe> ();
    m_queueProbe[interface]->SetInterfaceId (interface);
    m_queueProbe[interface]->SetIpv4LinkProbe (this);

    std::ostringstream oss;
    oss << "/NodeList/" << node->GetId () << "/DeviceList/" << interface << "/TxQueue/Dequeue";
    Config::ConnectWithoutContext (oss.str (),
            MakeCallback (&Ipv4QueueProbe::DequeueLogger, m_queueProbe[interface]));

    std::ostringstream oss2;
    oss2 << "/NodeList/" << node->GetId () << "/DeviceList/" << interface << "/TxQueue/PacketsInQueue";
    Config::ConnectWithoutContext (oss2.str (),
            MakeCallback (&Ipv4QueueProbe::PacketsInQueueLogger, m_queueProbe[interface]));

    std::ostringstream oss3;
    oss3 << "/NodeList/" << node->GetId () << "/DeviceList/" << interface << "/TxQueue/BytesInQueue";
    Config::ConnectWithoutContext (oss3.str (),
            MakeCallback (&Ipv4QueueProbe::BytesInQueueLogger, m_queueProbe[interface]));

    std::ostringstream oss4;
    oss4 << "/NodeList/" << node->GetId () << "/$ns3::TrafficControlLayer/RootQueueDiscList/" << interface << "/PacketsInQueue";
    Config::ConnectWithoutContext (oss4.str (),
            MakeCallback (&Ipv4QueueProbe::PacketsInQueueDiscLogger, m_queueProbe[interface]));

    std::ostringstream oss5;
    oss5 << "/NodeList/" << node->GetId () << "/$ns3::TrafficControlLayer/RootQueueDiscList/" << interface << "/BytesInQueue";
    Config::ConnectWithoutContext (oss5.str (),
            MakeCallback (&Ipv4QueueProbe::BytesInQueueDiscLogger, m_queueProbe[interface]));

    std::ostringstream oss6;
    oss6 << "/NodeList/" << node->GetId () << "/DeviceList/" << interface << "/TxQueue/Enqueue";
    Config::ConnectWithoutContext (oss.str (),
            MakeCallback (&Ipv4QueueProbe::EnqueueLogger, m_queueProbe[interface]));

  }

  if (!m_ipv4->TraceConnectWithoutContext ("Tx",
              MakeCallback (&Ipv4LinkProbe::TxLogger, this)))
  {
    NS_FATAL_ERROR ("trace fail");
  }
}

void
Ipv4LinkProbe::SetDataRateAll (DataRate dataRate)
{
  for (uint32_t interface = 1; interface < m_ipv4->GetNInterfaces (); ++interface)
  {
    m_dataRate[interface] = dataRate;
  }
}

void
Ipv4LinkProbe::TxLogger (Ptr<const Packet> packet, Ptr<Ipv4> ipv4, uint32_t interface)
{
  uint32_t size = packet->GetSize ();
  NS_LOG_LOGIC ("Trace " << size << " bytes TX on port: " << interface);
  m_accumulatedTxBytes[interface] = m_accumulatedTxBytes[interface] + size;

  // Per flow logging
  FlowIdTag flowIdTag;
  bool flowIdFound = packet->PeekPacketTag(flowIdTag);
  std::map<uint32_t, std::map<uint32_t, std::pair<uint32_t, uint32_t> > >::iterator flowTxIt = m_flowTx.find(interface);

  if (!flowIdFound) {
    NS_LOG_ERROR(this << " Cannot extract the flow id");
  }
  else {
    uint32_t flowId = flowIdTag.GetFlowId();
    NS_LOG_LOGIC(this << "Logging packet for FlowId:" << flowId);
    std::map<uint32_t, std::pair<uint32_t, uint32_t> >::iterator it = flowTxIt->second.find(flowId);
    if (it != flowTxIt->second.end()) {
      NS_LOG_LOGIC(this << "FlowId found, bytes: " << it->second.first +size);
      it -> second = std::make_pair(it->second.first + size, it->second.second + 1);
    } else {
      NS_LOG_LOGIC(this << "No entry for this flowId");
      flowTxIt->second.insert(it, std::map<uint32_t, std::pair<uint32_t, uint32_t> >::value_type(flowId, 
              std::make_pair(size, 1)));
    }
    NS_LOG_LOGIC(this << " TX packets in interface " << interface << "for " << flowId << " are " << it->second.second);
  }

  // std::map<uint32_t,
  //          std::map<uint32_t, std::pair<uint32_t, uint32_t> > >::iterator
  //     flowTxIt = m_flowTx.find(interface);

  // if (!flowIdFound) {
  //   NS_LOG_ERROR(this << " Cannot extract the flow id");
  // } else {
  //   uint32_t flowId = flowIdTag.GetFlowId();
  //   NS_LOG_LOGIC(this << "Logging packet for FlowId:" << flowId);
  //   std::map<uint32_t, std::pair<uint32_t, uint32_t> >::iterator it =
  //       flowTxIt->second.find(flowId);
  //   if (it != flowTxIt->second.end()) {
  //     NS_LOG_LOGIC(this << "FlowId found, bytes: " << it->second.first + size);
  //     it->second =
  //         std::make_pair(it->second.first + size, it->second.second + 1);
  //   } else {
  //     NS_LOG_LOGIC(this << "No entry for this flowId");
  //     flowTxIt->second.insert(
  //         it, std::map<uint32_t, std::pair<uint32_t, uint32_t> >::value_type(
  //                 flowId, std::make_pair(size, 1)));
  //   }
  //   NS_LOG_LOGIC(this << " TX packets in interface " << interface << "for "
  //                     << flowId << " are " << it->second.second);
  // }
}

void
Ipv4LinkProbe::DequeueLogger (Ptr<const Packet> packet, uint32_t interface)
{
  uint32_t size = packet->GetSize ();
  NS_LOG_LOGIC ("Trace " << size << " bytes dequeued on port: " << interface);
  m_accumulatedDequeueBytes[interface] = m_accumulatedDequeueBytes[interface] + size;

  // Also reduce the number of attacker packets when one gets dequeued.
  if (!m_attackerAddress.IsEqual(Ipv4Address::GetZero())) { 
    Ptr<Packet> copy = packet->Copy ();
    Ipv4Header iph;
    copy->RemoveHeader (iph);

    std::stringstream log;
    iph.GetDestination().Print(log);
    log << "dequeued packet with source";
    NS_LOG_LOGIC (log.str());
    if ((iph.GetSource().IsEqual(m_attackerAddress)))
    {  
      NS_LOG_LOGIC ("Dequed attacker packet!");
      m_NAttackerPacketsInQueue[interface] = m_NAttackerPacketsInQueue[interface] - 1;
    }
  }
}

void
Ipv4LinkProbe::EnqueueLogger (Ptr<const Packet> packet, uint32_t interface)
{
  NS_LOG_LOGIC ("Packet queued on port: " << interface);
  Ptr<Packet> copy = packet->Copy ();
  Ipv4Header iph;
  copy->RemoveHeader (iph);
  if (iph.GetSource().IsEqual(m_attackerAddress))
  {  
    NS_LOG_LOGIC ("Logged as attacker packet!");
    m_NAttackerPacketsInQueue[interface] = m_NAttackerPacketsInQueue[interface] + 1;
  }
}

void
Ipv4LinkProbe::PacketsInQueueLogger (uint32_t NPackets, uint32_t interface)
{
  NS_LOG_LOGIC ("Packets in queue are now: " << NPackets);
  m_NPacketsInQueue[interface] = NPackets;
}

void
Ipv4LinkProbe::BytesInQueueLogger (uint32_t NBytes, uint32_t interface)
{
  NS_LOG_LOGIC ("Bytes in queue are now: " << NBytes);
  m_NBytesInQueue[interface] = NBytes;
}

void
Ipv4LinkProbe::PacketsInQueueDiscLogger (uint32_t NPackets, uint32_t interface)
{
  NS_LOG_LOGIC ("Packets in queue are now: " << NPackets);
  m_NPacketsInQueueDisc[interface] = NPackets;
}

void
Ipv4LinkProbe::BytesInQueueDiscLogger (uint32_t NBytes, uint32_t interface)
{
  NS_LOG_LOGIC ("Bytes in queue are now: " << NBytes);
  m_NBytesInQueueDisc[interface] = NBytes;
}

void
Ipv4LinkProbe::CheckCurrentStatus ()
{
  for (uint32_t interface = 1; interface < m_ipv4->GetNInterfaces (); ++interface)
  {
    uint64_t lastTxBytes = 0;
    uint64_t lastDequeueBytes = 0;

    std::map<uint32_t, std::vector<struct LinkProbe::LinkStats> >::iterator itr = m_stats.find (interface);
    if (itr == m_stats.end ())
    {
      struct LinkProbe::LinkStats newStats;
      newStats.checkTime = Simulator::Now ();
      newStats.accumulatedTxBytes = m_accumulatedTxBytes[interface];
      newStats.txLinkUtility =
          Ipv4LinkProbe::GetLinkUtility (interface, m_accumulatedTxBytes[interface] - lastTxBytes, m_checkTime);
      newStats.accumulatedDequeueBytes = m_accumulatedDequeueBytes[interface];
      newStats.dequeueLinkUtility =
          Ipv4LinkProbe::GetLinkUtility (interface, m_accumulatedDequeueBytes[interface] - lastDequeueBytes, m_checkTime);
      newStats.packetsInQueue = m_NPacketsInQueue[interface];
      newStats.bytesInQueue = m_NBytesInQueue[interface];
      newStats.attackerPacketsInQueue = m_NAttackerPacketsInQueue[interface];
      newStats.packetsInQueueDisc = m_NPacketsInQueueDisc[interface];
      newStats.bytesInQueueDisc = m_NBytesInQueueDisc[interface];
      newStats.txFlow = m_flowTx[interface];
      std::map<uint32_t, std::pair<uint32_t, uint32_t> > flowTxMap;
      m_flowTx[interface] = flowTxMap;
      std::vector<struct LinkProbe::LinkStats> newVector;
      newVector.push_back (newStats);
      m_stats[interface] = newVector;
    }
    else
    {
      lastTxBytes = (itr->second).back ().accumulatedTxBytes;
      lastDequeueBytes = (itr->second).back ().accumulatedDequeueBytes;
      struct LinkProbe::LinkStats newStats;
      newStats.checkTime = Simulator::Now ();
      newStats.accumulatedTxBytes = m_accumulatedTxBytes[interface];
      newStats.txLinkUtility =
          Ipv4LinkProbe::GetLinkUtility (interface, m_accumulatedTxBytes[interface] - lastTxBytes, m_checkTime);
      newStats.accumulatedDequeueBytes = m_accumulatedDequeueBytes[interface];
      newStats.dequeueLinkUtility =
          Ipv4LinkProbe::GetLinkUtility (interface, m_accumulatedDequeueBytes[interface] - lastDequeueBytes, m_checkTime);
      newStats.packetsInQueue = m_NPacketsInQueue[interface];
      newStats.bytesInQueue = m_NBytesInQueue[interface];
      newStats.attackerPacketsInQueue = m_NAttackerPacketsInQueue[interface];
      newStats.packetsInQueueDisc = m_NPacketsInQueueDisc[interface];
      newStats.bytesInQueueDisc = m_NPacketsInQueueDisc[interface];
      newStats.txFlow = m_flowTx[interface];
      std::map<uint32_t, std::pair<uint32_t, uint32_t> > flowTxMap;
      m_flowTx[interface] = flowTxMap;
      (itr->second).push_back (newStats);
    }
  }

  m_checkEvent = Simulator::Schedule (m_checkTime, &Ipv4LinkProbe::CheckCurrentStatus, this);

}

void
Ipv4LinkProbe::Start ()
{
  m_checkEvent = Simulator::Schedule (m_checkTime, &Ipv4LinkProbe::CheckCurrentStatus, this);
}

void
Ipv4LinkProbe::Stop ()
{
  m_checkEvent.Cancel ();
}

double
Ipv4LinkProbe::GetLinkUtility (uint32_t interface, uint64_t bytes, Time time)
{
  std::map<uint32_t, DataRate>::iterator itr = m_dataRate.find (interface);
  if (itr == m_dataRate.end ())
  {
    return 0.0f;
  }

  return static_cast<double> (bytes * 8) / ((itr->second).GetBitRate () * time.GetSeconds ());
}

void
Ipv4LinkProbe::SetCheckTime (Time checkTime)
{
  m_checkTime = checkTime;
}

}

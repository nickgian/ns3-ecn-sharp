#include <assert.h>

#include <algorithm>  // std::max
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <utility>
#include <vector>

#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/internet-module.h"
#include "ns3/ipv4-clove.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/ipv4-letflow-routing-helper.h"
#include "ns3/ipv4-static-routing-helper.h"
#include "ns3/ipv4-xpath-routing-helper.h"
#include "ns3/link-monitor-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/tcp-resequence-buffer.h"
#include "ns3/traffic-control-module.h"

// The CDF in TrafficGenerator
extern "C"
{
#include "cdf.h"
}

#define LINK_CAPACITY_BASE 1000000000 // 1Gbps
#define BUFFER_SIZE 600               // 250 packets

#define RED_QUEUE_MARKING 65 // 65 Packets (available only in DcTcp)

// The flow port range, each flow will be assigned a random port number within
// this range
#define PORT_START 10000
#define PORT_END 50000

#define START_TIME 0.0
#define END_TIME 10.0

// Adopted from the simulation from WANG PENG
// Acknowledged to
// https://williamcityu@bitbucket.org/williamcityu/2016-socc-simulation.git
#define PACKET_SIZE 1400

#define PRESTO_RATIO 10

    using namespace ns3;

NS_LOG_COMPONENT_DEFINE("LetFlowConvergence");

enum RunMode
{
  ECMP,
  LetFlow
};

template <typename T>
T rand_range(T min, T max)
{
  return min + ((double)max - min) * rand() / RAND_MAX;
}

void attackerInstallOnOff(
    NodeContainer fromServers, NodeContainer destServers,
    std::vector<std::pair<Ipv4Address, uint32_t> > toAddresses, int i,
    uint32_t port, int destIndex, double start_time, double end_time,
    uint32_t flowSize, uint32_t offTime, uint32_t onTime,
    std::string attackerProt, int rate, int attackerPacketSize)
{
  std::stringstream prot;
  prot << "ns3::" << attackerProt << "SocketFactory";

  std::cout << prot.str();
  OnOffHelper source(prot.str(),
                     InetSocketAddress(toAddresses[destIndex].first, port));

  PacketSinkHelper sink(prot.str(),
                        InetSocketAddress(Ipv4Address::GetAny(), port));

  /* Compute off time */
  double offTimed = (double(offTime) / 1000000);

  std::stringstream offTimeStr;

  offTimeStr << "ns3::ConstantRandomVariable[Constant=" << offTimed << "]";

  /* Compute on time */
  double onTimed = (double(onTime) / 1000000);

  printf("%f ", offTimed);
  printf("%f", onTimed);
  std::stringstream onTimeStr;
  onTimeStr << "ns3::ConstantRandomVariable[Constant=" << onTimed << "]";

  std::stringstream rateStr;
  rateStr << rate << "Mbps";

  source.SetAttribute("PacketSize", UintegerValue(attackerPacketSize));
  source.SetAttribute("MaxBytes", UintegerValue(flowSize));
  source.SetAttribute("OnTime", StringValue(onTimeStr.str()));
  source.SetAttribute("OffTime", StringValue(offTimeStr.str()));
  source.SetAttribute("DataRate", DataRateValue(DataRate(rateStr.str())));

  // Install apps
  ApplicationContainer sourceApp = source.Install(fromServers.Get(i));
 
  sourceApp.Start(MicroSeconds(start_time));
  sourceApp.Stop(Seconds(end_time));

  // Install packet sinks
  ApplicationContainer sinkApp = sink.Install(destServers.Get(destIndex));
  sinkApp.Start(MicroSeconds(start_time));
  sinkApp.Stop(Seconds(end_time));
}

void install_applications(
    NodeContainer fromServers, NodeContainer destServers, int SERVER_COUNT,
    std::vector<std::pair<Ipv4Address, uint32_t> > toAddresses,
    double attacker_start, double end_time, uint32_t flowSize, int &flowCount,
    std::set<int> compromised, uint32_t offTime, uint32_t onTime,
    std::string attackerProt, std::string attackerApp, int rate,
    int hostileFlows, int attackerPacketSize, int hostileFlowSize)
{
  NS_LOG_INFO("Install applications:");
  for (int i = 0; i < SERVER_COUNT; i++)
  {
    flowCount++;
    uint16_t port = rand_range(PORT_START, PORT_END);
    // uint16_t port = PORT_START + i;
    int destIndex = rand_range(0, SERVER_COUNT - 1);

    // Slightly change the start time
 
     Time start_time = MicroSeconds(START_TIME);
     
        // Time start_time = MicroSeconds(rand_range(0, 50) + START_TIME);

    // Each server sends a flow

    if (compromised.count(i))
    {
      if (attackerApp.compare("Bulk") == 0)
      {
        BulkSendHelper source(
            "ns3::TcpSocketFactory",
            InetSocketAddress(toAddresses[destIndex].first, port));

        // onTime is treated as a number of packets in the TCP case.
        source.SetAttribute("SendSize", UintegerValue(PACKET_SIZE));
        source.SetAttribute("MaxBytes", UintegerValue(hostileFlowSize));
        source.SetAttribute("DelayThresh", UintegerValue(onTime));
        source.SetAttribute("DelayTime", TimeValue(MicroSeconds(offTime)));

        // Install apps
        ApplicationContainer sourceApp = source.Install(fromServers.Get(i));
        sourceApp.Start(start_time);
        sourceApp.Stop(Seconds(end_time));

        // Install packet sinks
        PacketSinkHelper sink("ns3::TcpSocketFactory",
                              InetSocketAddress(Ipv4Address::GetAny(), port));
        ApplicationContainer sinkApp = sink.Install(destServers.Get(destIndex));
        sinkApp.Start(start_time);
        sinkApp.Stop(Seconds(end_time));
      }
      else
      {
        
        //TODO: redo this whole thing, allow multiple attacker flows.
        // Do consider attacker start time for the first flow, if it's just one flow.
        if (hostileFlows == 1) {
        attackerInstallOnOff(fromServers, destServers, toAddresses, i, port,
                             destIndex, START_TIME + attacker_start, end_time, hostileFlowSize,
                             offTime, onTime, attackerProt, rate,
                             attackerPacketSize);
        }
        else { // Otherwise ignore it and just keep it for the second flow.
        attackerInstallOnOff(fromServers, destServers, toAddresses, i, port,
                             destIndex, START_TIME, end_time, hostileFlowSize,
                             offTime, onTime, attackerProt, rate,
                             attackerPacketSize);
        }

        if (hostileFlows > 1)
        {
          // Second flow
          port = rand_range(PORT_START, PORT_END);
          // uint16_t port = PORT_START + i;
          destIndex = rand_range(0, SERVER_COUNT - 1);

          attackerInstallOnOff(fromServers, destServers, toAddresses, i, port,
                               destIndex, START_TIME + attacker_start, end_time,
                               hostileFlowSize, offTime, onTime, attackerProt,
                               rate, attackerPacketSize);
          flowCount++;
        }
      }
    }
    else
    {
      // If it's  not an attacker
      BulkSendHelper source(
          "ns3::TcpSocketFactory",
          InetSocketAddress(toAddresses[destIndex].first, port));

      source.SetAttribute("SendSize", UintegerValue(PACKET_SIZE));
      source.SetAttribute("MaxBytes", UintegerValue(flowSize));

      // Install apps
      ApplicationContainer sourceApp = source.Install(fromServers.Get(i));
      sourceApp.Start(start_time);
      sourceApp.Stop(Seconds(end_time));

      // Install packet sinks
      PacketSinkHelper sink("ns3::TcpSocketFactory",
                            InetSocketAddress(Ipv4Address::GetAny(), port));
      ApplicationContainer sinkApp = sink.Install(destServers.Get(destIndex));
      sinkApp.Start(start_time);
      sinkApp.Stop(Seconds(end_time));
    }

    NS_LOG_INFO("\tFlow from server: "
                << i << " to server: " << destIndex << " on port: " << port
                << " [start time: " << start_time << "]");
  }
}

/* Parsing the load balancer to use */
RunMode parseRunMode(std::string runModeStr)
{
  if (runModeStr.compare("ECMP") == 0)
  {
    return ECMP;
  }
  else if (runModeStr.compare("LetFlow") == 0)
  {
    return LetFlow;
  }
  else
  {
    NS_LOG_ERROR("The running mode should be LetFlow or ECMP");
    exit(0);
  }
}

/* Output log file relating ports to flows. Takes as input a filename, a vector
  of time and a map from flowId to Time (duration of flowlet gap that caused
  rerouting), a vector of pairs of time of sample, a pair of two maps:
  - the first one maps attacker flow Ids to ports
  - and the second one maps ports to number of flows on them. and a set of ports
    that we want to log.
*/
void outputFlowLog(
    std::string filename,
    std::vector<std::pair<Time, std::map<uint32_t, std::pair<Time, bool> > > > flowGapHistory,
    std::vector<std::pair<
        Time, std::pair<std::map<uint32_t, uint32_t>, std::map<uint32_t, int> > > >
        flowsPerPort,
    std::set<uint32_t> ports) {
  std::ofstream logfile;
  logfile.open(filename.c_str());
  std::vector<std::pair<Time, std::pair<std::map<uint32_t, uint32_t>,
                                             std::map<uint32_t, int> > > >::
           const_iterator i = flowsPerPort.begin();

  // std::vector<std::pair<Time, std::map<uint32_t, std::pair<Time, bool> > > > ::
  //          const_iterator fh = flowGapHistory.begin();

  // while (fh != flowGapHistory.end()) {
  //   logfile << fh->first.As(Time::MS);
  //   for (std::map<uint32_t, std::pair<Time, bool> >::const_iterator fhj = (fh->second).begin();
  //        fhj != (fh->second).end(); ++fhj)
  //   {
  //       // Using ':' for flow to flowlet gap info.
  //       logfile << ", " << fhj->first << ":" << fhj->second.first.As(Time::US) << ":" << fhj->second.second;
  //   }
  //   logfile << "\n"; 
  //   ++fh;
  //  }

 while (i != flowsPerPort.end())
  {
    // Print time
    logfile << i->first.As(Time::MS);
    // Attacker's flows selected ports

    for (std::map<uint32_t, uint32_t>::const_iterator j =
             (i->second.first).begin();
         j != (i->second.first).end(); ++j) {
      // Using tilde for attacker ports
      logfile << ", " << j->first << "~" << j->second;
    }

    // Flows per port
    for (std::map<uint32_t, int>::const_iterator j = (i->second.second).begin();
         j != (i->second.second).end(); ++j)
    {
      if (ports.count(j->first) != 0)
      {
        // Using ':' for port to flows.
        logfile << ", " << j->first << ":" << j->second;
      }
    }
   // Print flowlet gap information
  //  if (fh != flowGapHistory.end() && fh->first == i->first) {
  //   for (std::map<uint32_t, Time>::const_iterator fhj = (fh->second).begin();
  //        fhj != (fh->second).end(); ++fhj)
  //   {
  //       // Using '-' for flow to flowlet gap info.
  //       logfile << ", " << fhj->first << "-" << fhj->second;
  //   } 
  //   ++fh;
  //  }
    logfile << "\n";
    ++i;
  }
  logfile.close();
}

int main(int argc, char *argv[])
{
#if 1
  LogComponentEnable("LetFlowConvergence", LOG_LEVEL_INFO);
#endif

  // Command line parameters parsing
  std::string id = "0";
  std::string runModeStr = "LetFlow";
  unsigned randomSeed = 0;
  std::string cdfFileName = "";
  double load = 0.0;
  std::string transportProt = "Tcp";
  std::string attackerProt = "Tcp";
  std::string attackerApp = "Bulk";

  uint32_t linkLatency = 10;

  int SERVER_COUNT = 8;

  uint64_t linkOneCapacity = 5;
  uint64_t linkTwoCapacity = 20;
  uint64_t linkThreeCapacity = 10;

  uint32_t letFlowFlowletTimeout = 500;

  bool hostile = false;

  uint32_t flowSize = 2000000000; // 2 Gbps

  uint32_t hostileFlowSize = 1000000000;  // 1 Gbps

  uint32_t offTime = 0;
  uint32_t onTime = END_TIME * 1000000;

  uint32_t attackerStart = 0;

  int attackerRate = 2000; // 2Gbps

  int attackerPacketSize = PACKET_SIZE;

  int hostileFlows = 1;

  // The simulation starting and ending time
  double startTime = START_TIME;
  double endTime = END_TIME;

  int buffer_size = BUFFER_SIZE;

  // Ratio of large flows
  double largeFlowRatio = 0.5;
  double smallFlowRatio = 1.0 - largeFlowRatio;


  CommandLine cmd;
  cmd.AddValue("ID", "Running ID", id);
  cmd.AddValue("StartTime", "Start time of the simulation", startTime);
  cmd.AddValue("EndTime", "End time of the simulation", endTime);
  cmd.AddValue("runMode", "Running mode of this simulation: ECMP, LetFlow",
               runModeStr);
  cmd.AddValue("randomSeed", "Random seed, 0 for random generated", randomSeed);
  cmd.AddValue("servers", "Server count", SERVER_COUNT);
  cmd.AddValue("transportProt", "Transport protocol to use: Tcp, DcTcp",
               transportProt);
  cmd.AddValue("linkLatency", "Link latency, should be in MicroSeconds",
               linkLatency);

  cmd.AddValue("linkOneCapacity", "Link one capacity in Gbps", linkOneCapacity);
  cmd.AddValue("linkTwoCapacity", "Link two capacity in Gbps", linkTwoCapacity);
  cmd.AddValue("linkThreeCapacity", "Link two capacity in Gbps", linkThreeCapacity);

  cmd.AddValue("letFlowFlowletTimeout", "Flowlet timeout in LetFlow",
               letFlowFlowletTimeout);

  cmd.AddValue("hostile", "Whether there are compromised hosts", hostile);
  cmd.AddValue("flowSize", "The size of the flow hosts generate", flowSize);
  cmd.AddValue("attackerOnTime",
               "How long the attacker should send packets until he pauses in "
               "Microseconds (OnOff), or number of packets until pause (Bulk)",
               onTime);
  cmd.AddValue("attackerOffTime",
               "The time for an attacker pause, in Microseconds", offTime);
  cmd.AddValue("attackerRate", "Attacker rate of transmission", attackerRate);
  cmd.AddValue("hostileFlows", "Number of hostile flows", hostileFlows);
  cmd.AddValue("attackerProt",
               "What protocol the attacker is using, currently: Tcp or Udp.",
               attackerProt);
  cmd.AddValue("attackerApp",
               "What application is the attacker using (Bulk or OnOff)",
               attackerApp);
  cmd.AddValue("attackerPacketSize", "The size of the attacker packets",
               attackerPacketSize);
  cmd.AddValue("attackerStart",
               "Start time for the attacker's second flow, if any",
               attackerStart);
  cmd.AddValue("buffer",
               "The queue size",
               buffer_size);
  cmd.AddValue("hostileFlowSize", "Size of hostile flows", hostileFlowSize);
  cmd.AddValue("largeFlowRatio", "Ratio of large flows in all generated flows", largeFlowRatio);
  cmd.Parse(argc, argv);

  uint64_t LINK_ONE_CAPACITY   = linkOneCapacity * LINK_CAPACITY_BASE;
  uint64_t LINK_TWO_CAPACITY   = linkTwoCapacity * LINK_CAPACITY_BASE;
  uint16_t LINK_THREE_CAPACITY = linkThreeCapacity * LINK_CAPACITY_BASE;
  Time LINK_LATENCY = MicroSeconds(linkLatency);

  RunMode runMode = parseRunMode(runModeStr);

  // This is just reusing the RunMode type, but in the future we can/should
  // set up different attacker modes. RunMode attackerMode =
  // parseRunMode(attackerModeStr);

  if (load < 0.0 || load >= 1.0)
  {
    NS_LOG_ERROR("The network load should within 0.0 and 1.0");
    return 0;
  }

  if (largeFlowRatio < 0.0 || largeFlowRatio >= 1.0)
  {
    NS_LOG_ERROR("Ratio of large flows should be between 0.0 and 1.0");
    return 0;
  }
  smallFlowRatio = 1.0 - largeFlowRatio;
  // this line is just to make sure ns3 doesnt throw any warnings, still working on the large+small flow mix.
  smallFlowRatio++;

  if (transportProt.compare("DcTcp") == 0)
  {
    NS_LOG_INFO("Enabling DcTcp");
    Config::SetDefault("ns3::TcpL4Protocol::SocketType",
                       TypeIdValue(TcpDCTCP::GetTypeId()));
    Config::SetDefault("ns3::RedQueueDisc::Mode",
                       StringValue("QUEUE_MODE_BYTES"));
    Config::SetDefault("ns3::RedQueueDisc::MeanPktSize",
                       UintegerValue(PACKET_SIZE));
    Config::SetDefault("ns3::RedQueueDisc::QueueLimit",
                       UintegerValue(buffer_size * PACKET_SIZE));
    // Config::SetDefault ("ns3::QueueDisc::Quota", UintegerValue
    // (BUFFER_SIZE));
    Config::SetDefault("ns3::RedQueueDisc::Gentle", BooleanValue(false));
  }

  NS_LOG_INFO("Config parameters");
  Config::SetDefault("ns3::TcpSocket::SegmentSize", UintegerValue(PACKET_SIZE));
  Config::SetDefault("ns3::TcpSocket::DelAckCount", UintegerValue(0));
  Config::SetDefault("ns3::TcpSocket::ConnTimeout", TimeValue(MilliSeconds(5)));
  Config::SetDefault("ns3::TcpSocket::InitialCwnd", UintegerValue(10));
  Config::SetDefault("ns3::TcpSocketBase::MinRto", TimeValue(MilliSeconds(5)));
  Config::SetDefault("ns3::TcpSocketBase::ClockGranularity",
                     TimeValue(MicroSeconds(100)));
  Config::SetDefault("ns3::RttEstimator::InitialEstimation",
                     TimeValue(MicroSeconds(80)));
  Config::SetDefault("ns3::TcpSocket::SndBufSize", UintegerValue(160000000));
  Config::SetDefault("ns3::TcpSocket::RcvBufSize", UintegerValue(160000000));

  NS_LOG_INFO("Create nodes");

  // Two leaves
  Ptr<Node> leaf0 = CreateObject<Node>();
  Ptr<Node> leaf1 = CreateObject<Node>();

  // Two spines
  Ptr<Node> spine0 = CreateObject<Node>();
  Ptr<Node> spine1 = CreateObject<Node>();

  // Additional spine for >2 paths
  Ptr<Node> spine2 = CreateObject<Node>();

  // Some number of servers connecting to the leaves
  NodeContainer servers0;
  servers0.Create(SERVER_COUNT);

  NodeContainer servers1;
  servers1.Create(SERVER_COUNT);

  NS_LOG_INFO("Install Internet stacks");
  InternetStackHelper internet;
  Ipv4StaticRoutingHelper staticRoutingHelper;
  Ipv4GlobalRoutingHelper globalRoutingHelper;
  Ipv4LetFlowRoutingHelper letFlowRoutingHelper;

  if (runMode == LetFlow)
  {
    internet.SetRoutingHelper(staticRoutingHelper);
    internet.Install(servers0);
    internet.Install(servers1);

    internet.SetRoutingHelper(letFlowRoutingHelper);
    internet.Install(leaf0);
    internet.Install(leaf1);
    internet.Install(spine0);
    internet.Install(spine1);
    // extra spine
    internet.Install(spine2);
  }
  else if (runMode == ECMP)
  {
    internet.SetRoutingHelper(globalRoutingHelper);
    Config::SetDefault("ns3::Ipv4GlobalRouting::PerflowEcmpRouting",
                       BooleanValue(true));
    internet.Install(servers0);
    internet.Install(servers1);
    internet.Install(leaf0);
    internet.Install(leaf1);
    internet.Install(spine0);
    internet.Install(spine1);
    // extra spine
    internet.Install(spine2);
  }

  NS_LOG_INFO("Install channels and assign addresses");

  PointToPointHelper p2p;
  Ipv4AddressHelper ipv4;

  // Setting switches
  p2p.SetChannelAttribute("Delay", TimeValue(LINK_LATENCY));
  p2p.SetQueue("ns3::DropTailQueue", "MaxPackets", UintegerValue(buffer_size));

  // Connecting to Spine 0
  p2p.SetDeviceAttribute("DataRate",
                         DataRateValue(DataRate(LINK_ONE_CAPACITY)));
  NodeContainer leaf0_spine0 = NodeContainer(leaf0, spine0);
  NetDeviceContainer netdevice_leaf0_spine0 = p2p.Install(leaf0_spine0);
  NodeContainer leaf1_spine0 = NodeContainer(leaf1, spine0);
  NetDeviceContainer netdevice_leaf1_spine0 = p2p.Install(leaf1_spine0);

  // Does changing rate here work or do I need another p2p helper?
  p2p.SetDeviceAttribute("DataRate",
                         DataRateValue(DataRate(LINK_TWO_CAPACITY)));
  NodeContainer leaf0_spine1 = NodeContainer(leaf0, spine1);
  NetDeviceContainer netdevice_leaf0_spine1 = p2p.Install(leaf0_spine1);
  NodeContainer leaf1_spine1 = NodeContainer(leaf1, spine1);
  NetDeviceContainer netdevice_leaf1_spine1 = p2p.Install(leaf1_spine1);

  // connect to spine 2
  p2p.SetDeviceAttribute("DataRate",
                         DataRateValue(DataRate(LINK_THREE_CAPACITY)));
  NodeContainer leaf0_spine2 = NodeContainer(leaf0, spine2);
  NetDeviceContainer netdevice_leaf0_spine2 = p2p.Install(leaf0_spine2);
  NodeContainer leaf1_spine2 = NodeContainer(leaf1, spine2);
  NetDeviceContainer netdevice_leaf1_spine2 = p2p.Install(leaf1_spine2);


  ipv4.SetBase("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer addr_leaf0_spine0 =
      ipv4.Assign(netdevice_leaf0_spine0);
  Ipv4InterfaceContainer addr_leaf0_spine1 =
      ipv4.Assign(netdevice_leaf0_spine1);
  // spine 2
  Ipv4InterfaceContainer addr_leaf0_spine2 =
      ipv4.Assign(netdevice_leaf0_spine2);

  Ipv4InterfaceContainer addr_leaf1_spine0 =
      ipv4.Assign(netdevice_leaf1_spine0);
  Ipv4InterfaceContainer addr_leaf1_spine1 =
      ipv4.Assign(netdevice_leaf1_spine1);
  //spine 2
  Ipv4InterfaceContainer addr_leaf1_spine2 =
      ipv4.Assign(netdevice_leaf1_spine2);

  std::vector<std::pair<Ipv4Address, uint32_t> > serversAddr0 =
      std::vector<std::pair<Ipv4Address, uint32_t> >(SERVER_COUNT);
  std::vector<std::pair<Ipv4Address, uint32_t> > serversAddr1 =
      std::vector<std::pair<Ipv4Address, uint32_t> >(SERVER_COUNT);

  // Setting servers under leaf 0
  p2p.SetDeviceAttribute("DataRate",
                         DataRateValue(DataRate(std::max(LINK_ONE_CAPACITY, LINK_TWO_CAPACITY))));
  ipv4.SetBase("10.1.2.0", "255.255.255.0");
  for (int i = 0; i < SERVER_COUNT; i++)
  {
    NodeContainer nodeContainer = NodeContainer(leaf0, servers0.Get(i));
    NetDeviceContainer netDeviceContainer = p2p.Install(nodeContainer);
    Ipv4InterfaceContainer interfaceContainer = ipv4.Assign(netDeviceContainer);
    serversAddr0[i] = std::make_pair(interfaceContainer.GetAddress(1),
                                     netDeviceContainer.Get(0)->GetIfIndex());
  }

  // Setting servers under leaf 1
  ipv4.SetBase("10.1.3.0", "255.255.255.0");
  for (int i = 0; i < SERVER_COUNT; i++)
  {
    NodeContainer nodeContainer = NodeContainer(leaf1, servers1.Get(i));
    NetDeviceContainer netDeviceContainer = p2p.Install(nodeContainer);
    Ipv4InterfaceContainer interfaceContainer = ipv4.Assign(netDeviceContainer);
    serversAddr1[i] = std::make_pair(interfaceContainer.GetAddress(1),
                                     netDeviceContainer.Get(0)->GetIfIndex());
  }

  /* Nick: Create set of compromised servers */

  std::set<int> compromised;
  std::set<Ipv4Address> compromisedAddresses;

  Ipv4Address compromisedAddress;
  // Let's consider server 0 as compromised.
  if (hostile)
  {
    compromised.insert(0);
    Ptr<Node> compromisedServer = servers0.Get(0);
    Ptr<Ipv4> ipv4 = compromisedServer->GetObject<Ipv4>();
    Ipv4InterfaceAddress compromisedInterface = ipv4->GetAddress(1, 0);
    compromisedAddress = compromisedInterface.GetLocal();
    compromisedAddresses.insert(compromisedAddress);
    compromisedAddress.Print(std::cout);
  }

  if (runMode == LetFlow)
  {
    NS_LOG_INFO("Initing LetFlow routing tables");

    // First, init all the servers
    for (int serverIndex = 0; serverIndex < SERVER_COUNT; ++serverIndex)
    {
      staticRoutingHelper
          .GetStaticRouting(servers0.Get(serverIndex)->GetObject<Ipv4>())
          ->AddNetworkRouteTo(Ipv4Address("0.0.0.0"), Ipv4Mask("0.0.0.0"), 1);

      Ptr<Ipv4LetFlowRouting> letFlowLeaf0 =
          letFlowRoutingHelper.GetLetFlowRouting(leaf0->GetObject<Ipv4>());

      // Enabling logging for leaf0
      letFlowLeaf0->EnableLetFlowHistory(compromisedAddress);

      // LetFlow leaf switches forward the packet to the correct servers
      letFlowLeaf0->AddRoute(serversAddr0[serverIndex].first,
                             Ipv4Mask("255.255.255.255"),
                             serversAddr0[serverIndex].second);
      letFlowLeaf0->SetFlowletTimeout(MicroSeconds(letFlowFlowletTimeout));

      staticRoutingHelper
          .GetStaticRouting(servers1.Get(serverIndex)->GetObject<Ipv4>())
          ->AddNetworkRouteTo(Ipv4Address("0.0.0.0"), Ipv4Mask("0.0.0.0"), 1);

      Ptr<Ipv4LetFlowRouting> letFlowLeaf1 =
          letFlowRoutingHelper.GetLetFlowRouting(leaf1->GetObject<Ipv4>());

      letFlowLeaf1->AddRoute(serversAddr1[serverIndex].first,
                             Ipv4Mask("255.255.255.255"),
                             serversAddr1[serverIndex].second);
      letFlowLeaf1->SetFlowletTimeout(MicroSeconds(letFlowFlowletTimeout));
    }

    // Leaf 0 to spines
    letFlowRoutingHelper.GetLetFlowRouting(leaf0->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.3.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf0_spine0.Get(0)->GetIfIndex());
    letFlowRoutingHelper.GetLetFlowRouting(leaf0->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.3.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf0_spine1.Get(0)->GetIfIndex());
    letFlowRoutingHelper.GetLetFlowRouting(leaf0->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.3.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf0_spine2.Get(0)->GetIfIndex());

    // Leaf 1 to spines
    letFlowRoutingHelper.GetLetFlowRouting(leaf1->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.2.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf1_spine0.Get(1)->GetIfIndex());
    letFlowRoutingHelper.GetLetFlowRouting(leaf1->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.2.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf1_spine1.Get(1)->GetIfIndex());
    letFlowRoutingHelper.GetLetFlowRouting(leaf1->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.2.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf1_spine2.Get(1)->GetIfIndex());

    // Spine 0 to leafs
    letFlowRoutingHelper.GetLetFlowRouting(spine0->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.3.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf1_spine0.Get(1)->GetIfIndex());
    letFlowRoutingHelper.GetLetFlowRouting(spine0->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.2.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf0_spine0.Get(1)->GetIfIndex());

    // Spine 1 to leafs
    letFlowRoutingHelper.GetLetFlowRouting(spine1->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.3.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf1_spine1.Get(1)->GetIfIndex());
    letFlowRoutingHelper.GetLetFlowRouting(spine1->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.2.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf0_spine1.Get(1)->GetIfIndex());

    // Spine 2 to leafs
    letFlowRoutingHelper.GetLetFlowRouting(spine1->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.3.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf1_spine2.Get(1)->GetIfIndex());
    letFlowRoutingHelper.GetLetFlowRouting(spine1->GetObject<Ipv4>())
        ->AddRoute(Ipv4Address("10.1.2.0"), Ipv4Mask("255.255.255.0"),
                   netdevice_leaf0_spine2.Get(1)->GetIfIndex());
  }
  else
  {
    NS_LOG_INFO("Populate global routing tables");
    Ipv4GlobalRoutingHelper::PopulateRoutingTables();
  }

  NS_LOG_INFO("Initialize random seed: " << randomSeed);
  if (randomSeed == 0)
  {
    srand((unsigned)time(NULL));
  }
  else
  {
    srand(randomSeed);
  }

  NS_LOG_INFO("Create applications");

  int flowCount = 0;
  // Install apps on servers under switch leaf0, large flows first
  install_applications(servers0, servers1, SERVER_COUNT, serversAddr1,
                       attackerStart, endTime, flowSize, flowCount, compromised,
                       offTime, onTime, attackerProt, attackerApp, attackerRate,
                       hostileFlows, attackerPacketSize, hostileFlowSize);

  NS_LOG_INFO("Total flow: " << flowCount);

  NS_LOG_INFO("Enabling flow monitor");

  Ptr<FlowMonitor> flowMonitor;
  FlowMonitorHelper flowHelper;
  flowMonitor = flowHelper.InstallAll();

  // XXX Link Monitor Test Code Starts
  Ptr<LinkMonitor> linkMonitor = Create<LinkMonitor>();
  Ptr<Ipv4LinkProbe> linkProbe = Create<Ipv4LinkProbe>(leaf0, linkMonitor, compromisedAddress);
  linkProbe->SetProbeName("Leaf 0");
  linkProbe->SetCheckTime(MicroSeconds(100)); 
  linkProbe->SetDataRateAll(DataRate(LINK_TWO_CAPACITY));
  linkMonitor->Start(Seconds(startTime));
  linkMonitor->Stop(Seconds(END_TIME));

  NS_LOG_INFO("Start simulation");
  Simulator::Stop(Seconds(END_TIME));
  Simulator::Run();

  flowMonitor->CheckForLostPackets();

  std::stringstream flowMonitorFilename;
  std::stringstream linkMonitorFilename;
  std::stringstream flowLoggingFilename;

  flowMonitorFilename << id << "-letflow_convergence-" << linkOneCapacity << "-"
                      << linkTwoCapacity << "-b" << buffer_size << "-" << SERVER_COUNT << "-"
                      << endTime << "-" << transportProt << "-"
                      << letFlowFlowletTimeout << "-" << flowSize << "-"
                      << (hostile == 0 ? "no_attacker" : "attacker") << "-"
                      << attackerRate << "-" << attackerStart << "-" << offTime
                      << "-" << onTime << "-" << attackerPacketSize << "-"
                      << attackerProt << "-" << attackerApp << "-hflows-"
                      << hostileFlows << "-" << hostileFlowSize << ".xml";
  linkMonitorFilename << id << "-letflow_convergence-" << linkOneCapacity << "-"
                      << linkTwoCapacity << "-b" << buffer_size << "-" << SERVER_COUNT << "-"
                      << endTime << "-" << transportProt << "-"
                      << letFlowFlowletTimeout << "-" << flowSize << "-"
                      << (hostile == 0 ? "no_attacker" : "attacker") << "-"
                      << attackerRate << "-" << attackerStart << "-" << offTime
                      << "-" << onTime << "-" << attackerPacketSize << "-"
                      << attackerProt << "-" << attackerApp << "-hflows-"
                      << hostileFlows << "-" << hostileFlowSize << ".out";

  flowLoggingFilename << id << "-letflow_convergence-" << linkOneCapacity << "-"
                      << linkTwoCapacity << "-b" << buffer_size << "-" << SERVER_COUNT << "-"
                      << endTime << "-" << transportProt << "-"
                      << letFlowFlowletTimeout << "-" << flowSize << "-"
                      << (hostile == 0 ? "no_attacker" : "attacker") << "-"
                      << attackerRate << "-" << attackerStart << "-" << offTime
                      << "-" << onTime << "-" << attackerPacketSize << "-"
                      << attackerProt << "-" << attackerApp << "-hflows-"
                      << hostileFlows << "-" << hostileFlowSize << ".flow";

  std::stringstream flowMonitorString;
  std::set<int>::iterator it = compromised.begin();

  // Add compromised servers list at top of flow file.
  flowMonitorString << "<Sim>\n";
  while (it != compromised.end())
  {
    flowMonitorString << "  <Compromised server=\"";
    (serversAddr0[(*it)].first).Print(flowMonitorString);
    flowMonitorString << "\"/>\n";
    it++;
  }

  std::ofstream os(flowMonitorFilename.str().c_str(),
                   std::ios::out | std::ios::binary);
  os << "<?xml version=\"1.0\" ?>\n";
  os << flowMonitorString.str();
  flowMonitor->SerializeToXmlStream(os, 0, true, true);
  os << "</Sim>\n";
  os.close();

  linkMonitor->OutputToFile(linkMonitorFilename.str(),
                            &LinkMonitor::DefaultFormat);

  // Flow logs if in LetFlow mode
  if (runMode == LetFlow) 
  {
    Ptr<Ipv4LetFlowRouting> letFlowLeaf0 =
        letFlowRoutingHelper.GetLetFlowRouting(leaf0->GetObject<Ipv4>());

    assert(letFlowLeaf0->GetLetFlowHistory().enabled);
    std::vector<std::pair<Time, std::pair<std::map<uint32_t, uint32_t>,
                                          std::map<uint32_t, int> > > >
        flows0 = letFlowLeaf0->ComputeNumberOfFlowsPerPort();

    // Ports we are interested in
    //TODO: When extending to N ports we need to add all of them here.
    std::set<uint32_t> ports;
    ports.insert(netdevice_leaf0_spine0.Get(0)->GetIfIndex());
    ports.insert(netdevice_leaf0_spine1.Get(0)->GetIfIndex());
    ports.insert(netdevice_leaf0_spine2.Get(0)->GetIfIndex());
    outputFlowLog(flowLoggingFilename.str(), letFlowLeaf0->GetLetFlowHistory().flowGapHistory,flows0, ports);
  }
  Simulator::Destroy();

  NS_LOG_INFO("Stop simulation");
}
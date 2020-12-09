# Letflow stability/convergence

# 8 paths, 21 servers.
./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Tcp --attackerOffTime=0 --attackerOnTime=1 --attackerRate=2000 --hostileFlows=1 --attackerApp=Bulk --hostile --letFlowFlowletTimeout=150 --EndTime=4 --largeFlowRatio=1 --largeFlowSize=500000000 --paths=8 --fastPathRatio=0.8 --fastPathCapacity=4 --slowPathCapacity=2" &
./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=0 --attackerOnTime=1 --attackerRate=2000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=4 --largeFlowRatio=1 --largeFlowSize=500000000 --paths=8 --fastPathRatio=0.8 --fastPathCapacity=4 --slowPathCapacity=2" &
./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=0 --attackerOnTime=1 --attackerRate=4000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=4 --largeFlowRatio=1 --largeFlowSize=500000000 --paths=8 --fastPathRatio=0.8 --fastPathCapacity=4 --slowPathCapacity=2" &


# 4 paths, 21 servers
./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Tcp --attackerOffTime=0 --attackerOnTime=1 --attackerRate=2000 --hostileFlows=1 --attackerApp=Bulk --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=0 --attackerOnTime=1 --attackerRate=2000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=0 --attackerOnTime=1 --attackerRate=4000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &


# 4 paths, attack with 2gbps rate, since that rate seems to do what we expect.

for attackerOffTime in 200
do
# 200 400 600
  for attackerOnTime in 800 1000 1200 1400 2000
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=2000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

for attackerOffTime in 400
do
# 200 400 600
  for attackerOnTime in 200 400 600 800 1000 1200 1400 2000
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=2000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

for attackerOffTime in 800
do
# 200 400 600
  for attackerOnTime in 200 400 600 800 1000 1200 1400 2000
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=2000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

for attackerOffTime in 1000
do
# 200 400 600
  for attackerOnTime in 400 600 800 1000 1200 1400 2000
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=2000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

for attackerOffTime in 3000
do
  for attackerOnTime in 200 400 600 800
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=2000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

for attackerOffTime in 5000
do
  for attackerOnTime in 1200 2000 3000 4000
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=2000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

for attackerOffTime in 5000
do
  for attackerOnTime in 500 600 1000 2000
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=4000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

# Very high rate microburst.
for attackerOffTime in 5000
do
  for attackerOnTime in 100 200 300 400 500
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=8000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowRatio=1 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

# high rate microburst

for attackerOffTime in 4000
do
  for attackerOnTime in 200 300 500
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=8000 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6  --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

# low rate microburst

for attackerOffTime in 1000
do
  for attackerOnTime in 400 500 600
  do
    ./waf --run "letflow-configurable --servers=21 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=100000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --attackerRate=1800 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=6 --largeFlowSize=300000000 --paths=4 --fastPathRatio=0.5 --fastPathCapacity=4 --slowPathCapacity=2" &
  done
done

    ./waf --run "letflow-configurable --servers=8 --runMode=LetFlow --transportProt=Tcp --buffer=250 --hostileFlowSize=25000000 --randomSeed=1 --attackerProt=Udp --attackerOffTime=1000 --attackerOnTime=500 --attackerRate=1800 --hostileFlows=1 --attackerApp=OnOff --hostile --letFlowFlowletTimeout=150 --EndTime=2 --largeFlowSize=40000000 --paths=3 --fastPathRatio=1.0 --fastPathCapacity=3 --slowPathCapacity=2" &

# Link monitor on the leafs to find 

for runMode in LetFlow Conga
do
#0.5 0.7 0.9
    for load in 0.5
    do
    sleep 1;
    ./waf --run "conga-simulation-large --linkMonitor=true --attackerApp=Bulk --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=2000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Tcp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
     done
done

for runMode in LetFlow Conga
do
    for attackerOffTime in 800 1000 5000 6000
    do
        for attackerOnTime in 500
        do
            for rate in 9000 9500
            do
                sleep 1;
                ./waf --run "conga-simulation-large --linkMonitor=true --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.5 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done
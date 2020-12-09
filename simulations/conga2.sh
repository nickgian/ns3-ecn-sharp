# Large simulation for LetFlow/Conga with a more selective choice of rate/on/off time.
# We vary the load, and on/off times, and consider an attacker budget of 200mb.


for runMode in ECMP LetFlow Conga
do
#0.5 0.7 0.9
    for load in 0.2 0.5 0.7 0.9
    do
    sleep 1;
    ./waf --run "conga-simulation-large --linkMonitor=true --attackerApp=Bulk --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=2000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Tcp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
     done
done

# For load 0.2 - In theory we need higher rate, avg load for spines is around 40% of 5gbps.
	# 300us: Rdos = 350.000 + 112.500 / 300 = 1541 MBps or 12.3Gbps
	# 500us: Rdos = 1075MBps or 8.6Gbps
	# 600us: Rdos = 958.3MBps or 7.66Gbps
	# 1000us: Rdos = 725MBps or 5.8Gbps
for runMode in ECMP LetFlow Conga
do
    for attackerOffTime in 800 1000 5000 6000
    do
        for attackerOnTime in 500
        do
            for rate in 9000 9500
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.2 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
    sleep 900;
done

# Load 0.2 again, but shorter on time.
	# 300us: Rdos = 350.000 + 112.500 / 300 = 1541 MBps or 12.3Gbps
	# 500us: Rdos = 1075MBps or 8.6Gbps
	# 600us: Rdos = 958.3MBps or 7.66Gbps
	# 1000us: Rdos = 725MBps or 5.8Gbps
for runMode in ECMP LetFlow Conga
do
    for attackerOffTime in 800 1000 5000 6000
    do
        for attackerOnTime in 310
        do
            for rate in 12500 14000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.2 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
    sleep 300;
done



# For load 0.5 - In theory we need higher rate, avg load for spines is around 50% of 5gbps.
	# 300us: Rdos = (350.000 + 93.750) / 300 = 1479 MBps or 11.8Gbps
	# 500us: Rdos = 1012MBps or 8.1Gbps
for runMode in ECMP LetFlow Conga
do
    for attackerOffTime in 800 1000 5000 6000
    do
        for attackerOnTime in 500
        do
            for rate in 8500 9000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.5 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
    sleep 100;
done

# Load 0.5 again, but shorter on time.
	# 300us: Rdos = (350.000 + 93.750) / 300 = 1479 MBps or 11.8Gbps
	# 500us: Rdos = 1012MBps or 8.1Gbps
for runMode in ECMP LetFlow Conga
do
    for attackerOffTime in 800 1000 5000 6000
    do
        for attackerOnTime in 310
        do
            for rate in 11900 12500
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.5 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
    sleep 100;
done

# For load 0.7 - avg load for spines is around 70% of 5gbps.
	# 300us: Rdos = (350.000 + 93.750) / 300 = 10.8Gbps
	# 500us: Rdos = 7.1GBps
for runMode in ECMP LetFlow Conga
do
    for attackerOffTime in 800 1000 3000 5000
    do
        for attackerOnTime in 500
        do
            for rate in 7300 8000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.7 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
    sleep 1000;
done

# For load 0.7 - avg load for spines is around 70% of 5gbps.
	# 300us: Rdos = (350.000 + 93.750) / 300 = 10.8Gbps
	# 500us: Rdos = 7.1GBps
for runMode in ECMP LetFlow Conga
do
    for attackerOffTime in 800 1000 3000 5000
    do
        for attackerOnTime in 310
        do
            for rate in 11000 11500
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.7 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
    sleep 1000;
done

#Load 0.7 - for letflow again because attack failed.
for runMode in LetFlow
do
    for attackerOffTime in 600 800 1000 3000
    do
        for attackerOnTime in 310
        do
            for rate in 8000 9000 10000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.7 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done

# Trying more simulations to understand why 0.7 fails.
for runMode in LetFlow
do
    for attackerOffTime in 600 800 1000 1500 3000
    do
        for attackerOnTime in 400
        do
            for rate in 6000 8000 8750 9000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.7 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done

# For load 0.9 - avg load for spines is around 83% of 5gbps.
	# 300us: Rdos ~ 10.1Gbps
	# 500us: Rdos = 6.3Gbps
for runMode in ECMP LetFlow Conga
do
    for attackerOffTime in 800 1000 5000
    do
        for attackerOnTime in 500
        do
            for rate in 5000 6500 7000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.9 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done

# For load 0.9 - avg load for spines is around 83% of 5gbps.
	# 300us: Rdos ~ 10.1Gbps
	# 500us: Rdos = 6.3Gbps

#LetFlow Conga
for runMode in ECMP LetFlow Conga 
do
    for attackerOffTime in 800 1000 5000
    do
        for attackerOnTime in 310
        do
            for rate in 9000 10500 11000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=$runMode --letFlowFlowletTimeout=150 --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=200000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=0.9 --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done
# Large simulation for LetFlow/Conga.
# We vary the load, on/off times.

# LetFlow
for load in 0.2 0.5 0.7 0.9
do
    ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=LetFlow --letFlowFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=2000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Tcp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
    ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=LetFlow --letFlowFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=2000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Udp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
    ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=LetFlow --letFlowFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=4000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Udp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
done

# Conga
for load in 0.2 0.5 0.7 0.9
do
    ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=Conga --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=2000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Tcp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
    ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=Conga --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=2000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Udp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
    ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=Conga --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=4000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Udp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
done

# ECMP
for load in 0.2 0.5 0.7 0.9
do
    ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=ECMP --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=2000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Tcp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
    ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=ECMP --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=2000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Udp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
    ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=ECMP --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=4000 --attackerOffTime=0 --attackerOnTime=1 --attackerProt=Udp --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
done

# LetFlow
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 150 200
    do
        for attackerOnTime in 150 500
        do
            for rate in 3000 4000 5000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=LetFlow --letFlowFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done

# Conga
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 150 200
    do
        for attackerOnTime in 150 300 500
        do
            for rate in 3000 4000 5000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=Conga --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done

#ECMP
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 150 200
    do
        for attackerOnTime in 150 300 500
        do
            for rate in 3000 4000 5000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=ECMP --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done


#Letflow
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 1500
    do
        for attackerOnTime in 500 800 1000
        do
            for rate in 3000 4000 5000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=LetFlow --letFlowFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done

# Conga
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 1500
    do
        for attackerOnTime in 500 800 1000
        do
            for rate in 3000 4000 5000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=Conga --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done

#ECMP
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 1500
    do
        for attackerOnTime in 500 800 1000
        do
            for rate in 3000 4000 5000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=ECMP --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done


#LetFlow
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 2000
    do
        for attackerOnTime in 600 800 1000
        do
            for rate in 5000 6000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=LetFlow --letFlowFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done

#Conga
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 2000
    do
        for attackerOnTime in 600 800 1000
        do
            for rate in 4000 5000 6000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=Conga --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done



#LetFlow
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 2500
    do
        for attackerOnTime in 400 800 1000
        do
            for rate in 5000 6000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=LetFlow --letFlowFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done

#Conga
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 2000
    do
        for attackerOnTime in 600 800 1000
        do
            for rate in 4000 5000 6000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=Conga --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done


#LetFlow 0.5 0.7 0.9
for load in 0.5 0.7 0.9
do   
    for attackerOffTime in 5000
    do
        for attackerOnTime in 200 400 800 1000
        do
            for rate in 5000 6000 8000 10000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=LetFlow --letFlowFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
    sleep 2000;
done

#Conga
for load in 0.2 0.5 0.7 0.9
do   
    for attackerOffTime in 2000
    do
        for attackerOnTime in 600 800 1000
        do
            for rate in 4000 5000 6000
            do
                sleep 1;
                ./waf --run "conga-simulation-large --spineLeafCapacity=5 --leafServerCapacity=5 --runMode=Conga --congaFlowletTimeout=150 --transportProt=Tcp --hostile --hostileFlowSize=300000000 --attackerMode=LetFlow --attackerRate=$rate --attackerOffTime=$attackerOffTime --attackerOnTime=$attackerOnTime --randomSeed=1 --cdfFileName=examples/load-balance/DCTCP_CDF.txt --load=$load --FlowLaunchEndTime=2.15 --EndTime=2.45" &
            done
        done
    done
done
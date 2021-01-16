#!/bin/sh

set -x

# sleep 300
python3 loadgen.py --lambda 5 --image mfgmateus/jmeter:1.0.2 --name api-stress --cluster k8s --method=constant --args='-Jserver=35.184.64.160' --duration=30
sleep 300
python3 loadgen.py --lambda 10 --image mfgmateus/jmeter:1.0.2 --name api-stress --cluster k8s --method=constant --args='-Jserver=35.184.64.160' --duration=30
sleep 300
python3 loadgen.py --lambda 5 --image mfgmateus/cassandra-stress:1.0.8 --name cassandra-stress --cluster k8s --method=constant --args "" --duration=30
sleep 300
python3 loadgen.py --lambda 10 --image mfgmateus/cassandra-stress:1.0.8 --name cassandra-stress --cluster k8s --method=constant --args "" --duration=30
sleep 300
python3 loadgen.py --lambda 10 --image mfgmateus/jmeter:1.0.2 --name api-stress --cluster k8s --method=flashcrowd --args='-Jserver=35.184.64.160' --period=15 --shock-level=3 --duration=60 --ocurrences=3
sleep 300
python3 loadgen.py --lambda 20 --image mfgmateus/jmeter:1.0.2 --name api-stress --cluster k8s --method=sinusoid --args='-Jserver=35.184.64.160' --period=15 --duration=60 --sinusoid 10,20 
sleep 300
python3 loadgen.py --lambda 10 --image mfgmateus/cassandra-stress:1.0.8 --name cassandra-stress --cluster k8s --method=flashcrowd --args "" --period=15 --shock-level=3 --duration=60 --ocurrences=3
sleep 300
python3 loadgen.py --lambda 20 --image mfgmateus/cassandra-stress:1.0.8 --name cassandra-stress --cluster k8s --method=sinusoid --args "" --period=10 --duration=60 --sinusoid 10,20 
sleep 300
python3 loadgen.py --lambda 10 --image mfgmateus/jmeter:1.0.2 --name api-stress --cluster k8s --method=flashcrowd --args='-Jserver=35.184.64.160' --period=15 --shock-level=5 --duration=60 --ocurrences=3
sleep 300
python3 loadgen.py --lambda 30 --image mfgmateus/jmeter:1.0.2 --name api-stress --cluster k8s --method=sinusoid --args='-Jserver=35.184.64.160' --period=15 --duration=60 --sinusoid 20,20 
sleep 300
python3 loadgen.py --lambda 10 --image mfgmateus/cassandra-stress:1.0.8 --name cassandra-stress --cluster k8s --method=flashcrowd --args "" --period=15 --shock-level=5 --duration=60 --ocurrences=3
sleep 300
python3 loadgen.py --lambda 30 --image mfgmateus/cassandra-stress:1.0.8 --name cassandra-stress --cluster k8s --method=sinusoid --args "" --period=10 --duration=60 --sinusoid 20,20
export DROPBOX_TOKEN="3KQlOaEVH2gAAAAAAAAAAZlo419-e-YWvxVJtH8klJ-nlV1kozkgA3eyPmXpGV8r"

gcloud container clusters get-credentials cluster-2 --region us-central1-c

python3 loadgen.py --lambda 5 --image mfgmateus/jmeter:1.0.4 --name api-stress --cluster k8s --method=constant --args="-Jserver=35.184.64.160 -Jthreads=90 -Jduration=1800" --duration=30 --dropbox-token=$DROPBOX_TOKEN
sleep 600

python3 loadgen.py --lambda 5 --image mfgmateus/jmeter:1.0.4 --name api-stress --cluster k8s --method=constant --args="-Jserver=35.184.64.160 -Jthreads=60 -Jduration=1800" --duration=30 --dropbox-token=$DROPBOX_TOKEN
sleep 600
python3 loadgen.py --lambda 10 --image mfgmateus/jmeter:1.0.4 --name api-stress --cluster k8s --method=constant --args="-Jserver=35.184.64.160 -Jthreads=60 -Jduration=1800" --duration=30 --dropbox-token=$DROPBOX_TOKEN
sleep 600

gcloud container clusters get-credentials cluster-2 --region us-central1-c
python3 loadgen.py --lambda 10 --image mfgmateus/jmeter:1.0.4 --name api-stress --cluster k8s --method=flashcrowd --args="-Jserver=35.184.64.160 -Jthreads=60 -Jduration=3600" --period=15 --shock-level=3 --duration=60 --ocurrences=3 --dropbox-token=$DROPBOX_TOKEN
sleep 600
python3 loadgen.py --lambda 20 --image mfgmateus/jmeter:1.0.4 --name api-stress --cluster k8s --method=sinusoid --args="-Jserver=35.184.64.160 -Jthreads=60 -Jduration=3600" --period=15 --duration=60 --sinusoid 10,20 --dropbox-token=$DROPBOX_TOKEN 

gcloud container clusters get-credentials cluster-2 --region us-central1-c
sleep 600
python3 loadgen.py --lambda 10 --image mfgmateus/jmeter:1.0.4 --name api-stress --cluster k8s --method=flashcrowd --args="-Jserver=35.184.64.160 -Jthreads=60 -Jduration=3600" --period=15 --shock-level=5 --duration=60 --ocurrences=3 --dropbox-token=$DROPBOX_TOKEN
sleep 600
python3 loadgen.py --lambda 30 --image mfgmateus/jmeter:1.0.4 --name api-stress --cluster k8s --method=sinusoid --args="-Jserver=35.184.64.160 -Jthreads=60 -Jduration=3600" --period=15 --duration=60 --sinusoid 20,20 --dropbox-token=$DROPBOX_TOKEN 


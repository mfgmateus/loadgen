export DROPBOX_TOKEN="3KQlOaEVH2gAAAAAAAAAAZlo419-e-YWvxVJtH8klJ-nlV1kozkgA3eyPmXpGV8r"

gcloud container clusters get-credentials cluster-2 --region us-central1-c

python3 loadgen.py --lambda 5 --image mfgmateus/jmeter:1.0.4 --name api-stress --cluster k8s --method=constant --args="-Jserver=35.184.64.160 -Jthreads=30 -Jduration=1800" --duration=30 --dropbox-token=$DROPBOX_TOKEN

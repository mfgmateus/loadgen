from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes import client, config
import os, datetime, time

# configuration = client.Configuration()
# configuration.api_key['authorization'] = os.getenv('TOKEN')
# configuration.api_key_prefix['authorization'] = 'Bearer'
# configuration.host = os.getenv('APISERVER')
# configuration.verify_ssl = False
# config.load_kube_config()
# client.Configuration.set_default(configuration)
config.load_kube_config()

# def test_gke():

#     v1 = client.CoreV1Api()
#     print("Listing pods with their IPs:")
#     ret = v1.list_pod_for_all_namespaces(watch=False)
#     for i in ret.items:
#         print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

# # test_gke()
# # exit()

api_instance = client.AppsV1Api()
# api_instance_ext = client.ExtensionsV1beta1Api()

NAMESPACE = 'default'
test_name = datetime.datetime.now().strftime('%Y%m%d%H%M')

def create_deployment_object(deployment_name, name, image, args, mounts, replicas, duration):
    volume = client.V1Volume(
        name = "loadgen-volume",
        persistent_volume_claim = client.V1PersistentVolumeClaimVolumeSource(
            claim_name = "nfs-pvc"
        )
    )
    # Configureate Pod template container
    container = client.V1Container(
        name=name,
        image_pull_policy = "IfNotPresent",
        args=args,
        # resources=client.V1ResourceRequirements(
            # limits = {"cpu": "100m"}
        # ),
        volume_mounts = [client.V1VolumeMount(
            name = "loadgen-volume",
            mount_path = "/var/loadgen")],
        env = [
            client.V1EnvVar(
                name = "TEST_NAME",
                value = test_name
            ),
            client.V1EnvVar(
                name = "DURATION",
                value = str(duration) + "m"
            )
        ],
        image=image)
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container], volumes=[volume]))
    # Create the specification of deployment
    spec = client.V1DeploymentSpec(
        selector={"matchLabels": {"app": name}},
        replicas=replicas,
        template=template)
    # Instantiate the deployment object
    deployment = client.V1Deployment(
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=spec)
    

    return deployment

def create_log_collector(deployment_name, name, image, args, mounts, duration):
    deployment_name = deployment_name + "-collector"
    deployment = create_deployment_object(deployment_name, name, image, args, mounts, 1, duration)
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace=NAMESPACE)

def create(deployment_name, name, image, args, mounts, replicas, duration):
    create_log_collector(deployment_name, name, image, args, mounts, duration)
    deployment = create_deployment_object(deployment_name, name, image, args, mounts, replicas, duration)
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace=NAMESPACE)
    global out
    out = open("logs/load_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".log","w+")
    out.write("timestamp,clients\n")
    out.write(str(int(round(time.time()))) + "," + str(replicas) + "\n")
    out.flush()
    # print("Deployment created. status='%s'" % str(api_response.status))

def scale(deployment_name, name, image, args, mounts, replicas, duration):
    deployment = create_deployment_object(deployment_name, name, image, args, mounts, replicas, duration)
    deployment.spec.replicas = replicas
    api_response = api_instance.patch_namespaced_deployment(
        body=deployment,
        name=deployment_name,
        namespace=NAMESPACE
    )
    out.write(str(int(round(time.time()))) + "," + str(replicas) + "\n")
    out.flush()
    # print("Deployment updated. status='%s'" % str(api_response.status))

def remove_deployment(deployment_name):
    api_response = api_instance.delete_namespaced_deployment(
        name=deployment_name,
        namespace=NAMESPACE,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))

def remove(deployment_name):
    remove_deployment(deployment_name)
    remove_deployment(deployment_name+"-collector")
    # print("Deployment deleted. status='%s'" % str(api_response.status))


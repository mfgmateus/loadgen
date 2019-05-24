from kubernetes import client, config
from kubernetes.client.rest import ApiException
from google.oauth2 import service_account
from google.cloud.container_v1 import ClusterManagerClient
from kubernetes import client, config
import os

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
credentials = service_account.Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), scopes=SCOPES)
cluster_manager_client = ClusterManagerClient(credentials=credentials)
cluster = cluster_manager_client.get_cluster(project_id, zone, cluster_id)
configuration = client.Configuration()
configuration.host = "https://"+cluster.endpoint+":443"
configuration.verify_ssl = False
configuration.api_key = {"authorization": "Bearer " + credentials.token}
client.Configuration.set_default(configuration)
api_instance = client.ExtensionsV1beta1Api()

#automatic-load=sim

def create_deployment_object(deployment_name, name, image, args, mounts, replicas):
    # Configureate Pod template container
    container = client.V1Container(
        name=name,
        image_pull_policy = "IfNotPresent",
        args=args,
        image=image)
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas=replicas,
        template=template)
    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=spec)

    return deployment

def create(deployment_name, name, image, args, mounts, replicas):
    deployment = create_deployment_object(deployment_name, name, image, args, mounts, replicas)
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace="default")
    # print("Deployment created. status='%s'" % str(api_response.status))

def scale(deployment_name, replicas):
    deployment = api_instance.read_namespaced_deployment(deployment_name, "default")
    deployment.spec.replicas = replicas
    api_response = api_instance.patch_namespaced_deployment(
        body=deployment,
        name=deployment_name,
        namespace="default"
    )
    # print("Deployment updated. status='%s'" % str(api_response.status))

def remove(deployment_name):
    api_response = api_instance.delete_namespaced_deployment(
        name=deployment_name,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    # print("Deployment deleted. status='%s'" % str(api_response.status))


# test_gke("deft-province-207121", "us-central1-a", "demo-cluster")
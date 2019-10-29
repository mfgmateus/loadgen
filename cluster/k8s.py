from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes import client, config
import os

# configuration = client.Configuration()
# configuration.api_key['authorization'] = os.getenv('TOKEN')
# configuration.api_key_prefix['authorization'] = 'Bearer'
# configuration.host = os.getenv('APISERVER')
# configuration.verify_ssl = False
# client.Configuration.set_default(configuration)
# config.load_kube_config()

api_instance = client.CoreV1Api()
api_instance_ext = client.ExtensionsV1beta1Api()

NAMESPACE = 'default'

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
    api_response = api_instance_ext.create_namespaced_deployment(
        body=deployment,
        namespace=NAMESPACE)
    # print("Deployment created. status='%s'" % str(api_response.status))

def scale(deployment_name, name, image, args, mounts, replicas):
    deployment = create_deployment_object(deployment_name, name, image, args, mounts, replicas)
    deployment.spec.replicas = replicas
    api_response = api_instance_ext.patch_namespaced_deployment(
        body=deployment,
        name=deployment_name,
        namespace=NAMESPACE
    )
    # print("Deployment updated. status='%s'" % str(api_response.status))

def remove(deployment_name):
    api_response = api_instance_ext.delete_namespaced_deployment(
        name=deployment_name,
        namespace=NAMESPACE,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    # print("Deployment deleted. status='%s'" % str(api_response.status))

# test_gke("deft-province-207121", "us-central1-a", "demo-cluster")
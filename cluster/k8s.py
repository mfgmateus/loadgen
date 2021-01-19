from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes import client, config
import os, datetime, time, shutil, tarfile
from kubernetes.stream import stream
from tempfile import TemporaryFile
from cluster.tools.dropbox import DropboxTransferData

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
core_api_instance = client.CoreV1Api()
# api_instance_ext = client.ExtensionsV1beta1Api()

NAMESPACE = 'default'
test_start = datetime.datetime.now()
test_name = test_start.strftime('%Y%m%d%H%M')
log_dir = "logs/" + test_name
log_file = log_dir + "/load_" + test_start.strftime("%Y%m%d%H%M") + ".log"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def create_deployment_object(deployment_name, name, image, args, mounts, replicas, duration, envargs):

    if envargs == None:
        envargs = []

    provided_env = list(map(lambda item: client.V1EnvVar(
                name = item.split(":")[0],
                value = item.split(":")[1]
            ), envargs))
            
    env = [
            client.V1EnvVar(
                name = "TEST_NAME",
                value = test_name
            ),
            client.V1EnvVar(
                name = "DURATION",
                value = str(duration) + "m"
            )
        ]

    env += provided_env

    # Configureate Pod template container
    container = client.V1Container(
        name=name,
        image_pull_policy = "IfNotPresent",
        args=args,
        # resources=client.V1ResourceRequirements(
            # limits = {"cpu": "100m"}
        # ),
        env = env,
        image=image)
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container]))
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

def create_log_collector(deployment_name, name, image, args, mounts, duration, envargs):
    deployment_name = deployment_name + "-collector"
    deployment = create_deployment_object(deployment_name, name, image, args, mounts, 1, duration, envargs)
    deployment.spec.template.metadata.labels["collector"] = "true"
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace=NAMESPACE)

def create(deployment_name, name, image, args, mounts, replicas, duration, envargs):
    create_log_collector(deployment_name, name, image, args, mounts, duration, envargs)
    deployment = create_deployment_object(deployment_name, name, image, args, mounts, replicas, duration, envargs)
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace=NAMESPACE)
    global out
    out = open(log_file,"w+")
    out.write("timestamp,clients\n")
    out.write(str(int(round(time.time()))) + "," + str(replicas) + "\n")
    out.flush()
    # print("Deployment created. status='%s'" % str(api_response.status))

def scale(deployment_name, name, image, args, mounts, replicas, duration, envargs):
    deployment = create_deployment_object(deployment_name, name, image, args, mounts, replicas, duration, envargs)
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


def list_files(pod_name):
    command = ['find', '/var/loadgen', '-type', 'f']
    files = []
    resp = stream(core_api_instance.connect_get_namespaced_pod_exec, pod_name, NAMESPACE,
                command=command,
                stderr=True, stdin=True,
                stdout=True, tty=False,
                _preload_content=False)

    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            out = resp.read_stdout()
            if out.strip() != "":
                files += list(filter(lambda line: line != "",out.split("\n")))
        if resp.peek_stderr():
            print("STDERR: %s" % resp.read_stderr())
    resp.close()
    return files

def collect_files(pod_name, files):
    dest_file = log_dir + "/collector-files.tar"
    files = list(map(lambda f: f.split("/")[-1:][0], files))
    command = ['tar', '-C', '/tmp', '-cf', "/tmp/collector-files.tar"]
    command += files
    resp = stream(core_api_instance.connect_get_namespaced_pod_exec, pod_name, NAMESPACE,
                command=command,
                stderr=True, stdin=True,
                stdout=True, tty=False,
                _preload_content=False)

    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            out = resp.read_stdout()
        if resp.peek_stderr():
            print("STDERR: %s" % resp.read_stderr())
    resp.close()

    command = ['cat', '/tmp/collector-files.tar']
    resp = stream(core_api_instance.connect_get_namespaced_pod_exec, pod_name, NAMESPACE,
                command=command,
                stderr=True, stdin=True,
                stdout=True, tty=False,
                _preload_content=False)

    with open(dest_file, "w") as out_file:
        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                out = resp.read_stdout()
                out_file.write(out)
            if resp.peek_stderr():
                print("STDERR: %s" % resp.read_stderr())
        resp.close()

    TMP_DIR = ".tar_gz_converter_tmp"

    with tarfile.open(dest_file) as f:
        f.extractall(TMP_DIR)

    with tarfile.open(dest_file + ".gz", "w:gz") as f:
        f.add(TMP_DIR, ".")

    shutil.rmtree(TMP_DIR)
    os.remove(dest_file)

def backup_files(pod_name, files):
    new_files = []
    for file_name in files:
        new_file = backup_file(pod_name, file_name)
        new_files.append(new_file)
    return new_files

def backup_file(pod_name, file_name):
    dest_file = "/tmp" + "/" + file_name.split("/")[-1:][0]
    command = ['cp', file_name, dest_file]
    resp = stream(core_api_instance.connect_get_namespaced_pod_exec, pod_name, NAMESPACE,
                command=command,
                stderr=True, stdin=True,
                stdout=True, tty=False,
                _preload_content=False)

    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            out = resp.read_stdout()
            with open(dest_file, "w") as out_file:
                out_file.write(out)
        if resp.peek_stderr():
            print("STDERR: %s" % resp.read_stderr())
    resp.close()
    return dest_file

def collect_data(dropbox_token):
    collectors = core_api_instance.list_namespaced_pod(namespace=NAMESPACE, label_selector="collector=true")
    for collector in collectors.items:
        pod_name = collector.metadata.name
        files = list_files(pod_name)
        files = backup_files(pod_name, files)
        collect_files(pod_name, files)
    
    if dropbox_token != None:
        upload_to_dropbox(dropbox_token)


def upload_to_dropbox(access_token):
    files = [  log_dir + "/" + name for name in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, name)) ]
    transfer_data = DropboxTransferData(access_token)
    for source in files:
        destination =  "/loadgen/" + source
        print("Uploading {0}".format(destination))
        transfer_data.upload_file(source, destination)
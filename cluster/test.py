# import datetime, time, dropbox, shutil
# from kubernetes import client, config
# from kubernetes.client.rest import ApiException
# from kubernetes import client, config
# import os, datetime, time, tarfile
# from kubernetes.stream import stream
# from tempfile import TemporaryFile
# from tools.dropbox import DropboxTransferData

# # configuration = client.Configuration()
# # configuration.api_key['authorization'] = os.getenv('TOKEN')
# # configuration.api_key_prefix['authorization'] = 'Bearer'
# # configuration.host = os.getenv('APISERVER')
# # configuration.verify_ssl = False
# # config.load_kube_config()
# # client.Configuration.set_default(configuration)
# config.load_kube_config()

# # def test_gke():

# #     v1 = client.CoreV1Api()
# #     print("Listing pods with their IPs:")
# #     ret = v1.list_pod_for_all_namespaces(watch=False)
# #     for i in ret.items:
# #         print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

# # # test_gke()
# # # exit()

# api_instance = client.AppsV1Api()
# core_api_instance = client.CoreV1Api()
# # api_instance_ext = client.ExtensionsV1beta1Api()

# NAMESPACE = 'default'
# test_start = datetime.datetime.now()
# test_name = test_start.strftime('%Y%m%d%H%M')
# log_dir = "logs/" + test_name
# log_file = log_dir + "/load_" + test_start.strftime("%Y%m%d%H%M") + ".log"

# if not os.path.exists(log_dir):
#     os.makedirs(log_dir)

# def create(deployment_name, name, image, args, mounts, replicas, duration):
#     print("Creating service {0} with {1} clients".format(deployment_name, replicas))
#     global out
#     out = open("logs/load_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".log","w+")
#     out.write("timestamp,clients\n")
#     out.write(str(int(round(time.time()))) + "," + str(replicas) + "\n")
#     out.flush()
# def scale(deployment_name, name, image, args, mounts, replicas):
#     print("Scaling service {0} to {1} clients".format(deployment_name, replicas))
#     out.write(str(int(round(time.time()))) + "," + str(replicas) + "\n")
#     out.flush()

# def remove(deployment_name):
#     print("Removing service " + deployment_name)


# def list_files(pod_name):
#     command = ['find', '/var/loadgen', '-type', 'f']
#     files = []
#     resp = stream(core_api_instance.connect_get_namespaced_pod_exec, pod_name, NAMESPACE,
#                 command=command,
#                 stderr=True, stdin=True,
#                 stdout=True, tty=False,
#                 _preload_content=False)

#     while resp.is_open():
#         resp.update(timeout=1)
#         if resp.peek_stdout():
#             out = resp.read_stdout()
#             if out.strip() != "":
#                 files += list(filter(lambda line: line != "",out.split("\n")))
#         if resp.peek_stderr():
#             print("STDERR: %s" % resp.read_stderr())
#     resp.close()
#     return files

# def collect_files(pod_name, files):
#     dest_file = log_dir + "/collector-files.tar"
#     command = ['tar', '-cf', "/tmp/collector-files.tar"]
#     command += files
#     resp = stream(core_api_instance.connect_get_namespaced_pod_exec, pod_name, NAMESPACE,
#                 command=command,
#                 stderr=True, stdin=True,
#                 stdout=True, tty=False,
#                 _preload_content=False)

#     while resp.is_open():
#         resp.update(timeout=1)
#         if resp.peek_stdout():
#             out = resp.read_stdout()
#         if resp.peek_stderr():
#             print("STDERR: %s" % resp.read_stderr())
#     resp.close()

#     command = ['cat', '/tmp/collector-files.tar']
#     resp = stream(core_api_instance.connect_get_namespaced_pod_exec, pod_name, NAMESPACE,
#                 command=command,
#                 stderr=True, stdin=True,
#                 stdout=True, tty=False,
#                 _preload_content=False)

#     with open(dest_file, "w") as out_file:
#         while resp.is_open():
#             resp.update(timeout=1)
#             if resp.peek_stdout():
#                 out = resp.read_stdout()
#                 out_file.write(out)
#             if resp.peek_stderr():
#                 print("STDERR: %s" % resp.read_stderr())
#         resp.close()

#     TMP_DIR = ".tar_gz_converter_tmp"

#     with tarfile.open(dest_file) as f:
#         f.extractall(TMP_DIR)

#     with tarfile.open(dest_file + ".gz", "w:gz") as f:
#         f.add(TMP_DIR, ".")

#     shutil.rmtree(TMP_DIR)
#     os.remove(dest_file)

# def backup_files(pod_name, files):
#     new_files = []
#     for file_name in files:
#         new_file = backup_file(pod_name, file_name)
#         new_files.append(new_file)
#     return new_files

# def backup_file(pod_name, file_name):
#     dest_file = "/tmp" + "/" + file_name.split("/")[-1:][0]
#     command = ['cp', file_name, dest_file]
#     resp = stream(core_api_instance.connect_get_namespaced_pod_exec, pod_name, NAMESPACE,
#                 command=command,
#                 stderr=True, stdin=True,
#                 stdout=True, tty=False,
#                 _preload_content=False)

#     while resp.is_open():
#         resp.update(timeout=1)
#         if resp.peek_stdout():
#             out = resp.read_stdout()
#             with open(dest_file, "w") as out_file:
#                 out_file.write(out)
#         if resp.peek_stderr():
#             print("STDERR: %s" % resp.read_stderr())
#     resp.close()
#     return dest_file

# def collect_data():
#     collectors = core_api_instance.list_namespaced_pod(namespace=NAMESPACE, label_selector="collector=true")
#     for collector in collectors.items:
#         pod_name = collector.metadata.name
#         files = list_files(pod_name)
#         files = backup_files(pod_name, files)
#         collect_files(pod_name, files)
    
#     upload_to_dropbox("h3-qrM9-QkIAAAAAAAAAAVI5hoAHZsT-9Tfer4qE4KDUZcSCkQctCa1cGAT7OFV2")


# def upload_to_dropbox(access_token):
#     files = [  log_dir + "/" + name for name in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, name)) ]
#     transfer_data = DropboxTransferData(access_token)
#     for source in files:
#         destination =  "/loadgen/" + source
#         print("Uploading {0}".format(destination))
#         transfer_data.upload_file(source, destination)

# collect_data()
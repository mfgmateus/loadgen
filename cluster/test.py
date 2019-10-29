def create(deployment_name, name, image, args, mounts, replicas):
    print("Creating service {0} with {1} clients".format(deployment_name, replicas))

def scale(deployment_name, name, image, args, mounts, replicas):
    print("Scaling service {0} to {1} clients".format(deployment_name, replicas))

def remove(deployment_name):
    print("Removing service " + deployment_name)



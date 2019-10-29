import datetime, time

def create(deployment_name, name, image, args, mounts, replicas):
    print("Creating service {0} with {1} clients".format(deployment_name, replicas))
    global out
    out = open("logs/load_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".log","w+")
    out.write("timestamp,clients\n")
    out.write(str(int(round(time.time()))) + "," + str(replicas) + "\n")
    out.flush()
def scale(deployment_name, name, image, args, mounts, replicas):
    print("Scaling service {0} to {1} clients".format(deployment_name, replicas))
    out.write(str(int(round(time.time()))) + "," + str(replicas) + "\n")
    out.flush()

def remove(deployment_name):
    print("Removing service " + deployment_name)



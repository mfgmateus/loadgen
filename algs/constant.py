import math, logging, datetime, random, time, os

test_start = datetime.datetime.now()
test_name = test_start.strftime('%Y%m%d%H%M')
log_dir = "logs/" + test_name
info_file = log_dir + "/load_" + test_start.strftime("%Y%m%d%H%M") + ".txt"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def run(cluster, args):

    with open(info_file, "w") as f:
        f.write("name={0}\n".format(args.name))
        f.write("method=constant\n")
        f.write("cluster={0}\n".format(args.cluster))
        f.write("environment={0}\n".format(args.envargs))
        f.write("args={0}\n".format(args.args))
        f.write("duration={0}\n".format(args.duration))
        f.write("lambda={0}\n".format(args.lambd))

     # set the boundaries
    start = now = datetime.datetime.now()
    end   = now + datetime.timedelta(minutes=args.duration)

    cluster.create(args.service, args.name, args.image, args.args, args.mounts, args.lambd, args.duration, args.envargs)

    while datetime.datetime.now() < end:
        time.sleep(1)

    time.sleep(60)
    cluster.collect_data(args.dropbox_token)
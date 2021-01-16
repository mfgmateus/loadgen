import math, logging, datetime, random, time

def run(cluster, args):

     # set the boundaries
    start = now = datetime.datetime.now()
    end   = now + datetime.timedelta(minutes=args.duration)

    cluster.create(args.service, args.name, args.image, args.args, args.mounts, args.lambd, args.duration)

    while datetime.datetime.now() < end:
        time.sleep(1)
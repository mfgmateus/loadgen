import math, logging, datetime, random, time, os

test_start = datetime.datetime.now()
test_name = test_start.strftime('%Y%m%d%H%M')
log_dir = "logs/" + test_name
info_file = log_dir + "/load_" + test_start.strftime("%Y%m%d%H%M") + ".txt"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def run(cluster, args):

     # set the boundaries
    start = now = datetime.datetime.now()
    end   = now + datetime.timedelta(minutes=args.duration)

    # setup logger
    logger = logging.getLogger("run")

    A, T = args.sinusoid.split(',')

    with open(info_file, "w") as f:
        f.write("name={0}\n".format(args.name))
        f.write("method=sinusoid\n")
        f.write("cluster={0}\n".format(args.cluster))
        f.write("environment={0}\n".format(args.envargs))
        f.write("args={0}\n".format(args.args))
        f.write("duration={0}\n".format(args.duration))
        f.write("lambda={0}\n".format(args.lambd))
        f.write("amplitude={0}\n".format(A))
        f.write("period={0}\n".format(T))
    
    # The angular frequency  is aa scalar measure of rotation rate.
    # One revolution is equal to 2 radians, hence  = 2/T where
    # T is the period (measured in seconds),
    omega = 2.0 * math.pi / (float(T) * 60.0)
    A = float(A)
    logger.info('Using sine wave function with A=%f period=%f' % (A, omega))

    # the amplitude must be smaller than the lambda 
    assert(A < args.lambd)

    # general lambda
    lambd = args.lambd

    # set up the main values
    global num_client
    num_client = 0

    global alive

    #used to define poisson interarrival times - time to sleep in between processes
    global sleep_secs

    # until we finish
    while (now < end):
    
        if args.sinusoid:
            # The sine wave or sinusoid is a mathematical curve that describes
            # a smooth repetitive oscillation.
            # Its most basic form as a function of time (t) is:
            # y(t) = A * sin(2ft + ) = A * sin(t + )
            # where:
            #  -  is the phase (equal to 0)
            #  -  is evaluated at the previous step
            lambd = args.lambd + A * math.sin(omega * (now - start).total_seconds()) 
	
        # Poisson process:
        # The time between each pair of consecutive events has an exponential
        # distribution with parameter  and each of these inter-arrival times
        # is assumed to be independent of other inter-arrival times.
        if args.poisson:
        	sleep_secs = random.expovariate(lambd / 60.0)

        logger.debug('%s - Will sleep for %s sec' % (now, sleep_secs))
        logger.debug('Clients active = %s - lambda = %s' % (num_client, math.ceil(lambd)))
        
        replicas = int(math.ceil(lambd))

        time.sleep(sleep_secs)

        vlc_args = [args.args, ""]
    
        if num_client != replicas:
            logger.info("Scalling service to %s replicas" % (replicas))
            if num_client == 0:
                cluster.create(args.service, args.name, args.image, args.args, args.mounts, replicas, args.duration, args.envargs)
            else:
                cluster.scale(args.service, args.name, args.image, args.args, args.mounts, replicas, args.duration, args.envargs)
            num_client = replicas

        # refresh the timer
        now = datetime.datetime.now()

    time.sleep(60)
    cluster.collect_data(args.name, args.dropbox_token)
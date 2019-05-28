#!/usr/local/bin/python2.7
# encoding: utf-8
'''
Created on Sept 21, 2018

@author: pasquini
'''

import logging
import argparse
import datetime
import time
import random
import subprocess
import os
import threading
import math
import csv
import swarm
import k8s
from collections import deque

__version__ = 0.1
__updated__ = '2018-09-21'
DEBUG = 0

def run(cluster, args):

    # setup logger
    logger = logging.getLogger("run")

    # set the boundaries
    start = now = datetime.datetime.now()
    end   = now + datetime.timedelta(minutes=args.duration)

    # Null file, just open it for future use
    FNULL = open(os.devnull, 'w')

    # sinusoidal function
    if args.sinusoid:
        A, T = args.sinusoid.split(',')
        
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
                cluster.create(args.service, args.name, args.image, args.args, args.mounts, replicas)
            else:
                cluster.scale(args.service, args.name, args.image, args.args, args.mounts, replicas)
            num_client = replicas

        # refresh the timer
        now = datetime.datetime.now()


def main():
    
    logger = logging.getLogger("main")

    parser = argparse.ArgumentParser()
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    parser.add_argument('-V', '--version', action='version', version='%%(prog)s %s (%s)' % (program_version, program_build_date))
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
    parser.add_argument("-s", "--sinusoid", dest="sinusoid", metavar='A,P', help="set the sinusoidal lambda behavior, that varies with amplitude A on period P minutes around the lambda")
    parser.add_argument("-i", "--image", dest="image", help="The docker image to run", required=True)
    parser.add_argument("-n", "--name", dest="name", help="The application-name", required=True)
    parser.add_argument("-a", "--args", dest="args", nargs='+', help="The application arguments", required=False)
    parser.add_argument("-m", "--mounts", dest="mounts", help="The application dir mounts", required=False)
    parser.add_argument("-c", "--cluster", choices=["swarm", "k8s"], dest="cluster", help="The cluster to use", required=True)

    parser.add_argument('--poisson', dest='poisson', action='store_true')
    parser.add_argument('--no-poisson', dest='poisson', action='store_false')
    
    parser.set_defaults(poisson=True)
    parser.set_defaults(args=[])
    parser.set_defaults(mounts=[])

    # positional arguments (duration, lambda)
    parser.add_argument("-d", "--duration", dest="duration", type=float, help="set the duration of the experiment in minutes")
    parser.add_argument("-l", "--lambda", dest="lambd", type=float, help="set the (average) arrival rate of lambda clients/minute or normal level of functioning Rnorm for flash crowd")

    # Process arguments
    args = parser.parse_args()

    # print(args)

    # if args.verbose >= 1:
    #     logging.basicConfig(filename='rafael.log',level=logging.DEBUG)
    #     # setup logger
    #     logger.debug("Enabling debug mode")

    # else:
    #     # setup logger
    logging.basicConfig(filename='rafael.log',level=logging.INFO)


    args.service = service_name = args.name + "-" + "deployment"

    CLUSTER = k8s if args.cluster == "k8s" else swarm

    # print(CLUSTER)

    # exit()

    # main loop
    run(CLUSTER, args)

    CLUSTER.remove(args.service)

if __name__ == '__main__':
    main()
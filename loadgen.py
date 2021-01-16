#!/usr/local/bin/python2.7
# encoding: utf-8
'''
Created on Sept 21, 2018

@author: pasquini
'''

import logging
import argparse
from cluster import k8s, test
from algs import sinusoid, flashcrowd, constant
from collections import deque
import signal
import sys

global CLUSTER, SERVICE

CLUSTER = test

def signal_handler(sig, frame):
        print('Exiting gracefully!')
        CLUSTER.remove(SERVICE)
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

__version__ = 0.1
__updated__ = '2018-09-21'
DEBUG = 0

def run(cluster, args):

    if args.method == 'sinusoid':
        sinusoid.run(cluster, args)
    elif args.method == 'flashcrowd':
        flashcrowd.run(cluster, args)
    elif args.method == 'constant':
        constant.run(cluster, args)
    else:
        print("Method " + args.method + " is not valid!")

def main():
    
    logger = logging.getLogger("main")

    parser = argparse.ArgumentParser()
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    parser.add_argument('-V', '--version', action='version', version='%%(prog)s %s (%s)' % (program_version, program_build_date))
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
    parser.add_argument("-s", "--sinusoid", dest="sinusoid", metavar='A,P', help="set the sinusoidal lambda behavior, that varies with amplitude A on period P minutes around the lambda")
    parser.add_argument("-f", "--flashcrowd", dest="flash", metavar='R', help="set the flashcrowd behavior where R it is the RNORMAL")
    parser.add_argument("-i", "--image", dest="image", help="The docker image to run", required=True)
    parser.add_argument("-n", "--name", dest="name", help="The application-name", required=True)
    parser.add_argument("-a", "--args", dest="args", nargs='+', help="The application arguments", required=False)
    parser.add_argument("-m", "--method", dest="method", help="The method to run (sinusoid, flashcrowd)", required=True)
    parser.add_argument("-c", "--cluster", choices=["k8s", "test"], dest="cluster", help="The cluster to use", required=True)

    parser.add_argument('--poisson', dest='poisson', action='store_true')
    parser.add_argument('--no-poisson', dest='poisson', action='store_false')
    
    parser.set_defaults(poisson=True)
    parser.set_defaults(args=[])
    parser.set_defaults(mounts=[])

    parser.add_argument("-d", "--duration", dest="duration", type=int, help="set the duration of the experiment in minutes")
    parser.add_argument("-l", "--lambda", dest="lambd", type=int, help="set the (average) arrival rate of lambda clients/minute or normal level of functioning Rnorm for flash crowd")
    parser.add_argument("-p", "--period", dest="period", type=int, help="The period of flashcrowd")
    parser.add_argument("-o", "--ocurrences", dest="ocurrences", type=int, help="The number of flash ocurrences")
    parser.add_argument("-sl", "--shock-level", dest="shock_level", type=int, help="The number of flash ocurrences")

    # Process arguments
    args = parser.parse_args()

    logging.basicConfig(filename='loadgen.log',level=logging.INFO)

    args.service = service_name = args.name + "-" + "deployment"

    global SERVICE, CLUSTER
    
    CLUSTER = test
    SERVICE = args.service

    if args.cluster == 'k8s':
        CLUSTER = k8s

    run(CLUSTER, args)

    CLUSTER.remove(args.service)

if __name__ == '__main__':
    main()
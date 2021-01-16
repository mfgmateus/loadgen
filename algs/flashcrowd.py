import random, math, time, logging, datetime

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def run(cluster, args):

	period = args.period #15
	lambd = args.lambd #10
	shock_level = args.shock_level #2
	duration = args.duration #30
	ocurrences = args.ocurrences #5

	start = now = datetime.datetime.now()
	end   = now + datetime.timedelta(minutes=duration)	

	half_period = period/2

	flash_time = half_period / (ocurrences *1.0)

	flash_time_seconds = flash_time * 60

	#1t rampup
	#2t rampdown
	#2t sustained 

	rampup = (flash_time / 5.0) * 1
	sustained = (flash_time / 5.0) * 2
	rampdown = (flash_time / 5.0) * 2

	last_event_ending = flash_time
	last_event_start = 0

	ru_seconds = math.ceil(rampup * 60)
	ru_clients = (lambd * shock_level) - lambd
	ru_sleep_seconds = ru_seconds / ru_clients

	sustained_seconds = math.ceil(sustained * 60)

	rd_seconds = math.ceil(rampdown * 60)
	rd_clients = (lambd * shock_level) - lambd
	rd_sleep_seconds = rd_seconds / rd_clients


	clients = lambd
	maximum_clients = clients + ru_clients
	minimum_clients = clients

	end = datetime.datetime.now() + datetime.timedelta(minutes=duration)

	periods = int(duration / period)

	cluster.create(args.service, args.name, args.image, args.args, args.mounts, clients, args.duration)

	for i in range(0, periods):

		events = []

		for i in range(0, ocurrences):
			event = math.ceil(random.uniform(flash_time_seconds/1.5, flash_time_seconds))
			events.append(event)

		end_period  = datetime.datetime.now() + datetime.timedelta(minutes=period)

		print("End of this period will be: {0}".format(end_period))

		for event in events:

			# logging.info("Waiting for event start")
			time.sleep(event)
			# logging.info("New event started")

			# logging.info("Starting rampup!")
			while clients < maximum_clients:
				clients += 1
				cluster.scale(args.service, args.name, args.image, args.args, args.mounts, clients, args.duration)
				#logging.info("Number of clients increased to {0}".format(clients))
				time.sleep(ru_sleep_seconds)
			
			# logging.info("Now in sustained time")
			time.sleep(sustained_seconds)
			
			# logging.info("Starting rampdown")
			while clients > minimum_clients:
				clients -= 1
				cluster.scale(args.service, args.name, args.image, args.args, args.mounts, clients, args.duration)
				#logging.info("Number of clients decreased to {0}".format(clients))
				time.sleep(rd_sleep_seconds)
			
			# logging.info("Event finished!")

		while datetime.datetime.now() < end_period:
			time.sleep(10)
			# logging.info("Waiting for period ending!")


	while datetime.datetime.now() < end:
		time.sleep(10)
		# logging.info("Waiting for duration ending!")
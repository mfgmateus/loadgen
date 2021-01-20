import random, math, time, logging, datetime, os

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

test_start = datetime.datetime.now()
test_name = test_start.strftime('%Y%m%d%H%M')
log_dir = "logs/" + test_name
info_file = log_dir + "/load_" + test_start.strftime("%Y%m%d%H%M") + ".txt"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def run(cluster, args):

	period = args.period #15
	lambd = args.lambd #10
	shock_level = args.shock_level #2
	duration = args.duration #30
	ocurrences = args.ocurrences #5

	with open(info_file, "w") as f:
		f.write("name={0}\n".format(args.name))
		f.write("method=flashcrowd\n")
		f.write("cluster={0}\n".format(args.cluster))
		f.write("environment={0}\n".format(args.envargs))
		f.write("args={0}\n".format(args.args))
		f.write("duration={0}\n".format(args.duration))
		f.write("lambda={0}\n".format(args.lambd))
		f.write("period={0}\n".format(period))
		f.write("shock_level={0}\n".format(shock_level))
		f.write("ocurrences={0}\n".format(ocurrences))

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

	cluster.create(args.service, args.name, args.image, args.args, args.mounts, clients, args.duration, args.envargs)

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
				cluster.scale(args.service, args.name, args.image, args.args, args.mounts, clients, args.duration, args.envargs)
				#logging.info("Number of clients increased to {0}".format(clients))
				time.sleep(ru_sleep_seconds)
			
			# logging.info("Now in sustained time")
			time.sleep(sustained_seconds)
			
			# logging.info("Starting rampdown")
			while clients > minimum_clients:
				clients -= 1
				cluster.scale(args.service, args.name, args.image, args.args, args.mounts, clients, args.duration, args.envargs)
				#logging.info("Number of clients decreased to {0}".format(clients))
				time.sleep(rd_sleep_seconds)
			
			# logging.info("Event finished!")

		while datetime.datetime.now() < end_period:
			time.sleep(10)
			# logging.info("Waiting for period ending!")


	while datetime.datetime.now() < end:
		time.sleep(10)
		# logging.info("Waiting for duration ending!")
	
	time.sleep(60)
	cluster.collect_data(args.name, args.dropbox_token)
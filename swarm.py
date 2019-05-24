import docker, os, sys

client = docker.from_env()

def create(service_name, name, image, args, mounts, replicas):
    service = None
    service = client.services.create(name=service_name, image=image, args=args, mounts=mounts)

def scale(service_name, replicas):
    if replicas >= 1:
        service = client.services.get(service_name)
        service.scale(replicas)

def remove(service_name):
    service = client.services.get(service_name)
    service.remove()


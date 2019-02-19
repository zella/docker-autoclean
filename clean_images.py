import docker

client = docker.from_env()

result = client.images.prune({"dangling": False})
print(result)
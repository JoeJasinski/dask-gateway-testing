from dask_gateway import Gateway

gateway = Gateway("http://traefik-dask-gateway:80")
print(gateway.list_clusters())
cluster = gateway.new_cluster()
client = cluster.get_client()
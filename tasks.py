import os
import json
from invoke import task


release = os.environ.get("DASKGW_HELM_RELEASE_NAME", "dask-gateway")
docker_image = os.environ.get("DASKGW_DOCKER_IMAGE", "dask_client:0.1")
cluster_name = os.environ.get("DASKGW_KIND_CLUSTER_NAME", "jjj-cluster")
pod_name = os.environ.get("DASKGW_CLIENT_POD_NAME", "dask-client")

##########################
# Kind Cluster
#########################

@task
def install_kind(ctx):
    ctx.run(f"kind create cluster --config cluster.yaml --name {cluster_name}", echo=True)


@task
def uninstall_kind(ctx):
    ctx.run(f"kind delete cluster --name {cluster_name}", echo=True)

##########################
# Dask Gateway
#########################


@task
def uninstall_dask(ctx):
    ctx.run(f"helm uninstall {release}  --wait", echo=True, warn=True)

@task(pre=[uninstall_dask])
def install_dask(ctx):
    ctx.run(f"helm upgrade {release} dask-gateway "
            f"  --repo=https://helm.dask.org "
            f"  --install "
            f"  --values helm-values.yaml",
            echo=True
    )

@task
def delete_daskclusters(ctx):

    res = ctx.run(f"kubectl  get daskclusters -o json", echo=True)
    clusters = json.loads(res.stdout)
    cluster_names = [cl['metadata']['name'] for cl in clusters['items']]
    for cluster_name in cluster_names:
        ctx.run(f"kubectl delete daskclusters {cluster_name}", echo=True, warn=True)

##########################
# Client Pod
#########################

@task
def build_client(ctx):
    ctx.run(f"docker build -f docker/Dockerfile -t {docker_image} docker/", echo=True)

@task
def uninstall_client(ctx):
    ctx.run(f"kubectl delete po {pod_name}", echo=True, warn=True)

@task(pre=[uninstall_client, build_client])
def install_client(ctx):
    ctx.run(f"kind load docker-image {docker_image} --name {cluster_name}", echo=True)
    ctx.run(f"kubectl run --image {docker_image} {pod_name}", echo=True)

@task
def shell(ctx):
    ctx.run(f"kubectl exec -it {pod_name} -- bash", echo=True, pty=True)


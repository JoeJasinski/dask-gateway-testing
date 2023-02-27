import os
import json
from invoke import task


release = os.environ.get("DASKGW_HELM_RELEASE_NAME", "dask-gateway")
docker_image_client = os.environ.get("DASKGW_DOCKER_IMAGE_CLIENT", "dask_client:0.1")
docker_image_dask_gateway = os.environ.get("DASKGW_DOCKER_IMAGE_DASK_GATEWAY", "dask_gateway:0.1")
kind_cluster_name = os.environ.get("DASKGW_KIND_CLUSTER_NAME", "jjj-cluster")
pod_name = os.environ.get("DASKGW_CLIENT_POD_NAME", "dask-client")

##########################
# Kind Cluster
#########################

@task
def install_k8s(ctx):
    """Create the Kind cluster"""
    ctx.run(f"kind create cluster --config cluster.yaml --name {kind_cluster_name}", echo=True)


@task
def uninstall_k8s(ctx):
    """Destroy the Kind cluster"""
    ctx.run(f"kind delete cluster --name {kind_cluster_name}", echo=True)

##########################
# Gateway Pod
#########################

@task
def docker_build_gateway(ctx):
    """Build the Dask images needed for the scheduler and workers"""
    ctx.run(f"docker build -f docker/dask-gateway/Dockerfile -t {docker_image_dask_gateway} docker/dask-gateway/", echo=True)
    ctx.run(f"kind load docker-image {docker_image_dask_gateway} --name {kind_cluster_name}", echo=True)

##########################
# Dask Gateway
#########################


@task
def uninstall_dask(ctx):
    """Uninstall the Dask Helm chart"""
    ctx.run(f"helm uninstall {release}  --wait", echo=True, warn=True)

@task(pre=[uninstall_dask, docker_build_gateway])
def install_dask(ctx):
    """Install the Dask Helm chart"""
    image_parts = docker_image_dask_gateway.split(":")
    if len(image_parts) == 1:
        image_name = image_parts
        image_tag = "latest"
    elif len(image_parts) == 2:
        image_name = image_parts[0]
        image_tag = image_parts[1]

    ctx.run(f"helm upgrade {release} dask-gateway "
            f"  --repo=https://helm.dask.org "
            f"  --set gateway.backend.image.name={image_name}"
            f"  --set gateway.backend.image.tag={image_tag}"
            f"  --install "
            f"  --values helm-values.yaml",
            echo=True
    )

@task
def delete_daskclusters(ctx):
    """Delete Dask Cluster CRs (which deletes all cluster resources)"""
    res = ctx.run(f"kubectl  get daskclusters -o json", echo=True)
    clusters = json.loads(res.stdout)
    cluster_names = [cl['metadata']['name'] for cl in clusters['items']]
    for cluster_name in cluster_names:
        ctx.run(f"kubectl delete daskclusters {cluster_name}", echo=True, warn=True)


##########################
# Client Image and Pod
#########################

@task
def docker_build_client(ctx):
    """Build the Dask Client Docker image"""
    ctx.run(f"docker build -f docker/dask-client/Dockerfile -t {docker_image_client} docker/dask-client/", echo=True)
    ctx.run(f"kind load docker-image {docker_image_client} --name {kind_cluster_name}", echo=True)

@task
def uninstall_client(ctx):
    """Delete the Dask Client pd"""
    ctx.run(f"kubectl delete po {pod_name}", echo=True, warn=True)

@task(pre=[uninstall_client, docker_build_client])
def install_client(ctx):
    """Create the Dask client pod"""
    ctx.run(f"kubectl run --image {docker_image_client} {pod_name}", echo=True)

@task
def shell(ctx):
    """Enter an interactive Dask Client shell"""
    ctx.run(f"kubectl exec -it {pod_name} -- bash", echo=True, pty=True)


# Dask Gateway Example Kubernetes

This is just my test of the dask gateway, so I can learn
how it works.

## Requirements

- Kubernetes Kind binary (tested with version v0.17.0)
- Kubectl binary (tested with version 1.26.0)
- Helm binary (tested with version 3.11.1)
- Pyinvoke (tested with version 1.4.1)

Tested on Ubuntu 22.04

## Install

Start the kind cluster

    inv install-kind

Install Dask

    inv install-dask

Install a Dask test client pod 

    inv install-client

Enter into the test pod to test stuff

    inv shell

Once inside the test pod, create a test cluster

    python -i script.py

# Uninstall

Delete all of the dask clusters

    inv delete-daskclusters

Uninstall the dask test pod 

    inv uninstall-client

Uninstall the Dask Gateway

    inv uninstall-dask

Shut down the kind cluster

    inv uninstall-kind


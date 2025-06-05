#!/bin/bash


if [ -z "${EKS_NODE_ROLE}" ]; then
  echo "Error: EKS_NODE_ROLE environment variable is not set"
  echo "Please make sure that you have installed the TF components earlier."
  exit 1
fi

# First install the NVidia device plugin. Note that you donot need the GPU OPerator becuase AMazon EKS GPU Optimised images already have the NVIDIA drivers installed.
kubectl create -f device-plugin.yaml

# Then create the GPU Node Pool
cp gpu-nodepool.yaml /tmp/gpu-nodepool.yaml
sed -i '' "s|<ADD_NODE_ROLE>|${EKS_NODE_ROLE}|g" /tmp/gpu-nodepool.yaml
kubectl create -f /tmp/gpu-nodepool.yaml
rm /tmp/gpu-nodepool.yaml

# Then create the Graviton Node Pool
cp graviton-nodepool.yaml /tmp/graviton-nodepool.yaml
sed -i '' "s|<ADD_NODE_ROLE>|${EKS_NODE_ROLE}|g" /tmp/graviton-nodepool.yaml
kubectl create -f /tmp/graviton-nodepool.yaml
rm /tmp/graviton-nodepool.yaml

echo "#### REMOVING THE GENERAL_PURPOSE NODEPOOL ####"
kubectl delete nodepool general-purpose 

# Deploy the GPU workload
kubectl create -f storage-class.yaml


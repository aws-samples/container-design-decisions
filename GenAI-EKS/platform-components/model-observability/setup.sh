#!/bin/bash
kubectl create namespace genai
kubectl create -f langfuse-sa.yaml -n genai
kubectl create -f langfuse.yaml -n genai

# helm repo add langfuse https://langfuse.github.io/langfuse-k8s
# helm repo update

# # SALT=$(openssl rand -hex 16)
# SALT="NOT_SALTY"


# helm install langfuse langfuse/langfuse --create-namespace -n genai -f values.yaml

echo "Waiting for Langfuse pods to be ready..."
kubectl wait --for=condition=ready pods --selector=app.kubernetes.io/instance=langfuse --timeout=300s -n genai



echo "Refer to README.md to access Langfuse and define Public/Private Keys"


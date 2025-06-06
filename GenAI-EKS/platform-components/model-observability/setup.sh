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

echo "Creating Langfuse web ingress..."
kubectl apply -f langfuse-web-ingress.yaml -n genai

echo "Waiting for Langfuse ingress to be ready..."
# Wait for the ingress to get an address (timeout after 5 minutes)
timeout=300
start_time=$(date +%s)
while true; do
  current_time=$(date +%s)
  elapsed=$((current_time - start_time))
  
  if [ $elapsed -gt $timeout ]; then
    echo "Timeout waiting for ingress address"
    exit 1
  fi
  
  INGRESS_HOSTNAME=$(kubectl get ingress langfuse-web-ingress-alb -n genai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
  
  if [ -n "$INGRESS_HOSTNAME" ] && [ "$INGRESS_HOSTNAME" != "null" ]; then
    echo "Langfuse ingress is ready!"
    break
  fi
  
  echo "Waiting for ingress address... (${elapsed}s elapsed)"
  sleep 10
done

# Export the ingress endpoint to LANGFUSE_URL
export LANGFUSE_URL="http://${INGRESS_HOSTNAME}"
echo "LANGFUSE_URL has been set to: ${LANGFUSE_URL}"
echo "You can access Langfuse at: ${LANGFUSE_URL}"

echo "Refer to README.md to access Langfuse and define Public/Private Keys"


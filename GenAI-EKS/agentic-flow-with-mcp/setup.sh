#!/bin/bash

if [ -z "${LANGFUSE_PUBLIC_KEY}" ]; then
  echo "Error: LANGFUSE_PUBLIC_KEY environment variable is not set"
  echo "Please make sure that you have installed the Langfuse script and it has set the LANGFUSE_PUBLIC_KEY environment variable."
  exit 1
fi

if [ -z "${LANGFUSE_SECRET_KEY}" ]; then
  echo "Error: LANGFUSE_SECRET_KEY environment variable is not set"
  echo "Please make sure that you have installed the Langfuse script and it has set the LANGFUSE_SECRET_KEY environment variable."
  exit 1
fi

if [ -z "${LLAMA_VISION_MODEL_KEY}" ]; then
  echo "Error: LLAMA_VISION_MODEL_KEY environment variable is not set"
  echo "Please go through README to create this."
  exit 1
fi

# Create namespace if it doesn't exist
kubectl get namespace genai &>/dev/null || kubectl create namespace genai

kubectl delete deployment mcp-weather -n genai || true
kubectl delete deployment mcp-fruit-services -n genai || true
kubectl delete deployment agentic-app -n genai || true

kubectl delete configmap mcp-weather-config -n genai || true
kubectl delete configmap mcp-fruit-prices-config -n genai || true
kubectl delete configmap agentic-app-config -n genai || true

# Create ConfigMap from the Python file
kubectl create configmap mcp-weather-config \
  --from-file=mcp-weather.py \
  -n genai \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply the deployment and service
kubectl apply -f deployments/mcp-weather-deployment.yaml -n genai

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/mcp-weather -n genai

echo "MCP Weather Service deployed successfully!"
echo "Service is accessible at: http://mcp-weather.genai.svc.cluster.local"


# Create ConfigMap from the Python file
kubectl create configmap mcp-fruit-prices-config \
  --from-file=mcp-fruit-prices.py \
  -n genai \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply the deployment and service
kubectl apply -f deployments/mcp-fruit-prices-deployment.yaml -n genai

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/mcp-fruit-services -n genai

echo "MCP fruit-prices Service deployed successfully!"
echo "Service is accessible at: http://mcp-fruit-services.genai.svc.cluster.local"

# local portforward
# kubectl port-forward services/mcp-fruit-services 8000:8000 -n genai &
# kubectl port-forward services/mcp-weather 7000:8000 -n genai &


echo "Deploying the agentic application..."
kubectl create configmap agentic-app-config \
  --from-file=langgraph-agent-react-agent.py \
  -n genai \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply the deployment and service
cp deployments/agentic-app.yaml /tmp/agentic-app.yaml
sed -i '' "s|<GENERATE AND PUT YOUR LANGFUSE SECRET KEY HERE>|${LANGFUSE_SECRET_KEY}|g" /tmp/agentic-app.yaml
sed -i '' "s|<GENERATE AND PUT YOUR LANGFUSE PUBLIC KEY HERE>|${LANGFUSE_PUBLIC_KEY}|g" /tmp/agentic-app.yaml
sed -i '' "s|<ADD LLAMA_VISION_MODEL_KEY>|${LLAMA_VISION_MODEL_KEY}|g" /tmp/agentic-app.yaml

kubectl apply -f /tmp/agentic-app.yaml -n genai
rm /tmp/agentic-app.yaml

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/agentic-app -n genai

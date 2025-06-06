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

cp litellm-deployment.yaml /tmp/litellm-deployment.yaml
sed -i '' "s|<GENERATE AND PUT YOUR LANGFUSE SECRET KEY HERE>|${LANGFUSE_SECRET_KEY}|g" /tmp/litellm-deployment.yaml

sed -i '' "s|<GENERATE AND PUT YOUR LANGFUSE PUBLIC KEY HERE>|${LANGFUSE_PUBLIC_KEY}|g" /tmp/litellm-deployment.yaml






kubectl create -f /tmp/litellm-deployment.yaml -n genai

# Create the litellm ingress
kubectl create -f litellm-ingress.yaml -n genai

echo "Waiting for ingress to be provisioned with an ALB endpoint..."
# Wait for the ingress to be provisioned with a hostname
max_retries=30
counter=0
while [ $counter -lt $max_retries ]; do
  GATEWAY_URL=$(kubectl get ingress litellm-ingress-alb -n genai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
  
  if [ -n "$GATEWAY_URL" ]; then
    echo "Ingress successfully provisioned!"
    echo "GATEWAY_URL=$GATEWAY_URL"
    
    # Export the environment variable
    export GATEWAY_URL
    
    # Add to shell rc files for persistence
    echo "# Added by model-gateway setup script" >> ~/.bashrc
    echo "export GATEWAY_URL=$GATEWAY_URL" >> ~/.bashrc
    if [ -f ~/.zshrc ]; then
      echo "# Added by model-gateway setup script" >> ~/.zshrc
      echo "export GATEWAY_URL=$GATEWAY_URL" >> ~/.zshrc
    fi
    
    break
  fi
  
  echo "Waiting for ALB endpoint to be assigned... (attempt $counter/$max_retries)"
  sleep 10
  counter=$((counter+1))
done

if [ $counter -eq $max_retries ]; then
  echo "Warning: Timed out waiting for ingress to be provisioned with an ALB endpoint."
  echo "You may need to manually export the GATEWAY_URL once the ALB is provisioned:"
  echo "export GATEWAY_URL=\$(kubectl get ingress litellm-ingress-alb -n genai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"
fi

rm /tmp/litellm-deployment.yaml
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


rm /tmp/litellm-deployment.yaml
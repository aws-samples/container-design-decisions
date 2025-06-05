#!/bin/bash

if [ -z "${HF_TOKEN}" ]; then
  echo "Error: HF_TOKEN environment variable is not set"
  echo "Please set it with: export HF_TOKEN=your_huggingface_token_here"
  exit 1
fi

# Apply all YAML files in the current directory
for yaml_file in *.yaml; do
  echo "Applying $yaml_file..."
  cp "$yaml_file" "/tmp/$yaml_file"
  sed -i '' "s|HUGGING_FACE_HUB_TOKEN\n          value: \"\"|HUGGING_FACE_HUB_TOKEN\n          value: \"${HF_TOKEN}\"|g" "/tmp/$yaml_file"
  kubectl apply -f "/tmp/$yaml_file" -n genai
  rm "/tmp/$yaml_file"
done
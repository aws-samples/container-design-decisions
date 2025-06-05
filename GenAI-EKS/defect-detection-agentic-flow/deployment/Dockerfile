# This Dockerfile contains all dependencies and the code to run the fault detection multi-agent system.

# FOR CUDA
# FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04
# RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*

# THIS image should be in a private repo
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt


COPY fault-detection-multi-agent.py /app/fault-detection-multi-agent.py
COPY classify-conv-server.py /app/classify-conv-server.py
COPY ui.py /app/ui.py

# SHOULD BE IN THE FSX or S# store to download 
# TODO
# COPY weights /app/y-weights/


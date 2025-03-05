FROM python:3.11-slim-bookworm

RUN apt update && apt -y upgrade 

# Create the working directory in the container.
WORKDIR /llmhub-api

# Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Copy the requirements file located here and copy it into the container's working directory.
COPY ../../requirements.txt ./

# Pip Dependencies
RUN apt-get install -y curl
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose
RUN apt-get -y install git
RUN apt-get update && apt-get install -y build-essential libpq-dev
RUN pip install --upgrade pip 
RUN pip install -r ./requirements.txt
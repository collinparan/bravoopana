# Description

This template is for the Bravo Hackathon

# Requirements

- docker
- docker-compose

# Deploying using docker-compose

1. Build docker image

```
docker-compose build
```

2. Deploy docker all containers

```
docker-compose up -d
```

3. (Optional) Deploying or recreating one container at time for testing

```
docker-compose up -d --force-recreate --build <container name>
```
Example:
```
docker-compose up -d --force-recreate --build bravo_frontend
```

# Running only the tools 

```
docker-compose -f docker-compose.tools.yml up -d --force-recreate --build
```

# Research Reference Materials

Tagging: https://docs.docker.com/build/bake/compose-file/#specification
Tagging 2: https://stackoverflow.com/questions/33816456/how-to-tag-docker-image-with-docker-compose

Tarball offline: https://dev.to/shandesai/prepare-your-docker-compose-stack-as-a-tarball-for-offline-installations-40cd


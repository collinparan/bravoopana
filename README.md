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
docker-compose up -d --force-recreate --build front_end
```

#!/bin/bash

## get ECR_URL from env
$(aws ecr get-login --no-include-email --region ap-northeast-2)
docker build -t sonarqube .
docker tag sonarqube:latest ${ECR_URL}:/sonarqube:latest
docker push ${ECR_URL}/sonarqube:latest

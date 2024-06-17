#!/bin/bash
#############################
# Example varialbes
#############################
REPO_ADMIN="admin@dongdorrong.io"
REPO_URL="harbor.dongdorrong.io"


# Namespace << develop | staging | develop
target_namespace="develop"

# Application Name <<< dongdorrong-bank | dongdorrong-market | dongdorrong-platform
harbor_project="dongdorrong-bank"

harbor_credential=$(cat default_harbor_credential.json)
harbor_user=$(echo "$harbor_credential" | jq -r '.name')
harbor_secret=$(echo "$harbor_credential" | jq -r '.secret')

docker_auth=$(printf "%s:%s" "$harbor_user" "$harbor_secret" | base64)
docker_config="{\"auths\": {\"$REPO_URL\": {\"username\": \"$harbor_user\",\"password\": \"$harbor_secret\",\"email\": \"$REPO_ADMIN\",\"auth\": \"$docker_auth\"}}}"

kube_secret=$(echo "$docker_config" | base64)

cp default_kube_secret.yaml secret_harbor.yaml

yq eval ".metadata.name = \"secret-$harbor_project\"" -i secret_harbor.yaml
yq eval ".metadata.namespace = \"$target_namespace\"" -i secret_harbor.yaml
yq eval ".data[\".dockerconfigjson\"] = \"$kube_secret\"" -i secret_harbor.yaml

kubectl apply -f secret_harbor.yaml
if [ $? -ne 0 ]; then
    echo "Error applying Kubernetes secret."
    exit 1
fi

sleep 3
rm -rf secret_harbor.yaml

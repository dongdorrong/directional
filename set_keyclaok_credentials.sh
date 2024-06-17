#!/bin/bash
#############################
# Example varialbes
#############################
KEYCLOAK_DOMAIN="keycloak.dongdorrong.io"
KEYCLOAK_REALM="dongdorrong"


echo -n "Enter your ID: "
read USER_ID

echo -n "Enter your password: "
read -s USER_PW

TOKEN=`curl -s -k -X POST https://$KEYCLOAK_DOMAIN/auth/realms/$KEYCLOAK_REALM/protocol/openid-connect/token \
-d grant_type=password \
-d client_id=kubernetes-client \
-d scope=openid \
-d username=$USER_ID \
-d password="$USER_PW"`

echo

ID_TOKEN=`echo $TOKEN | jq -r ".id_token"`
REFRESH_TOKEN=`echo $TOKEN | jq -r ".refresh_token"`

kubectl config set-credentials $USER_ID \
--auth-provider=oidc \
--auth-provider-arg=idp-issuer-url="https://$KEYCLOAK_DOMAIN/auth/realms/$KEYCLOAK_REALM" \
--auth-provider-arg=client-id="kubernetes-client" \
--auth-provider-arg=id-token="$ID_TOKEN" \
--auth-provider-arg=refresh-token="$REFRESH_TOKEN"

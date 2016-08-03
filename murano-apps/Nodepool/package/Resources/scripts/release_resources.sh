#!/usr/bin/env bash

source creds

set -x

# Get server ids.
server_ids=$(mysql -u nodepool --password=nodepool nodepool -e 'select external_id from node' | grep -o '[-0-9a-f]\{36\}')
image_ids=$(mysql -u nodepool --password=nodepool nodepool -e 'select external_id from snapshot_image' | grep -o '[-0-9a-f]\{36\}')

# Get token and service catalog.
resp=$(curl -H "Content-Type: application/json" -X POST "$OS_AUTH_URL/tokens" --data '{"auth": {"tenantName": '"$OS_TENANT_NAME"', "passwordCredentials": {"username": '"$OS_USERNAME"', "password": '"$OS_PASSWORD"'}}}')

token=$(echo "$resp" | json_pp | grep -A15 '"token"' | sed -e '/"tenant"/,+7d' | grep '"id"' | cut -d '"' -f 4)
nova_url=$(echo "$resp" | json_pp | grep '8774/v2' | grep publicURL | cut -d '"' -f 4)
glance_url=$(echo "$resp" | json_pp | grep ':9292' | grep publicURL | cut -d '"' -f 4)

# Clean up servers.
for id in $server_ids
do
  curl -X DELETE -H "X-Auth-Token: $token" "$nova_url/servers/$id"
done

# Clean up images.
for id in $image_ids
do
  curl -X DELETE -H "X-Auth-Token: $token" "$glance_url/v1/images/$id"
done

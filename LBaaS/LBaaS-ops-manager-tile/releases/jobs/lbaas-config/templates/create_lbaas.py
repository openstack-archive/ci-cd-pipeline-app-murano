import json
import time
import uuid

import requests

BROKER_URL = 'http://localhost:8080/v2'

instance_id = str(uuid.uuid4())

# Create LBaaS.
requests.put(
    "%s/service_instances/%s" % (BROKER_URL, instance_id),
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'service_id': 'io.murano.apps.lbaas.HAProxy'}),
    auth=('user', 'password')
)

status = ''
answer = None

while status != 'succeeded':
    time.sleep(20)

    # Get status of provisioning.
    resp = requests.get(
        "%s/service_instances/%s/last_operation" % (BROKER_URL, instance_id),
        auth=('user', 'password')
    )

    answer = resp.json()

    status = answer['state']
    print ("STATUS = %s" % status)

    if status == 'failed':
        print ("LBaaS deployment finished with errors.")
        exit(1)


# Get LBaaS URL.
resp = requests.put(
    "%s/service_instances/%s/service_bindings/%s" % (
        BROKER_URL, instance_id, str(uuid.uuid4())
    ),
    headers={'Content-Type': 'application/json'},
    data=json.dumps(
        {'service_id': 'io.murano.apps.lbaas.HAProxy'}
    ),
    auth=('user', 'password')
)

url = resp.json()['credentials']['uri']

print(url)
print(instance_id)

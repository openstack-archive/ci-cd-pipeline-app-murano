# Copyright 2015 - Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
import os
import six
import sys
import uuid

import bottle
from keystoneclient.v3 import client as keystoneclient
from muranoclient.v1 import client as muranoclient

# Constant representing the API version supported by Cloud Controller.
X_BROKER_API_VERSION = 2.7
X_BROKER_API_VERSION_NAME = 'X-Broker-Api-Version'
PORT_VAR_NAME = 'SERVICE_BROKER_PORT'


if len(sys.argv) < 2:
    print("Usage: %s <path-to-config.json>" % __file__)
    sys.exit(1)

config = json.load(open(sys.argv[1]))

USER = config['username']
PASSWORD = config['password']
TENANT = config['tenant_name']
AUTH_URL = config['auth_url']
KEY_NAME = config['keyname']
IMAGE_NAME = config['image_name']


SERVICES = [
    {
        'id': 'io.murano.apps.lbaas.HAProxy',
        'name': 'LBaaS-service',
        'description': 'TBD',
        'bindable': True,
        'plans': [{
            'id': 'standard_plan',
            'name': 'm1.medium',
            'description': 'Creates an instance with m1.medium flavor on OpenStack.'
        }]
    }
]


def keystone_client():
    return keystoneclient.Client(
        username=USER,
        password=PASSWORD,
        auth_url=AUTH_URL,
        project_name=TENANT
    )


def murano_client():
    ks_client = keystone_client()

    murano_url = ks_client.service_catalog.url_for(
        service_type='application_catalog'
    )

    return muranoclient.Client(
        murano_url,
        auth_url=AUTH_URL,
        tenant=ks_client.project_id,
        token=ks_client.auth_token
    )


def normalize_instance_id(instance_id):
    prefix = "CF-LBaaS-"
    instance_id = instance_id[:-len(prefix)]

    return "%s%s" % (prefix, instance_id)


def ensure_package_by_fqn(packages, fqn):
    filtered = list(filter(
        lambda p: p.fully_qualified_name == fqn,
        packages
    ))

    if len(filtered) > 0:
        return filtered[0]
    else:
        bottle.abort(400, 'Requested service does not exist: %s' % fqn)


def get_env_by_name(murano, name):
    envs = list(
        filter(lambda e: e.name == name, murano.environments.list())
    )

    if not envs:
        return None

    return envs[0]


def get_lbaas_object_model(instance_id, keyname, image_name, impl='haproxy'):
    return {
        "instance":
        {
            "assignFloatingIp": "true",
            "keyname": keyname,
            "image": image_name,
            "name": instance_id,
            "flavor": "m1.medium",
            "?":
            {
                "type": "io.murano.resources.LinuxMuranoInstance",
                "id": six.text_type(uuid.uuid4())
            }
        },
        "name": "HAProxyBasedLBaaS",
        "?": {
            "_26411a1861294160833743e45d0eaad9": {
                "name": "HAProxyBasedLBaaS"
            },
            "type": "io.murano.apps.lbaas.HAProxy",
            "id": six.text_type(uuid.uuid4())
        },
        "implementation": impl
    }


@bottle.error(401)
@bottle.error(404)
@bottle.error(409)
@bottle.error(410)
def error(error):
    bottle.response.content_type = 'application/json'

    return '{"error": "%s"}' % error.body


def authenticate(username, password):
    return True


@bottle.route('/v2/catalog', method='GET')
@bottle.auth_basic(authenticate)
def catalog():
    """Return the catalog of services handled by this broker.

    GET /v2/catalog:

    HEADER:
        X-Broker-Api-Version: <version>

    return:
        JSON document with details about the
        services offered through this broker
    """
    api_version = bottle.request.headers.get('X-Broker-Api-Version')

    if not api_version or float(api_version) < X_BROKER_API_VERSION:
        bottle.abort(
            409,
            "Missing or incompatible %s. Expecting version %0.1f"
            " or later" % (X_BROKER_API_VERSION_NAME, X_BROKER_API_VERSION)
        )
    return {"services": SERVICES}


@bottle.route('/v2/service_instances/<instance_id>', method='PUT')
@bottle.auth_basic(authenticate)
def provision(instance_id):
    """Provision an instance of this service for the given org and space.

    PUT /v2/service_instances/<instance_id>:
        <instance_id> is provided by the Cloud
          Controller and will be used for future
          requests to bind, unbind and deprovision

    BODY:
        {
            "organization_guid": "org-guid-here",
            "plan_id":           "plan-guid-here",
            "service_id":        "service-guid-here",
            "space_guid":        "space-guid-here",
            "parameters":        {
                "parameter1": 1,
                "parameter2": "value"
          }
        }

    returns:
        JSON document with details about the
        services offered through this broker

    202 ACCEPTED in case if it is needed to trigger CF to poll progress.
    """
    instance_id = normalize_instance_id(instance_id)

    if bottle.request.content_type != 'application/json':
        bottle.abort(
            415,
            'Unsupported Content-Type: expecting application/json'
        )

    # Get the JSON document in the body.
    provision_details = bottle.request.json

    # Provision the service.
    service_id = provision_details['service_id']

    # Check that service is valid for current service broker.
    assert any(service_id == s['id'] for s in SERVICES)

    murano = murano_client()

    ensure_package_by_fqn(
        murano.packages.list(),
        service_id
    )

    # TODO(nmakhotkin): It may make sense for the broker to associate the
    # TODO(nmakhotkin): new instance with service/plan/org/space.
    # Check for case of already provisioned service.
    if get_env_by_name(murano, instance_id):
        bottle.abort(
            409,
            'The requested service instance already exists: %s' % instance_id
        )

    env = murano.environments.create({'name': instance_id})
    session_id = murano.sessions.configure(env.id).id
    env = murano.environments.get(env.id, session_id)

    object_model = get_lbaas_object_model(instance_id, KEY_NAME, IMAGE_NAME)

    murano.services.post(
        env.id,
        session_id=session_id,
        data=object_model,
        path='/'
    )

    murano.sessions.deploy(env.id, session_id)

    bottle.response.status = 202

    return {"dashboard_url": AUTH_URL}


@bottle.route('/v2/service_instances/<instance_id>/last_operation', method='GET')
@bottle.auth_basic(authenticate)
def last_operation(instance_id):
    instance_id = normalize_instance_id(instance_id)

    murano = murano_client()
    env = get_env_by_name(murano, instance_id)

    # First, try to find the appropriate service instance.
    # if not (instance_id in SERVICE_INSTANCES and env):
    #     bottle.abort(
    #         410,
    #         'The requested service instance not found: %s;'
    #         ' env: %s' % (instance_id, env)
    #     )

    last_deployment = murano.deployments.list(env.id)[0]

    reports = murano.deployments.reports(env.id, last_deployment.id)

    state_map_to_cf = {
        'running': 'in progress',
        'success': 'succeeded',
    }

    status = state_map_to_cf.get(last_deployment.state, 'failed')
    description = reports[-1].text if reports else "Not started yet."

    print("Status of %s: %s - %s" % (instance_id, status, description))

    return {
        "state": status,
        "description": description
    }


@bottle.route('/v2/service_instances/<instance_id>', method='DELETE')
@bottle.auth_basic(authenticate)
def deprovision(instance_id):
    """Deprovision an existing instance of this service.

    DELETE /v2/service_instances/<instance_id>:
        <instance_id> is the Cloud Controller provided
          value used to provision the instance

    return:
        As of API 2.7, an empty JSON document
        is expected
    """
    instance_id = normalize_instance_id(instance_id)
    murano = murano_client()

    env = get_env_by_name(murano, instance_id)

    # Check for case of no existing service.
    if not env:
        bottle.abort(
            410,
            'Given instance_id not found as environment name '
            'in murano: %s' % instance_id
        )

    # Deprovision service.
    murano.environments.delete(env.id)

    # Send response.
    bottle.response.status = 200

    return {}


@bottle.route(
    '/v2/service_instances/<instance_id>/service_bindings/<binding_id>',
    method='PUT'
)
@bottle.auth_basic(authenticate)
def bind(instance_id, binding_id):
    """Bind an existing instance with the for the given org and space.

    PUT /v2/service_instances/<instance_id>/service_bindings/<binding_id>:
        <instance_id> is the Cloud Controller provided
          value used to provision the instance
        <binding_id> is provided by the Cloud Controller
          and will be used for future unbind requests

    BODY:
        {
          "plan_id":           "<plan-guid>",
          "service_id":        "<service-guid>",
          "app_guid":          "<app-guid>"
        }

    return:
        JSON document with credentails and access details
        for the service based on this binding
        http://docs.cloudfoundry.org/services/binding-credentials.html
    """
    instance_id = normalize_instance_id(instance_id)

    if bottle.request.content_type != 'application/json':
        bottle.abort(
            415,
            'Unsupported Content-Type: expecting application/json'
        )
    # Get the JSON document in the body.
    binding_details = bottle.request.json

    service_id = binding_details['service_id']

    # Check that service is valid for current service broker.
    assert any(service_id == s['id'] for s in SERVICES)

    murano = murano_client()
    env = get_env_by_name(murano, instance_id)

    # Find the corresponding component for current service.
    components = murano.services.list(env.id)

    component = None
    for c in components:
        if c.to_dict()['?']['type'] == service_id:
            component = c

    if not component:
        bottle.abort(
            404,
            'The requested component type not found in murano env '
            '"%s": %s' % (instance_id, service_id)
        )

    ip = component.instance['floatingIpAddress']
    # Return created status code.
    bottle.response.status = 201

    return {
        "credentials": {
            "uri": "http://%s:8993/v1" % ip
        }
    }


@bottle.route(
    '/v2/service_instances/<instance_id>/service_bindings/<binding_id>',
    method='DELETE'
)
@bottle.auth_basic(authenticate)
def unbind(instance_id, binding_id):
    """Unbind an existing instance associated with the binding_id provided.

    DELETE /v2/service_instances/<instance_id>/service_bindings/<binding_id>:
        <instance_id> is the Cloud Controller provided
          value used to provision the instance
        <binding_id> is the Cloud Controller provided
          value used to bind the instance

    return:
        As of API 2.7, an empty JSON document
        is expected
    """
    instance_id = normalize_instance_id(instance_id)

    murano = murano_client()
    env = get_env_by_name(murano, instance_id)

    # Check for case of no existing service.
    if not env:
        bottle.abort(
            410,
            'The requested service instance does not exist: %s' % instance_id
        )

    # Send response.
    bottle.response.status = 200

    return {}


def main():
    port = int(os.getenv(PORT_VAR_NAME, '8080'))
    bottle.run(host='0.0.0.0', port=port, debug=True, reloader=False)

if __name__ == '__main__':
    main()

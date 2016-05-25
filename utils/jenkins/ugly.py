#!/usr/bin/env python

# Ugly script, for quick deployment. copy-paste from
# https://github.com/vryzhenkin/pegasus

from muranoclient import client as muranoclient
import os
import logging
import random
import yaml
import json
import uuid
import time
import sys
from keystoneclient.v2_0 import client as keystoneclient

formatter = logging.Formatter('%(asctime)s - %(name)s - '
                              '%(levelname)s - %(message)s')

username = os.environ.get('OS_USERNAME')
password = os.environ.get('OS_PASSWORD')
tenant_name = os.environ.get('OS_TENANT_NAME')
uri = os.environ.get('OS_AUTH_URL')
murano_endpoint = os.environ.get('MURANO_URL')

os_cleanup = os.environ.get('OS_CLEANUP', True)
murano_env_name = os.environ.get('ENV_NAME_PREFIX', 'test_run_')
flavor = os.environ.get('OS_FLAVOR', 'm1.medium')
image = os.environ.get('OS_IMAGE', 'Ubuntu_14.04_x64_murano-agent')
keyname = os.environ.get('OS_KEYNAME', 'test_key')
availability_zone = os.environ.get('OS_ZONE', 'nova')
m_pass = 'P@ssw0rd'
ARTIFACTS_DIR = os.environ.get('ARTIFACTS_DIR', 'logs')
deploy_timeout = 1800


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
if not os.path.exists(ARTIFACTS_DIR):
    os.makedirs(ARTIFACTS_DIR)
fh = logging.FileHandler(os.path.join(ARTIFACTS_DIR, 'runner.log'))
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
LOG.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
LOG.addHandler(ch)
history_log = []



def get_auth():
    keystone = keystoneclient.Client(username=username,
                                     password=password,
                                     tenant_name=tenant_name,
                                     auth_url=uri)
    return keystone


def rand_name(name=murano_env_name):
    return name + str(random.randint(1, 0x7fffffff))


def create_env():
    name = rand_name(murano_env_name)
    environment = murano.environments.create({'name': name})
    LOG.debug('Created Environment:\n {0}'.format(environment))
    return environment


def add_service( environment, data, session):
    """
    This function adding a specific service to environment
    Returns a specific class <Service>
    :param environment:
    :param data:
    :param session:
    :return:
    """

    LOG.debug('Added service:\n {0}'.format(data))
    return murano.services.post(environment.id,
                                path='/', data=data,
                                session_id=session.id)


def create_service(environment, session, json_data, to_json=True):
    """
    This function adding a specific service to environment
    Returns a JSON object with a service
    :param environment:
    :param session:
    :param json_data:
    :return:
    """
    service = add_service(environment, json_data, session)
    if to_json:
        service = service.to_dict()
        service = json.dumps(service)
        LOG.debug('Create Service json: {0}'.format(yaml.load(service)))
        return yaml.load(service)
    else:
        LOG.debug('Create Service: {0}'.format(service))
        return service


def fail(msg=None):
    """Fail immediately, with the given message."""
    raise Exception(msg)


def get_last_deployment(environment):
    deployments = murano.deployments.list(environment.id)
    return deployments[0]


def get_deployment_report(environment, deployment):
    history = ''
    report = murano.deployments.reports(environment.id, deployment.id)
    for status in report:
        history += '\t{0} - {1}\n'.format(status.created, status.text)
    return history


def _log_report(environment):
    deployment = get_last_deployment(environment)
    details = deployment.result['result']['details']
    LOG.error('Exception found:\n {0}'.format(details))
    report = get_deployment_report(environment, deployment)
    LOG.debug('Report:\n {0}\n'.format(report))


def _log_quick(environment):
    deployment = get_last_deployment(environment)
    history = get_deployment_report(environment, deployment)
    if len(history_log) == 0 or history_log[0] != history:
        history_log.insert(0, history)
        if len(history_log) > 30:
            history_log.pop()
        LOG.debug("Report: {}".format(history))
        return history


def wait_for_environment_deploy(environment):
    start_time = time.time()
    status = environment.manager.get(environment.id).status
    while status != 'ready':
        status = environment.manager.get(environment.id).status
        LOG.debug('Deployment status:{}...nothing new..'.format(status))
        _log_quick(environment)
        if time.time() - start_time > deploy_timeout:
            time.sleep(60)
            _log_report(environment)
            fail(
                'Environment deployment is not finished in {}seconds'.format(
                    deploy_timeout))
        elif status == 'deploy failure':
            _log_report(environment)
            time.sleep(60)
            fail('Environment has incorrect status {0}'.format(status))
        time.sleep(30)
    LOG.debug('Environment {0} is ready'.format(environment.name))
    return environment.manager.get(environment.id)


def deploy_environment(environment, session):
    murano.sessions.deploy(environment.id, session.id)
    return wait_for_environment_deploy(environment)

if __name__ == '__main__':

    if os_cleanup and tenant_name.lower() == 'admin':
        LOG.error(
            "Never use this ugly test with 'admin' tenant! it can "
            "destroy to much!")
        sys.exit(1)

    keystone = get_auth()
    murano = muranoclient.Client('1', endpoint=murano_endpoint,
                                 token=keystone.auth_token,
                                 )
    environment = create_env()
    session = murano.sessions.configure(environment.id)

    post_body = {
        '?': {'_{id}'.format(id=uuid.uuid4().hex): {'name': 'CI/CD'},
              'id': str(uuid.uuid4()),
              'type': 'io.murano.opaas.CiCdEnvironment'},
        'assignFloatingIp': False,
        'availabilityZone': availability_zone,
        'flavor': flavor,
        'image': image,
        'instance_name': rand_name(),
        'keyname': keyname,
        'ldapEmail': 'email@example.com',
        'ldapPass': m_pass,
        'ldapRootEmail': 'root@example.com',
        'ldapRootPass': m_pass,
        'ldapRootUser': 'root',
        'ldapUser': 'user',
        'name': 'CI/CD'
    }

    try:
        create_service(environment, session, post_body)
        LOG.debug("Attempt to deploy env..")
        deploy_environment(environment, session)
    except Exception as exc:
            LOG.debug('Deployment error', exc)
            raise
    finally:
        deployment = get_last_deployment(environment)
        if os_cleanup:
            LOG.debug('Removing all stuff')
            murano.environments.delete(environment.id)

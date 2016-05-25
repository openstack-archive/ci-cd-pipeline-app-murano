#!/usr/bin/env python

# Ugly script, for quick deployment. copy-paste from
# https://github.com/vryzhenkin/pegasus

from muranoclient import client as muranocl
import os
import logging
import urlparse
import yaml
import json
import uuid
import time
import sys
import socket
import pprint
import requests
from keystoneclient.v2_0 import client as keystoneclient
import muranoclient.common.exceptions as murano_excp

username = os.environ.get('OS_USERNAME')
password = os.environ.get('OS_PASSWORD')
tenant_name = os.environ.get('OS_TENANT_NAME', False)
uri = os.environ.get('OS_AUTH_URL')
murano_endpoint = os.environ.get('OS_MURANO_URL')
heat_endpoint = os.environ.get('OS_HEAT_URL')

os_cleanup = os.environ.get('OS_CLEANUP', False)
murano_env_name = os.environ.get('ENV_NAME_PREFIX', 'murano_ci_test_')
flavor = os.environ.get('OS_FLAVOR', 'm1.medium')
image = os.environ.get('OS_IMAGE', 'Ubuntu_14.04_x64_murano-agent')
keyname = os.environ.get('OS_KEYNAME', 'test_key')
availability_zone = os.environ.get('OS_ZONE', 'nova')
m_pass = 'P@ssw0rd'
ARTIFACTS_DIR = os.environ.get('ARTIFACTS_DIR', 'logs')
BUILD_TAG = os.environ.get('BUILD_TAG', None)
deploy_timeout = (60 * 60) * 2

formatter = logging.Formatter('%(asctime)s - %(name)s - '
                              '%(levelname)s - %(message)s')
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
pprinter = pprint.PrettyPrinter(indent=1, width=80, depth=None)
history_log = 0

murano_client = None

# service name , from murano-app map, and port, which sohuld be checked
check_map = {'jenkins':
                 {'ports': [8080, 22], 'url': 'api', 'url_port': 8080},
             'gerrit':
                 {'ports': [8081, 22], 'url': None},
             'ldap':
                 {'ports': [8081, 22], 'url': None},
             }

# check_map = {'jenkins': {'ports': [8080, 22], 'url': "api"}       }


def get_murano_client():
    """
    Hook for keystone
    :return:
    """
    global murano_client
    if murano_client is None:
        keystone = get_auth()
        murano_client = muranocl.Client('1', endpoint=murano_endpoint,
                                        token=keystone.auth_token)
        return murano_client
    try:
        keystoneclient.Client(token=murano_client.http_client.auth_token,
                              auth_url=uri)
    except Exception as e:
        keystone = get_auth()
        murano_client = muranocl.Client('1', endpoint=murano_endpoint,
                                        token=keystone.auth_token,
                                        )
    return murano_client


def get_auth():
    keystone = keystoneclient.Client(username=username,
                                     password=password,
                                     tenant_name=tenant_name,
                                     auth_url=uri)
    return keystone


def rand_name(name=murano_env_name):
    return name + str(time.strftime("%Y_%m_%d_%H_%M_%S"))


def create_env():
    if BUILD_TAG is None:
        name = rand_name(murano_env_name)
    else:
        name = murano_env_name + str(BUILD_TAG)
    environment = get_murano_client().environments.create({'name': name})
    LOG.debug('Created Environment:\n{0}'.format(pprinter.pformat(environment)))
    return environment


def add_service(environment, data, session):
    """
    This function adding a specific service to environment
    Returns a specific class <Service>
    :param environment:
    :param data:
    :param session:
    :return:
    """

    LOG.debug('Added service:\n {0}'.format(data))
    return get_murano_client().services.post(environment.id,
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
        LOG.debug('Create Service json:{0}'.format(pprinter.pformat(service)))
        return yaml.load(service)
    else:
        LOG.debug('Create Service: {0}'.format(service))
        return service


def fail(msg=None):
    """Fail immediately, with the given message."""
    raise Exception(msg)


def get_last_deployment(environment):
    deployments = get_murano_client().deployments.list(environment.id)
    return deployments[0]


def get_deployment_report(environment, deployment, as_list=False):
    report = get_murano_client().deployments.reports(environment.id, deployment.id)
    if as_list:
        history = []
        for status in report:
            history.append('{0} - {1}'.format(status.created, status.text))
    else:
        history = ''
        for status in report:
            history += '\t{0} - {1}\n'.format(status.created, status.text)
    return history


def _log_report(environment):
    deployment = get_last_deployment(environment)
    try:
        details = deployment.result['result']['details']
    except KeyError:
        LOG.error('Deployment has no result details!')
        pass
    LOG.error('Exception found:\n {0}'.format(details))
    report = get_deployment_report(environment, deployment)
    LOG.debug('Report:\n {0}\n'.format(report))


def _log_quick(environment):
    global history_log
    deployment = get_last_deployment(environment)
    history = get_deployment_report(environment, deployment, as_list=True)
    if history_log != len(history) or history_log == 0:
        tmp = len(history)
        history = history[history_log:]
        LOG.debug("Last report:\n{}".format(pprinter.pformat(history)))
        history_log = tmp
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
    get_murano_client().sessions.deploy(environment.id, session.id)
    return wait_for_environment_deploy(environment)


def get_ip_by_instance_name(environment, inst_name):
    """
    :return:
    """
    ip = None
    e = environment
    try:
        if inst_name in e.services[0]:
            ip = e.services[0][inst_name]['instance']['floatingIpAddress']
    except (KeyError, TypeError):
        pass
    try:
        socket.inet_aton(ip)
        LOG.debug("Found floating:{} for instance: {}".format(ip, inst_name))
        return ip
    except Exception:
        fail('Instance "{}" does not have floating IP'.format(inst_name))


def check_port_access(ip, port):
    # FIXME
    result = 1
    start_time = time.time()
    while time.time() - start_time < 60:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((str(ip), port))
        sock.close()
        if result == 0:
            LOG.debug('%s port is opened on instance' % port)
            break
        else:
            fail('%s port is not opened on instance' % port)
        time.sleep(5)
    if result != 0:
            fail('%s port is not opened on instance' % port)


def check_path(env, path, inst_name=None, port=80):
    environment = env.manager.get(env.id)
    if inst_name:
        ip = get_ip_by_instance_name(environment, inst_name)
    else:
        ip = environment.services[0]['instance']['floatingIpAddress']
    proto = 'http'
    if port in (443, 8443):
        proto = 'https'
    resp = requests.get('{}://{}:{}/{}'.format(proto, ip, port, path))
    if resp.status_code == 200:
        LOG.debug(
            "Service path fine: {}://{}:{}/{}".format(proto, ip, port, path))
        pass
    else:
        fail("Service path failed: {}://{}:{}/{}".format(proto, ip, port, path))


def deployment_success_check(environment, inst_name='jenkins', ports=[]):
    """
    :param environment:
    :param ports:
    """
    deployment = get_murano_client().deployments.list(environment.id)[-1]
    LOG.debug('Deployment status is {0}'.format(deployment.state))
    if str(deployment.state) != 'success':
        fail('Wrong deploymnet state = {}'.format(deployment.state))
    ip = get_ip_by_instance_name(environment, inst_name)
    for port in ports:
            LOG.debug("Looking into: {} {}:{} ".format(inst_name, ip, port))
            check_port_access(ip, port)


def cleaup_up_tenant():
    LOG.warning('Removing everything from tenant{}'.format(tenant_name))
    murano = get_murano_client()
    for env in murano.environments.list():
        try:
            murano.environments.delete(env)
        except Exception as e:
            LOG.warning("Unable delete env:{}".format(env))
            LOG.exception(e)
            pass
    from heatclient.client import Client as HeatCl

    tenant_id = get_auth().get_project_id(tenant_name)
    heat_url = urlparse.urljoin(heat_endpoint, tenant_id)
    heat = HeatCl('1', endpoint=heat_url, token=get_auth().auth_token)
    for stack in heat.stacks.list():
        try:
            heat.stacks.delete(stack.id)
        except Exception as e:
            LOG.warning("Unable delete stack:{}".format(stack))
            LOG.exception(e)
            pass
    return

if __name__ == '__main__':

    if os_cleanup and tenant_name.lower() == 'admin':
        LOG.error(
            "Never use this ugly test with 'admin' tenant! it can "
            "destroy to much!")
        sys.exit(1)

    # # instant test
    #
    # murano = get_murano_client()
    # environment = murano.environments.get('1b5eb6989a244a24a30dcd33d270c038')
    # service = 'jenkins'
    # ip = environment.services[0][service]['instance']['floatingIpAddress']

    environment = create_env()
    session = get_murano_client().sessions.configure(environment.id)

    post_body = {
        '?': {'_{id}'.format(id=uuid.uuid4().hex): {'name': 'CI/CD'},
              'id': str(uuid.uuid4()),
              'type': 'org.openstack.ci_cd_pipeline_murano_app.CiCdEnvironment'},
        'assignFloatingIp': True,
        'availabilityZone': availability_zone,
        'flavor': flavor,
        'image': image,
        'instance_name': environment.name,
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
        for service in check_map:
            deployment_success_check(environment, service, check_map[service]['ports'])
            if check_map[service]['url']:
                check_path(environment, check_map[service]['url'],
                           inst_name=service, port=check_map[service]['url_port'])

    except Exception as exc:
            LOG.debug('Deployment error', exc)
            raise
    finally:
        deployment = get_last_deployment(environment)
        if os_cleanup:
            LOG.warning('Removing all stuff')
            cleaup_up_tenant()


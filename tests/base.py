# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os
import socket
import shutil
import time
import uuid
from xml.etree import ElementTree as et

import jenkins
import paramiko
import requests
import testtools
import yaml
import muranoclient.common.exceptions as exceptions

import clients

ARTIFACTS_DIR = os.environ.get('ARTIFACTS_DIR', 'logs')

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
if not os.path.exists(ARTIFACTS_DIR):
    os.makedirs(ARTIFACTS_DIR)
fh = logging.FileHandler(os.path.join(ARTIFACTS_DIR, 'runner.log'))
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
fh.setFormatter(formatter)
LOG.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
LOG.addHandler(ch)

# Sometimes need to pass some boolean from bash env. Since each bash
# variable is string, we need such simply hack
_boolean_states = {
    '1': True, 'yes': True, 'true': True, 'on': True,
    '0': False, 'no': False, 'false': False, 'off': False
}

def str2bool(name, default):
    value = os.environ.get(name, '')
    return _boolean_states.get(value.lower(), default)

TIMEOUT_DELAY = 30


class MuranoTestsBase(testtools.TestCase, clients.ClientsBase):

    def setUp(self):
        super(MuranoTestsBase, self).setUp()
        self.os_username = os.environ.get('OS_USERNAME')
        self.os_password = os.environ.get('OS_PASSWORD')
        self.os_tenant_name = os.environ.get('OS_TENANT_NAME')
        self.os_auth_uri = os.environ.get('OS_AUTH_URL')

        self.keystone = self.initialize_keystone_client()
        self.heat = self.initialize_heat_client(self.keystone)
        self.murano = self.initialize_murano_client(self.keystone)
        self.nova = self.initialize_nova_client(self.keystone)

        # Since its really useful to debug deployment after it fail lets
        # add such possibility
        self.os_cleanup_before = str2bool('OS_CLEANUP_BEFORE', True)
        self.os_cleanup_after = str2bool('OS_CLEANUP_AFTER', False)

        # Data for Nodepool app
        self.os_np_username = os.environ.get('OS_NP_USERNAME', self.os_username)
        self.os_np_password = os.environ.get('OS_NP_PASSWORD', self.os_password)
        self.os_np_tenant_name = os.environ.get(
            'OS_NP_TENANT_NAME',
            self.os_tenant_name
        )
        self.os_np_auth_uri = os.environ.get('OS_NP_AUTH_URL', self.os_auth_uri)
        self.os_np_cleanup_before = str2bool('OS_NP_CLEANUP_BEFORE', False)

        if self.os_cleanup_before:
            self.cleanup_up_tenant()

        if self.os_np_cleanup_before:
            self.cleanup_up_np_tenant()

        # Counter for murano deployment logger
        self.latest_report = 0

        # Application instance parameters
        self.flavor = os.environ.get('OS_FLAVOR', 'm1.medium')
        self.image = os.environ.get('OS_IMAGE')
        self.docker_image = os.environ.get('OS_DOCKER_IMAGE')
        self.files = []
        self.keyname, self.pr_key, self.pub_key = self._create_keypair()
        self.availability_zone = os.environ.get('OS_ZONE', 'nova')

        self.envs = []

        LOG.info('Running test: {0}'.format(self._testMethodName))

    def tearDown(self):
        for env in self.envs:
            self._collect_murano_agent_logs(env)
        if self.os_cleanup_after:
            for env in self.envs:
                try:
                    self.delete_env(env)
                except Exception:
                    self.delete_stack(env)
            self.nova.keypairs.delete(self.keyname)
            for file in self.files:
                if os.path.isfile(file):
                    os.remove(file)
                elif os.path.isdir(file):
                    shutil.rmtree(file)

        super(MuranoTestsBase, self).tearDown()

    @staticmethod
    def rand_name(name='murano_ci_test_'):
        return name + str(time.strftime("%Y_%m_%d_%H_%M_%S"))

    @staticmethod
    def generate_id():
        return uuid.uuid4()

    def create_file(self, name, context):
        with open(name, 'w') as f:
            f.write(context)
        path_to_file = os.path.join(os.getcwd(), name)
        self.files.append(path_to_file)
        return path_to_file

    def cleanup_up_tenant(self):
        LOG.debug('Removing EVERYTHING in tenant: {0}'.format(
            self.keystone.tenant_name))
        for env in self.murano.environments.list():
            self.delete_env(env)
            self.delete_stack(env)
        for key in self.nova.keypairs.list():
            if key.name.startswith("murano_ci_keypair"):
                self.nova.keypairs.delete(key)
        return

    def cleanup_up_np_tenant(self):
        # TODO
        LOG.warning('NodePool cleanup not implemented yet!')
        return

    def _create_keypair(self):
        kp_name = self.rand_name('murano_ci_keypair_')
        keypair = self.nova.keypairs.create(kp_name)
        pr_key_file = self.create_file(
            'id_{}'.format(kp_name), keypair.private_key
        )
        # Note: by default, permissions of created file with
        # private keypair is too open
        os.chmod(pr_key_file, 0600)

        pub_key_file = self.create_file(
            'id_{}.pub'.format(kp_name), keypair.public_key
        )
        return kp_name, pr_key_file, pub_key_file

    def _get_stack(self, environment_id):
        for stack in self.heat.stacks.list():
            if environment_id in stack.description:
                return stack

    def delete_stack(self, environment):
        stack = self._get_stack(environment.id)
        if not stack:
            return
        else:
            try:
                self.heat.stacks.delete(stack.id)
            except Exception as e:
                LOG.warning("Unable delete stack:{}".format(stack))
                LOG.exception(e)
                pass

    def create_env(self):
        name = self.rand_name()
        environment = self.murano.environments.create({'name': name})
        self.envs.append(environment)
        if self.os_cleanup_after:
            self.addCleanup(self.delete_env, environment)
        LOG.debug('Created Environment:\n {0}'.format(environment))

        return environment

    def delete_env(self, environment, timeout=360):
        try:
            self.murano.environments.delete(environment.id)
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    self.murano.environments.get(environment.id)
                    time.sleep(1)
                except exceptions.HTTPNotFound:
                    return
            raise exceptions.HTTPOverLimit(
                'Environment "{0}" was not deleted in {1} seconds'.format(
                    environment.id, timeout)
            )
        except (exceptions.HTTPForbidden, exceptions.HTTPOverLimit,
                exceptions.HTTPNotFound):
            try:
                self.murano.environments.delete(environment.id, abandon=True)
                LOG.warning(
                    'Environment "{0}" from test {1} abandoned'.format(
                        environment.id, self._testMethodName))
            except exceptions.HTTPNotFound:
                return

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.murano.environments.get(environment.id)
                time.sleep(1)
            except exceptions.HTTPNotFound:
                return
        raise Exception(
            'Environment "{0}" was not deleted in {1} seconds'.format(
                environment.id, timeout)
        )

    def get_env(self, environment):
        return self.murano.environments.get(environment.id)

    def deploy_env(self, environment, session):
        self.murano.sessions.deploy(environment.id, session.id)
        return self.wait_for_environment_deploy(environment)

    def get_deployment_report(self, environment, deployment):
        history = ''
        report = self.murano.deployments.reports(environment.id, deployment.id)
        for status in report:
            history += '\t{0} - {1}\n'.format(status.created, status.text)
        return history

    def _log_report(self, environment):
        deployment = self.murano.deployments.list(environment.id)[0]
        details = deployment.result['result']['details']
        LOG.error('Exception found:\n {0}'.format(details))
        report = self.get_deployment_report(environment, deployment)
        LOG.debug('Report:\n {0}\n'.format(report))

    def _log_latest(self, environment):
        deployment = self.murano.deployments.list(environment.id)[0]
        history = self.get_deployment_report(environment, deployment)
        if self.latest_report != len(history) or self.latest_report == 0:
            tmp = len(history)
            history = history[self.latest_report:]
            LOG.debug("Last report from murano engine:\n{}".format((history)))
            self.latest_report = tmp
            return history

    def _collect_murano_agent_logs(self, environment):
        fips = self.get_services_fips(environment)
        logs_dir = "{0}/{1}".format(ARTIFACTS_DIR, environment.name)
        os.makedirs(logs_dir)
        for service, fip in fips.iteritems():
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(fip, username='ubuntu', key_filename=self.pr_key)
                ftp = ssh.open_sftp()
                ftp.get(
                    '/var/log/murano-agent.log',
                    os.path.join(logs_dir, '{0}-agent.log'.format(service))
                )
                ftp.close()
            except Exception as e:
                LOG.warning(
                    "Couldn't collect murano-agent "
                    "logs of {0} (IP: {1}): {2}".format(service, fip, e)
                )

    def wait_for_environment_deploy(self, env, timeout=7200):
        start_time = time.time()
        status = self.get_env(env).manager.get(env.id).status

        while status != 'ready':
            status = self.get_env(env).manager.get(env.id).status
            LOG.debug('Deployment status:{}...nothing new..'.format(status))
            self._log_latest(env)

            if time.time() - start_time > timeout:
                time.sleep(60)
                self.fail(
                    'Environment deployment wasn\'t'
                    'finished in {} seconds'.format(self.timeout)
                )
            elif status == 'deploy failure':
                self._log_report(env)
                self.fail(
                    'Environment has incorrect status "{0}"'.format(status)
                )

            time.sleep(TIMEOUT_DELAY)
        LOG.debug('Environment "{0}" is ready'.format(self.get_env(env).name))
        return self.get_env(env).manager.get(env.id)

    def create_session(self, environment):
        return self.murano.sessions.configure(environment.id)

    def create_service(self, environment, session, json_data, to_json=True):
        LOG.debug('Adding service:\n {0}'.format(json_data))
        service = self.murano.services.post(
            environment.id,
            path='/',
            data=json_data,
            session_id=session.id
        )
        if to_json:
            service = service.to_dict()
            service = json.dumps(service)
            LOG.debug('Create Service json: {0}'.format(yaml.load(service)))
            return yaml.load(service)
        else:
            LOG.debug('Create Service: {0}'.format(service))
            return service

    @staticmethod
    def guess_fip(env_obj_model):

        result = {}

        def _finditem(obj, result):
            if 'floatingIpAddress' in obj.get('instance', []):
                result[obj['?']['package']] = obj['instance'][
                    'floatingIpAddress']
            for k, v in obj.items():
                if isinstance(v, dict):
                    _finditem(v, result)
        _finditem(env_obj_model, result)

        return result

    def get_services_fips(self, environment):
        fips = {}
        for service in environment.services:
            fips.update(self.guess_fip(service))

        return fips

    def check_ports_open(self, ip, ports):
        for port in ports:
            result = 1
            start_time = time.time()
            while time.time() - start_time < 60:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((str(ip), port))
                sock.close()

                if result == 0:
                    LOG.debug('{} port is opened on instance'.format(port))
                    break
                time.sleep(5)

            if result != 0:
                self.fail('{} port is not opened on instance'.format(port))

    def check_url_access(self, ip, path, port):
        proto = 'http' if port not in (443, 8443) else 'https'
        url = '{proto}://{ip}:{port}/{path}'.format(
            proto=proto,
            ip=ip,
            port=port,
            path=path
        )

        resp = requests.get(url, timeout=60)

        return resp.status_code

    def deployment_success_check(self, environment, services_map):
        deployment = self.murano.deployments.list(environment.id)[-1]

        self.assertEqual(
            'success', deployment.state,
            'Deployment status is "{0}"'.format(deployment.state)
        )

        fips = self.get_services_fips(environment)

        for service in services_map:
            LOG.debug(
                'Checking ports availability on "{}" app instance'.format(
                    service)
                )
            self.check_ports_open(
                fips[service], services_map[service]['ports']
            )
            if services_map[service]['url']:
                LOG.debug(
                    'Checking {0} app url "{1}" availability'.format(
                        service, services_map[service]['url']
                    )
                )
                self.check_url_access(
                    fips[service],
                    services_map[service]['url'],
                    services_map[service]['url_port']
                )

    @staticmethod
    def add_to_file(path_to_file, context):
        with open(path_to_file, "a") as f:
            f.write(context)

    @staticmethod
    def read_from_file(path_to_file):
        with open(path_to_file, "r") as f:
            return f.read()

    def execute_cmd_on_remote_host(self, host, cmd, key_file, user='ubuntu'):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=user, key_filename=key_file)
        stdin, stdout, stderr = client.exec_command(cmd)
        data = stdout.read() + stderr.read()
        client.close()

        return data

    def export_ssh_options(self):
        context = (
            '#!/bin/bash\n'
            'ssh -o StrictHostKeyChecking=no -i {0} "$@"'.format(self.pr_key)
        )
        gitwrap = self.create_file('/tmp/gitwrap.sh', context)
        os.chmod(gitwrap, 0744)
        os.environ['GIT_SSH'] = gitwrap

    def clone_repo(self, gerrit_host, gerrit_user, repo, dest_dir):
        repo_dest_path = os.path.join(dest_dir, repo.split('/')[-1])
        self.files.append(repo_dest_path)

        if os.path.isdir(repo_dest_path):
            shutil.rmtree(repo_dest_path)

        os.system('git clone ssh://{user}@{host}:29418/{repo} {dest}'.format(
            user=gerrit_user,
            host=gerrit_host,
            repo=repo,
            dest=repo_dest_path
        ))
        return repo_dest_path

    def switch_to_branch(self, repo, branch):
        os.system('cd {repo}; git checkout {branch}'.format(
            repo=repo,
            branch=branch)
        )

    def add_committer_info(self, configfile, user, email):
        author_data = """
        [user]
            name={0}
            email={1}
        """.format(user, email)
        self.add_to_file(configfile, author_data)

    def make_commit(self, repo, branch, key, msg):
        # NOTE need to think how to use GIT_SSH
        os.system(
            'cd {repo};'
            'git add . ; git commit -am "{msg}"; '
            'ssh-agent bash -c "ssh-add {key}; '
            'git-review -r origin {branch}"'.format(
                repo=repo,
                msg=msg,
                key=key,
                branch=branch
            )
        )

    @staticmethod
    def _gerrit_cmd(gerrit_host, cmd):
        return (
            'sudo su -c "ssh -p 29418 -i '
            '/home/gerrit2/review_site/etc/ssh_project_rsa_key '
            'project-creator@{host} {cmd}" '
            'gerrit2'.format(host=gerrit_host, cmd=cmd)
        )

    def get_last_open_patch(self, gerrit_ip, gerrit_host, project, commit_msg):
        cmd = (
            'gerrit query --format JSON status:open '
            'project:{project} limit:1'.format(project=project)
        )
        cmd = self._gerrit_cmd(gerrit_host, cmd)

        # Note: "gerrit query" returns results describing changes that
        # match the input query.
        # Here is an example of results for above query:
        # {"project":"open-paas/project-config" ... "number":"1",
        # {"type":"stats","rowCount":1,"runTimeMilliseconds":219, ...}
        # Output has to be cut using "head -1", because json.loads can't
        # decode multiple jsons

        patch = self.execute_cmd_on_remote_host(
            host=gerrit_ip,
            key_file=self.pr_key,
            cmd='{} | head -1'.format(cmd)
        )
        patch = json.loads(patch)
        self.assertIn(commit_msg, patch['commitMessage'])

        return patch['number']

    def merge_commit(self, gerrit_ip, gerrit_host, project, commit_msg):
        patch_num = self.get_last_open_patch(
            gerrit_ip=gerrit_ip,
            gerrit_host=gerrit_host,
            project=project,
            commit_msg=commit_msg
        )

        cmd = (
            'gerrit review --project {project} --verified +2 '
            '--code-review +2 --label Workflow=+1 '
            '--submit {id},1'.format(project=project, id=patch_num)
        )
        cmd = self._gerrit_cmd(gerrit_host, cmd)

        self.execute_cmd_on_remote_host(
            host=gerrit_ip,
            user='ubuntu',
            key_file=self.pr_key,
            cmd=cmd
        )

    def set_tomcat_ip(self, pom_file, ip):
        et.register_namespace('', 'http://maven.apache.org/POM/4.0.0')
        tree = et.parse(pom_file)
        new_url = 'http://{ip}:8080/manager/text'.format(ip=ip)
        ns = {'ns': 'http://maven.apache.org/POM/4.0.0'}
        for plugin in tree.findall('ns:build/ns:plugins/', ns):
            plugin_id = plugin.find('ns:artifactId', ns).text
            if plugin_id == 'tomcat7-maven-plugin':
                plugin.find('ns:configuration/ns:url', ns).text = new_url

        tree.write(pom_file)

    def get_gerrit_projects(self, gerrit_ip, gerrit_host):
        cmd = self._gerrit_cmd(gerrit_host, 'gerrit ls-projects')
        return self.execute_cmd_on_remote_host(
            host=gerrit_ip,
            user='ubuntu',
            key_file=self.pr_key,
            cmd=cmd
        )

    def wait_for(self, func, expected, debug_msg, fail_msg, timeout, **kwargs):
        def check(exp, cur):
            if isinstance(cur, list) or isinstance(cur, str):
                return exp not in cur
            else:
                return exp != cur

        LOG.debug(debug_msg)
        start_time = time.time()

        current = func(**kwargs)

        while check(expected, current):
            current = func(**kwargs)

            if time.time() - start_time > timeout:
                self.fail("Time is out. {0}".format(fail_msg))
            time.sleep(TIMEOUT_DELAY)
        LOG.debug('Expected result has been achieved.')

    @staticmethod
    def _connect_jenkins_server(ip, user=None, password=None):
        return jenkins.Jenkins(
            'http://{0}:8080'.format(ip),
            username=user,
            password=password
        )

    def get_jenkins_jobs(self, ip):
        server = self._connect_jenkins_server(ip)

        return [job['name'] for job in server.get_all_jobs()]

    def get_last_build_number(self, ip, user, password, job_name, build_type):
        server = self._connect_jenkins_server(ip, user, password)
        # If there are no builds of desired type get_job_info returns None and
        # it is not possible to get number, in this case this function returns
        # None too and it means that there are no builds yet

        build = server.get_job_info(job_name)[build_type]
        if build:
            return build['number']
        else:
            return build
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

import base


class MuranoCiCdFlowTest(base.MuranoTestsBase):

    def test_run_cicd_flow(self):
        ldap_user = 'user'
        ldap_password = 'P@ssw0rd'
        ldap_user_email = 'email@example.com'

        environment = self.create_env()
        session = self.create_session(environment)

        cicd_json = {
            '?': {
                '_{id}'.format(id=self.generate_id().hex): {'name': 'CI/CD'},
                'id': str(self.generate_id()),
                'type':
                    'org.openstack.ci_cd_pipeline_murano_app.CiCdEnvironment'
            },
            'assignFloatingIp': True,
            'availabilityZone': self.availability_zone,
            'flavor': self.flavor,
            'image': self.image,
            'instance_name': environment.name,
            'keyname': self.keyname,
            'ldapEmail': ldap_user_email,
            'ldapPass': 'P@ssw0rd',
            'ldapRootEmail': 'root@example.com',
            'ldapRootPass': ldap_password,
            'ldapRootUser': 'root',
            'ldapUser': ldap_user,
            'userSSH': self.read_from_file(self.pub_key),
            'name': 'CI/CD',
        }

        self.create_service(environment, session, cicd_json)
        self.deploy_env(environment, session)

        session = self.create_session(environment)
        docker_json = {
              'instance': {
                  'name': self.rand_name('Docker'),
                  'assignFloatingIp': True,
                  'keyname': self.keyname,
                  'flavor': 'm1.large',
                  'image': self.docker_image,
                  'availabilityZone': self.availability_zone,
                  '?': {
                      'type': 'io.murano.resources.LinuxMuranoInstance',
                      'id': self.generate_id()
                  },
              },
              'name': 'DockerVM',
              '?': {
                  '_{id}'.format(id=self.generate_id().hex): {
                      'name': 'Docker VM Service'
                  },
                  'type': 'com.mirantis.docker.DockerStandaloneHost',
                  'id': str(self.generate_id())
              }
        }

        docker = self.create_service(environment, session, docker_json)

        tomcat_json = {
            'host': docker,
            'image': 'tutum/tomcat',
            'name': 'Tomcat',
            'port': 8080,
            'password': 'admin',
            'publish': True,
            '?': {
                '_{id}'.format(id=self.generate_id().hex): {
                    'name': 'Docker Tomcat'
                },
                'type': 'com.example.docker.DockerTomcat',
                'id': str(self.generate_id())
            }
        }
        self.create_service(environment, session, tomcat_json)

        self.deploy_env(environment, session)

        environment = self.get_env(environment)

        check_services = {
            'org.openstack.ci_cd_pipeline_murano_app.Jenkins': {
                'ports': [8080, 22],
                'url': 'api/',
                'url_port': 8080
            },
            'org.openstack.ci_cd_pipeline_murano_app.Gerrit': {
                'ports': [8081, 22],
                'url': '#/admin/projects/',
                'url_port': 8081
            },
            'org.openstack.ci_cd_pipeline_murano_app.OpenLDAP': {
                'ports': [389, 22],
                'url': None
            },
            'com.mirantis.docker.DockerStandaloneHost': {
                'ports': [8080, 22],
                'url': None
            }
        }

        self.deployment_success_check(environment, check_services)

        fips = self.get_services_fips(environment)

        # Get Gerrit ip and hostname

        gerrit_ip = fips['org.openstack.ci_cd_pipeline_murano_app.Gerrit']
        gerrit_hostname = self.execute_cmd_on_remote_host(
            host=gerrit_ip,
            cmd='hostname -f',
            key_file=self.pr_key
        )[:-1]

        self.export_ssh_options()

        # Clone "project-config" repository

        project_config_location = self.clone_repo(
            gerrit_host=gerrit_ip,
            gerrit_user=ldap_user,
            repo='open-paas/project-config',
            dest_dir='/tmp'
        )

        # Add new project to gerrit/projects.yaml

        new_project = (
            '- project: demo/petclinic\n'
            '  description: petclinic new project\n'
            '  upstream: https://github.com/sn00p/spring-petclinic\n'
            '  acl-config: /home/gerrit2/acls/open-paas/project-config.config\n'
        )
        self.add_to_file(
            '{0}/gerrit/projects.yaml'.format(project_config_location),
            new_project
        )

        # Add committer info to project-config repo git config

        self.add_committer_info(
            configfile='{0}/.git/config'.format(project_config_location),
            user=ldap_user,
            email=ldap_user_email
        )

        # Make commit to project-config

        self.make_commit(
            repo=project_config_location,
            branch='master',
            key=self.pr_key,
            msg='Add new project to gerrit/projects.yaml'
        )

        # Merge commit

        self.merge_commit(
            gerrit_ip=gerrit_ip,
            gerrit_host=gerrit_hostname,
            project='open-paas/project-config',
            commit_msg='Add new project to gerrit/projects.yaml'
        )

        self.wait_for(
            func=self.get_gerrit_projects,
            expected='demo/petclinic',
            debug_msg='Waiting while "demo/petlinic" project is created',
            fail_msg='Project "demo/petclinic" wasn\'t created',
            timeout=600,
            gerrit_ip=gerrit_ip,
            gerrit_host=gerrit_hostname,
        )

        # Create jenkins job for building petclinic app

        new_job = (
            '- project:\n'
            '    name: petclinic\n'
            '    jobs:\n'
            '      - "{{name}}-java-app-deploy":\n'
            '           git_url: "ssh://jenkins@{0}:29418/demo/petclinic"\n'
            '           project: "demo/petclinic"\n'
            '           branch: "Spring-Security"\n'
            '           goals: tomcat7:deploy\n'.format(gerrit_hostname)
        )
        self.add_to_file(
            '{0}/jenkins/jobs/projects.yaml'.format(project_config_location),
            new_job
        )

        # Make commit to project-config

        self.make_commit(
            repo=project_config_location,
            branch='master',
            key=self.pr_key,
            msg='Add job for petclinic app'
        )

        # Merge commit

        self.merge_commit(
            gerrit_ip=gerrit_ip,
            gerrit_host=gerrit_hostname,
            project='open-paas/project-config',
            commit_msg='Add job for petclinic app'
        )

        # Wait while new "petclinic-java-app-deploy" job is created

        self.wait_for(
            func=self.get_jenkins_jobs,
            expected='petclinic-java-app-deploy',
            debug_msg='Waiting while "petclinic-java-app-deploy" is created',
            fail_msg='Job "petclinic-java-app-deploy" wasn\'t created',
            timeout=600,
            ip=fips['org.openstack.ci_cd_pipeline_murano_app.Jenkins']
        )

        # Clone "demo/petclinic" repository

        petclinic_location = self.clone_repo(
            gerrit_host=gerrit_ip,
            gerrit_user=ldap_user,
            repo='demo/petclinic',
            dest_dir='/tmp'
        )

        # Switch to "Spring-Security" branch

        self.switch_to_branch(
            repo=petclinic_location,
            branch='Spring-Security'
        )

        # Set deployed Tomcat IP to pom.xml

        self.set_tomcat_ip(
            '{}/pom.xml'.format(petclinic_location),
            fips['com.mirantis.docker.DockerStandaloneHost']
        )

        # Add committer info to demo/petclinic repo git config

        self.add_committer_info(
            configfile='{0}/.git/config'.format(petclinic_location),
            user=ldap_user,
            email=ldap_user_email
        )

        self.make_commit(
            repo=petclinic_location,
            branch='Spring-Security',
            key=self.pr_key,
            msg='Update Tomcat IP'
        )

        # Merge commit

        self.merge_commit(
            gerrit_ip=gerrit_ip,
            gerrit_host=gerrit_hostname,
            project='demo/petclinic',
            commit_msg='Update Tomcat IP'
        )

        # Check that 'petclinic-java-app-deploy' (it triggers on-submit) was run

        self.wait_for(
            self.get_last_build_number,
            expected=1,
            debug_msg='Waiting while "petclinic-java-app-deploy" '
                      'job is run and first build is completed',
            fail_msg='Job "petclinic-java-app-deploy" wasn\'t run on-submit',
            timeout=900,
            ip=fips['org.openstack.ci_cd_pipeline_murano_app.Jenkins'],
            user=ldap_user,
            password=ldap_password,
            job_name='petclinic-java-app-deploy',
            build_type='lastCompletedBuild'
        )

        # Check that 'petclinic-java-app-deploy' (it triggers on-submit) was
        # finished and successful

        self.wait_for(
            self.get_last_build_number,
            expected=1,
            debug_msg='Checking that first build of "petclinic-java-app-deploy"'
                      ' job is successfully completed',
            fail_msg='Job "petclinic-java-app-deploy" has failed',
            timeout=60,
            ip=fips['org.openstack.ci_cd_pipeline_murano_app.Jenkins'],
            user=ldap_user,
            password=ldap_password,
            job_name='petclinic-java-app-deploy',
            build_type='lastSuccessfulBuild'
        )

        # Check that Petclinic application was successfully deployed

        self.wait_for(
            func=self.check_url_access,
            expected=200,
            debug_msg='Checking that "petlinic" app is deployed and available',
            fail_msg='Petclinic url isn\'t accessible.',
            timeout=300,
            ip=fips['com.mirantis.docker.DockerStandaloneHost'],
            path='petclinic/',
            port=8080
        )

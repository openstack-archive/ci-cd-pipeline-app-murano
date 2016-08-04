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
                  'flavor': self.flavor,
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

        new_project = """
        - project: demo/petclinic
          description: petclinic new project
          upstream: https://github.com/sn00p/spring-petclinic
          acl-config: /home/gerrit2/acls/open-paas/project-config.config
        """
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
            fail_msg='Project "demo/petclinic" wasn\'t created',
            timeout=600,
            gerrit_ip=gerrit_ip,
            gerrit_host=gerrit_hostname,
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

        # Create jenkins job for building petclinic app

        new_job = """
        - project:
          name: petclinic
          jobs:
          - "{{name}}-java-app":
              git_url: "ssh://jenkins@{0}:29418/demo/petclinic"
              project: "demo/petclinic"
              branch: "Spring-Security"
              goals: tomcat7:deploy
        """.format(gerrit_hostname)
        self.add_to_file(
            '{0}/jenkins/jobs/projects.yaml'.format(project_config_location),
            new_job
        )

        # Making commit to project-config

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

        # Wait while new "petclinic-java-app" job is created

        self.wait_for(
            func=self.get_jenkins_jobs,
            expected='petclinic-java-app',
            fail_msg='Job "petclinic-java-app" wasn\'t created',
            timeout=600,
            ip=fips['org.openstack.ci_cd_pipeline_murano_app.Jenkins']
        )

        # Run petclinic-java-app job

        self.run_job(
            fips['org.openstack.ci_cd_pipeline_murano_app.Jenkins'],
            ldap_user,
            ldap_password,
            'petclinic-java-app'
        )

        # Check that Petclinic application was successfully deployed

        self.wait_for(
            func=self.check_url_access,
            expected=200,
            fail_msg='Url isn\'t accessible.',
            timeout=300,
            ip=fips['com.mirantis.docker.DockerStandaloneHost'],
            path='petclinic/',
            port=8080

        )

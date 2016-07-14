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


class MuranoCiCdTest(base.MuranoTestsBase):

    def test_deploy_cicd(self):
        environment = self.create_env()
        session = self.create_session(environment)

        zuul_helper_id = str(self.generate_id())
        service_json1 = {
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
            'ldapEmail': 'email@example.com',
            'ldapPass': 'P@ssw0rd',
            'ldapRootEmail': 'root@example.com',
            'ldapRootPass': 'P@ssw0rd',
            'ldapRootUser': 'root',
            'ldapUser': 'user',
            'name': 'CI/CD',
            'zuulNodepoolHelper': zuul_helper_idб
            'systemConfigRepo': 'https://review.fuel-infra.org/open-paas/system-config'
        }

        service_json2 = {
            '?': {
                '_{id}'.format(id=self.generate_id().hex): {
                    'name': 'Zuul and Nodepool helper'},
                'id': zuul_helper_id,
                'type':
                    'org.openstack.ci_cd_pipeline_murano_app.ZuulNodepoolHelper'
            },

            'name': 'Zuul and Nodepool Parameters',
            'authUrl': self.os_np_auth_uri,
            'password': self.os_np_password,
            'tenant': self.os_np_tenant_name,
            'username': self.os_np_username
        }

        self.create_service(environment, session, service_json2)
        self.create_service(environment, session, service_json1)
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
        }

        self.deployment_success_check(environment, check_services)
        base.LOG.debug("Run second deployment, w\o any changes..")
        session = self.create_session(environment)
        self.deploy_env(environment, session)
        self.deployment_success_check(environment, check_services)

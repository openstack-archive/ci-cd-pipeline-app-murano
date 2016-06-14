from tests import base


class MuranoCiCdTest(base.MuranoTestsBase):

    def test_deploy_cicd(self):
        environment = self.create_env()
        session = self.create_session(environment)
        service_json = {
            '?': {
                '_{id}'.format(id=self.generate_id().hex): {'name': 'CI/CD'},
                'id': str(self.generate_id()),
                'type':'org.openstack.ci_cd_pipeline_murano_app.CiCdEnvironment'
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
            'name': 'CI/CD'
        }
        self.create_service(environment, session, service_json)
        self.deploy_env(environment, session)

        environment = self.get_env(environment.id)

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


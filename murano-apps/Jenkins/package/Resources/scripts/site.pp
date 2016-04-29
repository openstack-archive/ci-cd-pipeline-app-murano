node default {

  if ! defined(Class['project_config']) {
    class { 'project_config':
      url  => hiera('project_config_repo'),
    }
  }

  class { 'openstack_project::jenkins':
    jenkins_password        => '',
    jenkins_ssh_private_key => '',
    ssl_cert_file           => '/etc/ssl/certs/ssl-cert-snakeoil.pem',
    ssl_key_file            => '/etc/ssl/private/ssl-cert-snakeoil.key',
    ssl_chain_file          => '',
  }
}
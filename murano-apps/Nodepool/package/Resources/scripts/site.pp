node default {
  class { 'openstack_project::server':
    sysadmins                 => hiera('sysadmins', []),
    iptables_public_tcp_ports => [80],
  }

  if ! defined(Class['project_config']) {
    class { 'project_config':
      url  => hiera('project_config_repo'),
    }
  }

  class { 'nodepool':
    mysql_root_password           => hiera('nodepool_mysql_root_password'),
    mysql_password                => hiera('nodepool_mysql_password'),
    nodepool_ssh_private_key      => hiera('nodepool_ssh_private_key'),
    git_source_repo               => 'https://git.openstack.org/openstack-infra/nodepool',
    revision                      => 'master',
    vhost_name                    => $::fqdn,
    statsd_host                   => '',
    elements_dir                  => '/etc/project-config/nodepool/elements',
    scripts_dir                   => '/etc/project-config/nodepool/scripts',
    image_log_document_root       => '/var/log/nodepool/image',
    image_log_periodic_cleanup    => true,
    enable_image_log_via_http     => true,
    environment                   => {
      'NODEPOOL_SSH_KEY' => hiera('nodepool_ssh_pubkey')
    },
    jenkins_masters               => [
      {
        name        => 'jenkins',
        url         => sprintf('http://%s:8080', hiera('jenkins_host')),
        user        => hiera('jenkins_api_user', 'username'),
        apikey      => hiera('jenkins_api_key'),
        credentials => hiera('jenkins_credentials_id')
      }
    ],
    require                       => Class['project_config']
  }

  $nodepool_ssh_pubkey = hiera('nodepool_ssh_pubkey')
  $os_auth_url = hiera('os_auth_url')
  $os_tenant_name = hiera('os_tenant_name')
  $os_username = hiera('os_username')
  $os_password = hiera('os_password')

  class { 'nodepool_configure':
    jenkins_host => hiera('jenkins_host'),
    jenkins_user => hiera('jenkins_api_user'),
    zuul_host    => hiera('zuul_host'),
    net_id       => hiera('nodepool_network_uuid'),
    require      => Class['nodepool']
  }

  exec { 'start_nodepool' :
    command     => 'service nodepool start',
    path        => '/usr/bin:/bin',
    require     => [
      Class['nodepool'],
      Class['nodepool_configure'],
    ]
  }

  exec { 'start_nodepool_builder' :
    command     => 'service nodepool-builder start',
    path        => '/usr/bin:/bin',
    require     => [
      Class['nodepool'],
      Class['nodepool_configure'],
    ]
  }
}

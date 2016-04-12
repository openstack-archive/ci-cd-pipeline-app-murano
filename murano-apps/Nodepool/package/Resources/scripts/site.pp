node default {
  class { 'openstack_project::server':
    sysadmins                 => hiera('sysadmins', []),
    iptables_public_tcp_ports => [80],
  }

  class { 'nodepool':
    mysql_root_password           => hiera('nodepool_mysql_root_password'),
    mysql_password                => hiera('nodepool_mysql_password'),
    nodepool_ssh_private_key      => hiera('nodepool_ssh_private_key'),
    git_source_repo               => 'https://git.openstack.org/openstack-infra/nodepool',
    revision                      => 'master',
    vhost_name                    => $::fqdn,
    statsd_host                   => '',
    image_log_document_root       => '/var/log/nodepool/image',
    image_log_periodic_cleanup    => true,
    enable_image_log_via_http     => true,
    environment                   => {},
    jenkins_masters               => [
      {
        name        => 'jenkins',
        url         => sprintf('http://%s:8080', hiera('jenkins_host')),
        user        => hiera('jenkins_api_user', 'username'),
        apikey      => hiera('jenkins_api_key')
      }
    ]
  }

  class { 'nodepool_configure':
    jenkins_host => hiera('jenkins_host'),
    require => Class['nodepool']
  }
}

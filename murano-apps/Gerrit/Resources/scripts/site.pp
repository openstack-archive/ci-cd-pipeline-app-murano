node default {

  class { 'openstack_project::server':
    iptables_public_tcp_ports => [80, 443, 8081, 29418],
    sysadmins                 => hiera('sysadmins', []),
  }

  class { 'openstack_project::gerrit':
    ssl_cert_file                       => "/etc/ssl/certs/${::fqdn}.pem",
    ssl_key_file                        => "/etc/ssl/private/${::fqdn}.key",
    ssl_chain_file                      => '',
    ssl_chain_file_contents             => '',
    ssl_cert_file_contents              => hiera('gerrit_ssl_cert_file_contents'),
    ssl_key_file_contents               => hiera('gerrit_ssl_key_file_contents'),
    ssh_dsa_key_contents                => hiera('gerrit_ssh_dsa_key_contents'),
    ssh_dsa_pubkey_contents             => hiera('gerrit_ssh_dsa_pubkey_contents'),
    ssh_rsa_key_contents                => hiera('gerrit_ssh_rsa_key_contents'),
    ssh_rsa_pubkey_contents             => hiera('gerrit_ssh_rsa_pubkey_contents'),
    ssh_project_rsa_key_contents        => hiera('gerrit_ssh_project_rsa_key_contents'),
    ssh_project_rsa_pubkey_contents     => hiera('gerrit_ssh_project_rsa_pubkey_contents'),
    ssh_replication_rsa_key_contents    => hiera('ssh_replication_rsa_key_contents'),
    ssh_replication_rsa_pubkey_contents => hiera('gerrit_replication_ssh_rsa_pubkey_contents'),

    ssh_welcome_rsa_key_contents        => hiera('welcome_message_gerrit_ssh_private_key'),

    ssh_welcome_rsa_pubkey_contents     => hiera('welcome_message_gerrit_ssh_public_key'),
    email                               => 'review@openstack.org',
      # 1 + 100 + 9 + 2 + 2 + 25 => 139(rounded up)
    database_poollimit                  => '150',
    container_heaplimit                 => '12g',
    core_packedgitopenfiles             => '4096',
    core_packedgitlimit                 => '400m',
    core_packedgitwindowsize            => '16k',
    sshd_threads                        => '100',
    index_threads                       => 4,
    httpd_maxqueued                     => '200',
    httpd_maxwait                       => '5000min',
    war                                 =>
      'http://tarballs.openstack.org/ci/gerrit/gerrit-v2.11.4.11.a14450f.war',
    contactstore                        => false,
    contactstore_appsec                 => '',
    contactstore_pubkey                 => '',
    contactstore_url                    =>
      'http://direct.openstack.org/verify/member/',
    acls_dir                            => hiera('gerrit_acls_dir'),
    notify_impact_file                  => hiera('gerrit_notify_impact_file'),
    projects_file                       => hiera('jeepyb_project_file'),
    projects_config                     => hiera('jeepyb_project_file'),
    github_username                     => 'openstack-gerrit',
    github_oauth_token                  => hiera('gerrit_github_token'),
    github_project_username             => hiera('github_project_username', 'username'),
    github_project_password             => hiera('github_project_password'),
    mysql_host                          => hiera('gerrit_mysql_host', 'localhost'),
    mysql_password                      => hiera('gerrit_db_password'),
    email_private_key                   => hiera('gerrit_email_private_key'),
    token_private_key                   => hiera('gerrit_rest_token_private_key'),
    swift_username                      => hiera('swift_store_user', 'username'),
    swift_password                      => hiera('swift_store_key'),
    replication_force_update            => true,
    replication                         => [
    ],
    require => [
	      Class['project_config'],
    ],
  }
  gerrit::plugin { 'javamelody':
    version => '3fefa35',
  }
  class { 'gerrit::remotes':
    ensure => absent,
  }

  # exec { "/usr/xpg4/bin/id >/tmp/puppet-id-test 2>&1",
  #   user => "puppet",
  #
  # }

  if ! defined(Class['project_config']) {
    class { 'project_config':
      url  => hiera('project_config_repo'),
    }
  }
}

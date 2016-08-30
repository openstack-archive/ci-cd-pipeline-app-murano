#
# Top-level variables
#
# There must not be any whitespace between this comment and the variables or
# in between any two variables in order for them to be correctly parsed and
# passed around in test.sh
#

#
# Default: should at least behave like an openstack server
#
node default {
  # class { 'openstack_project::server':
  #   # TODO: 8140 should be only open on the puppet master
  #   iptables_public_tcp_ports => [8140],
  #   sysadmins => hiera('sysadmins', []),
  # }
}

#
# Long lived servers:
#
# Node-OS: trusty
node 'review' {
  $project_config_repo = hiera('project_config_repo')



  class { 'openstack_project::server':
    iptables_public_tcp_ports => [80, 443, 8081, 29418],
    sysadmins                 => hiera('sysadmins', []),
    certname                  => 'review',
    ca_server                 => 'puppet',
    puppetmaster_server       => 'puppet',
    enable_unbound            => false,
    manage_exim               => false,
  }

  class { '::mysql::server':
     root_password           => hiera('gerrit_db_root_password'),
     remove_default_accounts => true,
  }
  mysql::db { 'reviewdb':
    user     => hiera('gerrit_db_user'),
    password => hiera('gerrit_db_password'),
    host     => 'localhost',
    grant    => ['all'],
  }

  class { 'openstack_project::review':
    project_config_repo                 => $project_config_repo,
    projects_config                     => 'openstack_project/review.projects.ini.erb',
    # projects_file                       => hiera('jeepyb_project_file'),
    github_oauth_token                  => hiera('gerrit_github_token'),
    github_project_username             => hiera('github_project_username', 'username'),
    github_project_password             => hiera('github_project_password'),
    mysql_host                          => hiera('gerrit_mysql_host', 'localhost'),
    mysql_password                      => hiera('gerrit_mysql_password'),
    email_private_key                   => hiera('gerrit_email_private_key'),
    token_private_key                   => hiera('gerrit_rest_token_private_key'),
    # gerritbot_password                  => hiera('gerrit_gerritbot_password'),
    # gerritbot_ssh_rsa_key_contents      => hiera('gerritbot_ssh_rsa_key_contents'),
    # gerritbot_ssh_rsa_pubkey_contents   => hiera('gerritbot_ssh_rsa_pubkey_contents'),
    ssl_cert_file_contents              => hiera('gerrit_ssl_cert_file_contents'),
    ssl_key_file_contents               => hiera('gerrit_ssl_key_file_contents'),
    # ssl_chain_file_contents             => hiera('gerrit_ssl_chain_file_contents'),
    ssl_chain_file                      => '',
    ssl_chain_file_contents             => '',
    ssh_dsa_key_contents                => hiera('gerrit_ssh_dsa_key_contents'),
    ssh_dsa_pubkey_contents             => hiera('gerrit_ssh_dsa_pubkey_contents'),
    ssh_rsa_key_contents                => hiera('gerrit_ssh_rsa_key_contents'),
    ssh_rsa_pubkey_contents             => hiera('gerrit_ssh_rsa_pubkey_contents'),
    ssh_project_rsa_key_contents        => hiera('gerrit_project_ssh_rsa_key_contents'),
    ssh_project_rsa_pubkey_contents     => hiera('gerrit_project_ssh_rsa_pubkey_contents'),
    ssh_welcome_rsa_key_contents        => hiera('welcome_message_gerrit_ssh_private_key'),
    ssh_welcome_rsa_pubkey_contents     => hiera('welcome_message_gerrit_ssh_public_key'),
    ssh_replication_rsa_key_contents    => hiera('gerrit_replication_ssh_rsa_key_contents'),
    ssh_replication_rsa_pubkey_contents => hiera('gerrit_replication_ssh_rsa_pubkey_contents'),
    lp_sync_consumer_key                => hiera('gerrit_lp_consumer_key'),
    lp_sync_token                       => hiera('gerrit_lp_access_token'),
    lp_sync_secret                      => hiera('gerrit_lp_access_secret'),
    contactstore_appsec                 => hiera('gerrit_contactstore_appsec'),
    contactstore_pubkey                 => hiera('gerrit_contactstore_pubkey'),
    swift_username                      => hiera('swift_store_user', 'username'),
    swift_password                      => hiera('swift_store_key'),

    require => [
      # Package['build-essential'],
      # Package['libssl-dev'],
      # Package['libffi-dev'],
      # Package['python-dev'],
      Class['::mysql::server'],
    ]
  }

  exec { 'openstack_project::gerrit':
    command     => "/usr/bin/git remote set-url origin $project_config_repo",
    cwd         => "/etc/project-config/",
    require     => [
	      Class['project_config'],
    ],
  }
}

# Node-OS: precise
node jenkins {
  package { 'unzip':
    ensure => present
  }

  class { 'openstack_project::server':
    iptables_public_tcp_ports => [80, 443, 8080],
    sysadmins               => hiera('sysadmins', []),
    certname                => 'jenkins',
    ca_server               => 'puppet',
    puppetmaster_server     => 'puppet',
  }
  class { 'openstack_project::jenkins':
    vhost_name              => 'jenkins',
    jenkins_password        => hiera('jenkins_jobs_password'),
    jenkins_ssh_private_key => hiera('jenkins_ssh_private_key_contents'),
    ssl_cert_file           => '/etc/ssl/certs/ssl-cert-snakeoil.pem',
    ssl_key_file            => '/etc/ssl/private/ssl-cert-snakeoil.key',
    ssl_chain_file          => '',
    jenkins_username        => 'gerrit',
    serveradmin             => 'jenkins@example.com',
    project_config_repo     => hiera('project_config_repo'),
    project_config_base     => '',
  }
}


node openldap {

  $dc = hiera("ldap_dc")
  $dn = domain2dn(hiera("ldap_domain"))
  $user = hiera('ldap_root_user')

  class { 'ldap::server':
    suffix  => $dn,
    rootdn  => "cn=$user,$dn",
    rootpw  => hiera('ldap_root_password'),
    log_level => 1,
  }

  class { 'ldap::client':
    uri      => 'ldap://openldap',
    base     => "$dn",
  }

  $ldap_defaults = {
    ensure   => present,
    host     => 'openldap',
    base     => "$dn",
    port     => 389,
    ssl      => false,
    username => "cn=root,${dn}",
    password => hiera('ldap_root_password')
  }

  $ldap_entries = {
    "$dn"                   =>{
      attributes => {
        dc          => "$dc",
        objectClass => ['top','domain'],
        description => 'Tree root'
      },
    },
    "ou=users,$dn"          =>{
      attributes => {
        ou         => "users",
        objectClass=>['top', 'organizationalUnit'],
        description=> "Users for ${dn}",
      }
    },
    "uid=user,ou=users,$dn"          =>{
      attributes => {
        cn         => "user",
        uid        => "user",
        sn         => "user",
        uidNumber  => 1001,
        gidNumber  => 1001,
        objectClass=> [
          'top',
          'posixAccount',
          'shadowAccount',
          'iNetOrgPerson',
          'organizationalPerson'],
        description=> "User",
        gecos      => "user@$dn",
        homeDirectory => "/home/user",
        userPassword=> sha1digest(hiera('ldap_password')),
        shadowLastChange=> "0",
        shadowMax   => "0",
        shadowWarning=> "0",
        mail        => "mail@example.com"
      }
    },
  }

  create_resources('ldap_entry', $ldap_entries,$ldap_defaults)
}

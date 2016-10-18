node default {

  class { 'openstackci::jenkins_master':
    logo                    => 'openstack.png',
    serveradmin             => 'webmaster@${::fqdn}',
    jenkins_password        => '',
    jenkins_ssh_private_key => hiera('jenkins_ssh_private_key_contents'),
    jenkins_ssh_public_key  => hiera('jenkins_ssh_pubkey_contents'),
    ssl_cert_file           => '/etc/ssl/certs/ssl-cert-snakeoil.pem',
    ssl_key_file            => '/etc/ssl/private/ssl-cert-snakeoil.key',
    manage_jenkins_jobs     => false,
    jenkins_version        => '2.19.1',
  }

  package { 'unzip':
    ensure => present
  }
}

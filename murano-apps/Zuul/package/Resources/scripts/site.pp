node default {

  $gerrit_server = hiera('gerrit_server')
  $gerrit_ssh_host_key = hiera('gerrit_ssh_host_key')
  $zuul_host = hiera('zuul_host')

  class { 'openstackci::zuul_scheduler':
    gearman_server                 => '127.0.0.1',
    gerrit_server                  => hiera('gerrit_server'),
    gerrit_user                    => hiera('gerrit_user'),
    known_hosts_content            => "${gerrit_server} ${gerrit_ssh_host_key}",
    zuul_ssh_private_key           => hiera('zuul_ssh_private_key_contents'),
    job_name_in_report             => true,
    project_config_repo            => hiera('project_config_repo'),
    zuul_url                       => "http://${zuul_host}/p",
    status_url                     => "http://${zuul_host}",
    git_email                      => 'jenkins@openstack.org',
    git_name                       => 'OpenStack Jenkins',
  }

  class { '::zuul::merger':
    ensure => running,
    require => Class['openstackci::zuul_scheduler']
  }

}
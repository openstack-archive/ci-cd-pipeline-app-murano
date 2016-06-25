node default{
  package { 'ntp':
    ensure => 'installed',
  }

  class { '::puppet':
    server                => true,
    server_foreman        => false,
    server_reports        => 'store',
    server_http           => true,
    server_http_port      => 8130, # default: 8139
    server_http_allow     => [],
    # server_http_allow    => ['10.20.30.1', 'puppetbalancer.my.corp'],
    server_external_nodes => '',
    server_git_repo       => true,
    puppetmaster =>  'puppet',
    server_puppetserver_version => '2.4.99'
    # server_puppetserver_version
  }

  file { '/tmp/puppet-server':
    ensure  => 'present',
    replace => 'no', # this is the important property
    content => "From Puppet\n",
    mode    => '0644',
  }
}
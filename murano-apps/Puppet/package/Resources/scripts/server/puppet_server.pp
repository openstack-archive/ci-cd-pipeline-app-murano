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
    server_external_nodes => '',
    server_git_repo       => true,
    puppetmaster =>  'puppet',
    server_puppetserver_version => '2.4.99'
  }

  package {'librarian-puppet':
    ensure => 'installed',
    provider => 'gem'
  }
}
node default{
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
    puppetmaster =>  'masterpuppet'
    # server_puppetserver_version
  }
}
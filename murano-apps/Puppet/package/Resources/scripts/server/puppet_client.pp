node default{
  package {'iptables-persistent':
    ensure => 'installed'
  }
  class { '::puppet':
    server  => false,
    runmode => 'cron',
    puppetmaster => 'puppet',
    client_certname => hiera('node_role')
  }
}
node default{
  class { '::puppet':
    server  => false,
    runmode => 'cron',
    puppetmaster => 'puppet',
    client_certname => hiera('node_role')
  }

  file { '/tmp/puppet-client':
    ensure  => 'present',
    replace => 'no', # this is the important property
    content => "From Puppet\n",
    mode    => '0644',
  }
}
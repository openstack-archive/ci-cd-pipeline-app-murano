node default{
  class { '::puppet':
    server  => false,
    runmode => 'service'
  }

  file { '/tmp/puppet-client':
    ensure  => 'present',
    replace => 'no', # this is the important property
    content => "From Puppet\n",
    mode    => '0644',
  }
}
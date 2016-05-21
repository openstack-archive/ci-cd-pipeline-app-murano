file { '/usr/local/bin/periodic_puppet.sh':
  ensure => 'present',
  audit  => 'all',
}

cron { "puppet":
  user    => 'root',
  ensure  => present,
  command => "/usr/local/bin/periodic_puppet.sh",
  hour    => '*',
  minute  => '*/5',
}
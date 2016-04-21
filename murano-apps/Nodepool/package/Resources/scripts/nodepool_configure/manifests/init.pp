class nodepool_configure (
  $jenkins_host    = undef,
  $jenkins_user    = undef,
  $zuul_host       = undef,
  $net_id          = undef,
) {
  file { '/etc/nodepool/nodepool.yaml':
    ensure  => present,
    owner   => 'nodepool',
    group   => 'nodepool',
    mode    => '0644',
    content => template('nodepool_configure/nodepool.yaml.erb')
  }
}
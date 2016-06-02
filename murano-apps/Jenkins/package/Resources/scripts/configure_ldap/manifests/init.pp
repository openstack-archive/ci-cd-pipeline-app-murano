class configure_ldap (
  $openldap_ip    = undef,
  $admin_name     = undef,
  $admin_password = undef,
  $domain         = undef,
) {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  file { '/var/lib/jenkins/config.xml':
    notify  => Service['jenkins'],
    ensure  => present,
    owner   => 'jenkins',
    group   => 'jenkins',
    mode    => '0644',
    content => template('configure_ldap/config.erb'),
  }
}
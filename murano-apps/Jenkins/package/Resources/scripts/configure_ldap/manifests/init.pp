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
  file { '/etc/jenkins_jobs/jenkins_jobs.ini':
    ensure => present,
  }->
  file_line { 'Provide valid username to jjb config':
    path => '/etc/jenkins_jobs/jenkins_jobs.ini',
    line => "user=${admin_name}",
    match   => "^user=gerrig.*$",
  }->
  file_line { 'Provide valid password to jjb config':
    path => '/etc/jenkins_jobs/jenkins_jobs.ini',
    line => "password=${admin_password}",
    match   => "^password=.*$",
  }
}
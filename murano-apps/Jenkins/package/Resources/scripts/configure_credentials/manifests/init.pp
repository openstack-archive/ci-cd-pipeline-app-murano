class configure_credentials (
) {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  file { '/var/lib/jenkins/credentials.xml':
      notify  => Service['jenkins'],
      ensure  => present,
      owner   => 'jenkins',
      group   => 'jenkins',
      mode    => '0644',
      content => file('configure_credentials/credentials.xml'),
    }
}
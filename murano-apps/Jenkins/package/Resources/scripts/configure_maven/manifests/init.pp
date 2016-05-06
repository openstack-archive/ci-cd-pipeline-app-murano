class configure_maven (
  $maven_name = undef,
  $maven_id = undef,
) {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  file { '/var/lib/jenkins/hudson.tasks.Maven.xml':
      notify  => Service['jenkins'],
      ensure  => present,
      owner   => 'jenkins',
      group   => 'jenkins',
      mode    => '0644',
      content => template('configure_maven/hudson.tasks.Maven.xml.erb'),
    }
}
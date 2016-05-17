class configure_gerrit_plugin (
  $gerrit_host = undef,
) {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  file { '/var/lib/jenkins/gerrit-trigger.xml':
      notify  => Service['jenkins'],
      ensure  => present,
      owner   => 'jenkins',
      group   => 'jenkins',
      mode    => '0644',
      content => template('configure_gerrit_plugin/gerrit-trigger.xml.erb'),
    }
}

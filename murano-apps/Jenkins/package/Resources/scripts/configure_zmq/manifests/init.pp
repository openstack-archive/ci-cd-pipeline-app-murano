class configure_zmq (
  $zmq_port = undef,
) {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  file { '/var/lib/jenkins/org.jenkinsci.plugins.ZMQEventPublisher.HudsonNotificationProperty.xml':
      notify  => Service['jenkins'],
      ensure  => present,
      owner   => 'jenkins',
      group   => 'jenkins',
      mode    => '0644',
      content => template('configure_zmq/org.jenkinsci.plugins.ZMQEventPublisher.HudsonNotificationProperty.xml.erb'),
    }
}
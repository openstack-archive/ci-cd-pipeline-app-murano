class configure_gearman (
  $gearman_host = undef,
  $gearman_port = undef
) {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  file { '/var/lib/jenkins/hudson.plugins.gearman.GearmanPluginConfig.xml':
      notify  => Service['jenkins'],
      ensure  => present,
      owner   => 'jenkins',
      group   => 'jenkins',
      mode    => '0644',
      content => template('configure_gearman/hudson.plugins.gearman.GearmanPluginConfig.xml.erb'),
    }
}
node default {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  jenkins::plugin { 'cloudfoundry':
    notify  => Service['jenkins'],
    version         => $version,
  }
}
node default {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  jenkins::plugin { 'docker-build-publish':
    notify  => Service['jenkins'],
    version         => $version,
  }
}
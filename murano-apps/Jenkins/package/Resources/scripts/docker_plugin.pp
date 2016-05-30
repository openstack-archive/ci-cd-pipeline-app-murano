node default {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  jenkins::plugin { 'docker-build-publish':
    notify  => Service['jenkins'],
    version         => $version,
    require => [
      Jenkins::Plugin['token-macro'],
      Jenkins::Plugin['docker-commons'],
      Jenkins::Plugin['authentication-tokens'],
      Jenkins::Plugin['icon-shim'],
      Jenkins::Plugin['credentials]
    ]
  }
}

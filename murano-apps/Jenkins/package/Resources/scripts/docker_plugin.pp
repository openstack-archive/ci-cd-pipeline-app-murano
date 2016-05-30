node default {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }

  jenkins::plugin { 'authentication-tokens':
    notify  => Service['jenkins'],
    require => Jenkins::Plugin['credentials']
  }

  jenkins::plugin { 'docker-commons':
    notify  => Service['jenkins'],
    require => [
      Jenkins::Plugin['authentication-tokens'],
      Jenkins::Plugin['icon-shim'],
      Jenkins::Plugin['credentials']
    ]
  }

  jenkins::plugin { 'docker-build-publish':
    notify  => Service['jenkins'],
    require => [
      Jenkins::Plugin['token-macro'],
      Jenkins::Plugin['docker-commons']
    ]
  }
}

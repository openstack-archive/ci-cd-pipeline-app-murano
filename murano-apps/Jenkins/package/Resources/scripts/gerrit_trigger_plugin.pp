node default {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }

  jenkins::plugin { 'structs':
    notify  => Service['jenkins']
  }

  jenkins::plugin { 'rabbitmq-consumer':
    notify  => Service['jenkins']
  }

  jenkins::plugin { 'rebuild':
    notify  => Service['jenkins']
  }

  jenkins::plugin { 'workflow-step-api':
    notify  => Service['jenkins'],
    require => Jenkins::Plugin['structs']
  }

  jenkins::plugin { 'gerrit-trigger':
    notify  => Service['jenkins'],
    version => '2.20.0',
    require => [
      Jenkins::Plugin['workflow-step-api'],
      Jenkins::Plugin['rebuild'],
      Jenkins::Plugin['structs'],
      Jenkins::Plugin['rabbitmq-consumer']
    ]
  }
}
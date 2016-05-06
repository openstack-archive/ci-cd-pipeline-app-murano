node default {
  class { 'configure_maven':
    maven_name    => 'MAVEN',
    maven_id      => '3.3.9',
  }
}
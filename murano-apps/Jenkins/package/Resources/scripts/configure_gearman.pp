node default {
  class { 'configure_gearman':
    gearman_host => hiera('gearman_host'),
    gearman_port => hiera('gearman_port')
  }
}
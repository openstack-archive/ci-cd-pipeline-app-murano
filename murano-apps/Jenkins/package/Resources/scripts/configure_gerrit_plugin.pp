node default {
  class { 'configure_gerrit_plugin':
    gerrit_host    => hiera('gerrit_host')
  }
}

node default {
  class { '::mysql::server':
    root_password           => hiera('gerrit_db_root_password'),
    remove_default_accounts => true,
  }

  mysql::db { 'reviewdb':
    user     => hiera('gerrit_db_user'),
    password => hiera('gerrit_db_password'),
    host     => 'localhost',
    grant    => ['all'],
  }
}

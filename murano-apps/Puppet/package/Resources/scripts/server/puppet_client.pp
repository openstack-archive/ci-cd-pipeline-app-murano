node default{
  class { '::puppet':
    server  => false,
    runmode => 'cron'
  }
}
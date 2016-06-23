cron { "update_layout":
  user    => 'root',
  ensure  => present,
  command => "bash /usr/local/bin/update_layout.sh",
  hour    => '*',
  minute  => '*/5',
}
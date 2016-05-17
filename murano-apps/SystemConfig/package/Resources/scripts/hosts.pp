node default {
   $hosts = hiera('hosts')
   create_resources(host, $hosts)
}

node default {
  $ssh_key = hiera('jenkins_ssh_pubkey_contents', undef)
  if $ssh_key {
    class { 'jenkins::jenkinsuser':
      ssh_key => $ssh_key
    }
  }
}

node default {
  $ssh_key = hiera('gerrit_ssh_rsa_key_contents', undef)
  if $ssh_key {
    class { 'jenkins::jenkinsuser':
      ssh_key => $ssh_key
    }
  }
}
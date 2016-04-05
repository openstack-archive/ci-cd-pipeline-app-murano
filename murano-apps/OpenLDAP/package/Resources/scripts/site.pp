node default {

  $dc = hiera("ldap_dc")
  $dn = domain2dn(hiera("ldap_domain"))
  $user = hiera('ldap_root_user')

  class { 'ldap::server':
    suffix  => $dn,
    rootdn  => "cn=$user,$dn",
    rootpw  => hiera('ldap_root_password'),
  }

  $ldap_defaults = {
    ensure   => present,
    base     => $dn,
    host     => 'localhost',
    port     => 389,
    ssl      => false,
    username => "cn=$user,${dn}",
    password => hiera('ldap_root_password')
  }

  $ldap_entries = {
    "$dn"                   =>{
      attributes => {
        dc          => "$dc",
        objectClass => ['top','domain'],
        description => 'Tree root'
      },
    },
    "ou=users,$dn"          =>{
      attributes => {
        ou         => "users",
        objectClass=>['top', 'organizationalUnit'],
        description=> "Users for ${dn}",
      }
    },
  }

  create_resources('ldap_entry', $ldap_entries,$ldap_defaults)
}



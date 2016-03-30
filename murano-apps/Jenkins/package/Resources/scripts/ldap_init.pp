node default {
  class { 'configure_ldap':
    openldap_ip    => hiera('ldap_ip'),
    admin_name     => hiera('ldap_root_user'),
    admin_password => hiera('ldap_root_password'),
    domain         => hiera('ldap_domain')
  }
}
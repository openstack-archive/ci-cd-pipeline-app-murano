$db_root_password = hiera('gerrit_db_root_password')

$admin_user     = hiera('ldap_root_user')
$admin_password = hiera('ldap_root_password')

$user     = hiera('ldap_user')
$password = hiera('ldap_password')

$project_user       = 'project-creator'
$project_user_id    = 99
$project_user_key   = hiera('gerrit_ssh_project_rsa_pubkey_contents')
$project_user_email = "${$project_user}@${fqdn}"


file {'gerrit_gitconfig':
    ensure  => file,
    path    => '/home/gerrit2/.gitconfig',
    owner   => 'gerrit2',
    group   => 'gerrit2',
    content => template('openstack_project/gerrit_gitconfig.erb')
}

file {'/var/log/manage_projects.log':
    ensure  => file,
    owner   => 'gerrit2',
    group   => 'gerrit2',
}

#Currently gerrit is starting during more than 600 seconds
exec { 'check_gerrit':
    command     => "/usr/bin/curl -s -o /dev/null -w \"%{http_code}\" -k https://${fqdn}/ | grep -q 200",
    try_sleep   => 10,
    tries       => 90,
    notify      => Exec['first_admin_login'],
}

exec { 'first_admin_login':
     command     => "/usr/bin/curl -s -o /dev/null -w \"%{http_code}\" -k -X POST -d \"username=${admin_user}\" -d \"password=${admin_password}\" https://${fqdn}/login | grep -q 302",
     try_sleep   => 10,
     tries       => 6,
     refreshonly => true,
     notify      => Exec['create_gerrit_user_for_projects'],
}

exec { 'create_gerrit_user_for_projects':
    command     => "/bin/sleep 60 && /usr/bin/mysql -u root -p${db_root_password} << EOF
use reviewdb;
INSERT INTO accounts (full_name, preferred_email, inactive, account_id) VALUES (\'${project_user}\',\'${project_user_email}\', 'N', ${project_user_id});
INSERT INTO account_id (s) VALUES (${project_user_id});
INSERT INTO account_group_members (account_id, group_id) VALUES (${project_user_id},(SELECT group_id FROM account_group_names WHERE name='Administrators'));
INSERT INTO account_group_members_audit (added_by, account_id, group_id, added_on) VALUES (${project_user_id}, ${project_user_id}, 1,(SELECT registered_on FROM accounts WHERE account_id=${project_user_id}));
INSERT INTO account_ssh_keys (ssh_public_key, valid, account_id, seq) VALUES ( \'${project_user_key}\', 'Y', ${project_user_id}, 1 );
INSERT INTO account_external_ids (account_id, email_address, external_id) VALUES ( ${project_user_id}, \'${project_user_email}\', \'username:${project_user}\');
EOF",
    refreshonly => true,
    notify      => Exec['upload_gerrit_projects'],
}

#
# Create projects from initially cloned project config
# it contains project config itself also
# wait for gerrit being restarted and up
exec { 'upload_gerrit_projects':
    user        => 'gerrit2',
    environment => ["HOME=/home/gerrit2"],
    command     => "/usr/local/bin/manage-projects -v -d -l /var/log/manage_projects.log",
    try_sleep   => 60,
    tries       => 20,
    refreshonly => true,
    require     => [
            File['gerrit_gitconfig'],
            File['/var/log/manage_projects.log'],
          ],
}

include logrotate
logrotate::file { 'manage_projects.log':
    log     => '/var/log/manage_projects.log',
    options => [
      'compress',
      'missingok',
      'rotate 30',
      'daily',
      'notifempty',
      'copytruncate',
    ],
    require => Exec['upload_gerrit_projects'],
    notify      => Exec['first_user_login'],
}

exec { 'first_user_login':
     command     => "/usr/bin/curl -s -o /tmp/hhhh -w \"%{http_code}\" -k -X POST -d \"username=${user}\" -d \"password=${password}\" https://${fqdn}/login | grep -q 302",
     try_sleep   => 10,
     tries       => 6,
     refreshonly => true,
}

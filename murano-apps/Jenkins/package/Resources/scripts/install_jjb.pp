node default {

  $username = hiera('ldap_root_user', 'jenkins')
  $password = hiera('ldap_root_password', '')
  $project_config_repo = hiera('project_config_repo')

  if ! defined(Class['project_config']) {
    class { 'project_config':
      url                            => $project_config_repo,
      base                           => '',
    }
  }
  class { '::jenkins::job_builder':
    url                         => 'http://localhost:8080',
    username                    => $username,
    password                    => $password,
    jenkins_jobs_update_timeout => 1200,
    git_revision                => 'master',
    git_url                     => 'https://git.openstack.org/openstack-infra/jenkins-job-builder',
    config_dir                  => $::project_config::jenkins_job_builder_config_dir,
    require                     => $::project_config::config_dir,
    extensions                  => [
      {'name' => 'job_builder', 'parameters' => [{'name' => 'ignore_cache', 'value' => 'True'}]}
    ],
  }
  cron { "update_list_of_jobs":
    user    => 'root',
    ensure  => present,
    command => "bash /usr/local/bin/update_jobs.sh",
    hour    => '*',
    minute  => '*/5',
  }
}
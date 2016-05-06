class configure_git (
  $git_user = undef,
  $git_user_email = undef
) {
  service { 'jenkins':
    ensure => running,
    enable => true,
  }
  file { '/var/lib/jenkins/hudson.plugins.git.GitSCM.xml':
      notify  => Service['jenkins'],
      ensure  => present,
      owner   => 'jenkins',
      group   => 'jenkins',
      mode    => '0644',
      content => template('configure_git/hudson.plugins.git.GitSCM.xml.erb'),
    }
}
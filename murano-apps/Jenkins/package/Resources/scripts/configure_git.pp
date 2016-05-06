node default {
  class { 'configure_git':
    git_user => hiera('git_user'),
    git_user_email => hiera('git_user_email')
  }
}
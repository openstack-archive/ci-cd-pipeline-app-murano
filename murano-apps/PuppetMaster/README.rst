Puppet Master Support for Murano
================================

Puppet is an open-source configuration management tool. It runs on many
Unix-like systems as well as on Microsoft Windows, and includes its own
declarative language to describe system configuration.


This application is a demonstration of Puppet Library capabilities.


Application creates a set of nodes and connects them to a puppet master.
Every name in the list of the nodes names is the cert name in the puppet
master. Dependencies can be installed by pointing Puppetfile which
will be used to install modules by librarian-puppet. All nodes
are included in the "production" environment and that is the only
environment. Cron runs puppet-agent twice in an hour.

Tested under Ubuntu 14.04 Murano image.


Usage example
^^^^^^^^^^^^^
As an example of input data you can use:

Nodes list::

  server
  slave1
  slave2

Puppetfile link::

  http://paste.openstack.org/raw/529624/

Main manifest::

  modules/puppettest/manifests/


The resulting environment contains GoCD server with a slaves connected.
GoCD server will run on "server" node on port :8153

Known issues
^^^^^^^^^^^^

Cron runs puppet-agent twice in an hour and agents do not run during deployment.
You can wait while cron will run puppet agents or run them manually by executing::

    /usr/bin/puppet agent --config /etc/puppet/puppet.conf --onetime --no-daemonize --verbose --no-splay

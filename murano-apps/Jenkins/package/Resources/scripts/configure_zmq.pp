node default {
  class { 'configure_zmq':
    zmq_port    => 8888,
  }
}
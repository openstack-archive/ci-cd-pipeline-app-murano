sudo add-apt-repository ppa:vbernat/haproxy-1.5 -y

sudo apt-get update
sudo apt-get install -y haproxy

# Enabling HAProxy.
sudo sed -i 's/^ENABLED=.*/ENABLED=1/' /etc/default/haproxy

sudo chown -R $USER:$USER /etc/haproxy

# Starting HAProxy.
#sudo service haproxy restart


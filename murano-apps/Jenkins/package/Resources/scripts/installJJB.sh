cd ~
git clone https://git.openstack.org/openstack-infra/jenkins-job-builder
cd jenkins-job-builder

sudo apt-get install python-tox --assume-yes
tox -e venv -- sudo python setup.py install
tox -e venv -- sudo pip install -r requirements.txt


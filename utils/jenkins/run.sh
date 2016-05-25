#!/bin/sh

# Requirments:
# apt-get install python-venv python-pip build-essential libssl-dev libffi-dev -y

# Variables:
VENV_PATH=${VENV_PATH:-/.venv}
VENV_CLEAN=${VENV_PATH:-false}
TEST_NAME=${TEST_NAME:-none}

function prepare_venv() {
    echo 'LOG: Creating python venv for murano-client'
    mkdir -p ${VENV_PATH}
    virtualenv --system-site-packages  ${VENV_PATH}
    source ${VENV_PATH}/bin/activate
    #TODO install from requirments.txt ?
    pip install python-muranoclient
}

# Body
if [[ ("${VENV_CLEAN}" == true) || (! -f "${VENV_PATH}/bin/activate") ]]; then
    prepare_venv
fi

source ${VENV_PATH}/bin/activate
echo "LOG: murano client version: $(murano --version)"
if [[ "${TEST_NAME}" != "none" ]] ; then
    echo "LOG: Attempt to run test=${TEST_NAME}"
    ./utils/jenkins/${TEST_NAME}
fi


deactivate

#!/bin/bash

YUM_CMD=$(command -v yum 2> /dev/null)
APTGET_CMD=$(command -v apt-get 2> /dev/null)

BOLD="\e[1m"
UNBOLD="\e[22m"
NORMAL="\e[0m"
RED="\e[1;31m"
YELLOW="\e[1;33m"
GREEN="\e[1;32m"
BLUE="\e[1;34m"

_err()  { echo -e "${RED}${BOLD}Error: ${UNBOLD}${@}${NORMAL}"; }
_warn() { echo -e "${YELLOW}${BOLD}Warning: ${UNBOLD}${@}${NORMAL}"; }
_good() { echo -e "${GREEN}${BOLD}Success: ${UNBOLD}${@}${NORMAL}"; }
_info() { echo -e "${BLUE}${BOLD}Info: ${UNBOLD}${@}${NORMAL}"; }

install() {
    if [[ ! -z $YUM_CMD ]]; then
        yum install -y git python dbus-python
    elif [[ ! -z $APTGET_CMD ]]; then
        apt-get install -y git python python-apt python-dbus

        # Test for UFW
        $(dpkg -l ufw > /dev/null)
        if [[ !$? ]]; then
            apt-get install -y python-ufw
        fi
    else
        _err "Install could not determine package manager"
        exit 0
    fi
}

update () {
    if [[ ! -z $YUM_CMD ]]; then
        yum makecache fast && yum upgrade -y
    elif [[ ! -z $APTGET_CMD ]]; then
        apt-get update -y && apt-get upgrade -y
    else
        _err "Update could not determine package manager"
        exit 0
    fi
}

update   # updates system
install

pushd . > /dev/null
cd ~
git clone https://github.com/aeontechnology/blancco-pxe.git
cd blancco-pxe
                    git checkout develop
# Because of how this file is piped into bash, we need to reset our stdin
cat /dev/tty | python stage.py
popd > /dev/null

_info "Cleaning up..."
# Do all our removals...
_good "Installation complete. Please ensure there were no errors above."

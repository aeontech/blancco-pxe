#!/bin/bash

YUM_CMD=$(which yum)
APTGET_CMD=$(which apt-get)

BOLD="\e[1m"
UNBOLD="\e[22m"
NORMAL="\e[0m"
RED="\e[0;31m"
YELLOW="\e[1;33m"
GREEN="\e[1;32m"

_err()  { echo -e "${RED}${BOLD}Error: ${UNBOLD}${@}${NORMAL}"; }
_warn() { echo -e "${YELLOW}${BOLD}Warning: ${UNBOLD}${@}${NORMAL}"; }
_good() { echo -e "${GREEN}${BOLD}Success: ${UNBOLD}${@}${NORMAL}"; }

install() {
  if [[ ! -z $YUM_CMD ]]; then
    echo yum install -y $@
  elif [[ ! -z $APTGET_CMD ]]; then
    echo apt-get install -y $@
  else
    _err "Install could not determine package manager"
    exit 0
  fi
}

update () {
  if [[ ! -z $YUM_CMD ]]; then
    echo yum makecache fast && yum upgrade -y
  elif [[ ! -z $APTGET_CMD ]]; then
    echo apt-get update -y && apt-get upgrade -y
  else
    _err "Update could not determine package manager"
    exit 0
  fi
}


update   # updates system
install python git

pushd .
cd ~
git clone https://github.com/aeontechnology/blancco-pxe.git
cd blancco-pxe
python stage.py
popd

_good "Installation complete. Please ensure there were no errors above."

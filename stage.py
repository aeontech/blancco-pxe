#!/usr/bin/python

import sys
from src import log
from src.bootstrap import get_strapper

try:
    strapper = get_strapper()
    strapper.checkenv()
    strapper.install_packages()
    strapper.configure_packages()
except EnvironmentError:
    log.error(sys.exc_info()[1])
    exit(1)

exit(0)

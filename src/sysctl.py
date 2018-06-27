# Thanks, https://github.com/fmenabe/python-unix

from glob import glob
import os.path as path
from subprocess import Popen, PIPE

def execute(args):
    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    output = proc.communicate()[0]

    return proc.returncode, output

def list():
    lines = execute(['sysctl', '--all'])[1].rstrip()
    for line in lines.splitlines():
        param, value = line.split(' = ')
        yield (param, int(value) if value.isdigit() else value)

def get(param):
    output = execute(['sysctl', param])[1].rstrip()
    param, value = output.split(' = ')
    return int(value) if value.isdigit() else value

def set(param, value):
    return execute(['sysctl', '%s=%s' % (param, value)])[0] == 0

def read(param, default=None, filename=None):
    settings = readallconf()

    if param not in settings:
        if default is None:
            raise KeyError(param)
        else:
            return default

    return settings[param]

def write(param, value, filename=None):
    config = readconf(filename)
    config.update({param: value})

    return writeconf(config, filename)

def writeconf(config, filename=None):
    if filename and not filename.endswith('.conf'):
        return [False, '', "file extension must be '.conf'"]

    filepath = (path.join('/etc/sysctl.d/%s' % filename)
                if filename
                else '/etc/sysctl.conf')

    with open(filepath, 'w') as fhandler:
        fhandler.write('\n'.join('%s = %s' % (param, value)
                                 for param, value in config.items()))

    return execute(['sysctl', '-p %s' % filepath])

def readallconf():
    filepaths = [None] + [path.basename(f) for f in glob('/etc/sysctl.d/*.conf')]
    settings  = {}

    for file in filepaths:
        settings.update(readconf(file))

    return settings

def readconf(filename=None):
    filepath = (path.join('/etc/sysctl.d/%s' % filename)
                if filename
                else'/etc/sysctl.conf')

    with open(filepath) as fhandler:
        return {param.strip(): value.strip()
                for line in fhandler.read().splitlines()
                if line and not line.startswith('#')
                for param, value in [line.split('=')]}

import sys

def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True

# Initiate colors... This is nasty!
if not supports_color():
    colors = {
        'green': '',
        'orange': '',
        'blue': '',
        'red': '',
        'reset': '',
    }
elif sys.platform == 'win32':
    pass
else:
    colors = {
        'green':    '\x1b[1;32m',
        'orange':   '\x1b[1;33m',
        'blue':     '\x1b[1;34m',
        'red':      '\x1b[1;31m',
        'reset':    '\x1b[0m',
    }

def debug(message):
    print colors['blue'] + "DBG:  " + str(message) + colors['reset']

def info(message):
    print colors['blue'] + "INFO: " + str(message) + colors['reset']

def warn(message):
    print colors['orange'] + "WRN:  " + str(message) + colors['reset']

def error(message):
    print colors['red'] + "ERR:  " + str(message) + colors['reset']

def success(message):
    print colors['green'] + str(message) + colors['reset']

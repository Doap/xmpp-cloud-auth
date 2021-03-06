# systemd.daemon listen_fds_with_names() compatibility/abstraction library
# for socket activation
import os
import logging

def listen_fds_with_names():
    '''Tries to get file descriptors from (in order):
    - listen_fds_with_names() # Not yet merged, see https://github.com/systemd/python-systemd/pull/60
    - listen_fds() # With own hack in case it finds $LISTEN_FDNAMES until listen_fds_with_names() is supported
    - None
    In the first two cases, it returns a hash of {fd: name} pairs'''
    try:
        from systemd.daemon import listen_fds_with_names
        # We have the real McCoy
        return listen_fds_with_names()
    except ImportError:
        # Try to fall back to listen_fds(),
        # possbily emulating listen_fds_with_names() here
        try:
            from systemd.daemon import listen_fds
        except ImportError:
            if os.path.exists('/run/systemd/system') and 'LISTEN_FDS' in os.environ:
                logging.error('Software from https://github.com/systemd/python-systemd/ missing; do `apt install python3-systemd` or `pip3 install systemd-python`. Please note the similarly-named `pip3 install python-systemd` does not provide the interfaces needed and may actually need to be UNINSTALLED first!')
                raise
            else:
                logging.info('Please `apt install python3-systemd` for future compatibility')
                return None
        fds = listen_fds()
        if fds:
            listeners = {}
            if 'LISTEN_FDNAMES' in os.environ:
                # Evil hack, should not be here!
                # Is here only because it seems unlikely
                # https://github.com/systemd/python-systemd/pull/60
                # will be merged and distributed anyting soon ;-(.
                # Diverges from original if not enough fdnames are provided
                # (but this should not happen anyway).
                names = os.environ['LISTEN_FDNAMES'].split(':')
            else:
                names = ()
            for i in range(0, len(fds)):
                if i < len(names):
                    listeners[fds[i]] = names[i]
                else:
                    listeners[fds[i]] = 'unknown'
            return listeners
        else:
            return None

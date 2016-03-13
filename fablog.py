from fabric.api import task

import functools
import logging
import sys
import time


logging.basicConfig(format='%(asctime)s: %(message)s',
                    filename=time.strftime('fablog-%Y-%m-%dT%H-%M-%S.log'),
                    filemode='w',
                    level=logging.INFO)

class FakeStream:

    def __init__(self, other):
        self.other = other
        self.queue = ''

    def write(self, *args, **kwargs):
        out = args[0]
        if '\n' in out:
            lines = out.split('\n')
            if len(lines) > 1:
                logging.info(self.queue + lines[0])
                for l in lines[1:-1]:
                    logging.info(l)
                self.queue = lines[-1] or ''
            else:
                logging.info(self.queue + out)
                self.queue = ''
        else:
            self.queue += out
        return self.other.write(*args, **kwargs)

    def flush(self, *args, **kwargs):
        return self.other.flush(*args, **kwargs)

    def fileno(self, *args, **kwargs):
        return self.other.fileno(*args, **kwargs)

    def getattr(self, *args, **kwargs):
        return self.other.getattr(*args, **kwargs)

def log_streams(f):
    @functools.wraps(f)
    def newf(*args, **kwargs):
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = FakeStream(sys.stdout)
        sys.stderr = FakeStream(sys.stderr)
        try:
            return f(*args, **kwargs)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
    return newf

def logged_task(f):
    return task(log_streams(f))

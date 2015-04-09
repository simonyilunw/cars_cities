import logging
log = logging.getLogger(__name__)

import os
import errno
import cPickle as pickle


def ensure_dirs(filename, *args, **kwargs):
    if not os.path.exists(filename):
        # create all intermediate dirs if they don't exist
        try:
            os.makedirs(os.path.dirname(os.path.realpath(filename)))
        except OSError as exception:
            # to address rare race condition between the os.path.exists
            # and the os.makedirs calls
            if exception.errno != errno.EEXIST:
                raise


def open_safe(filename, *args, **kwargs):
    """
    Checks to see if the filename intermediate dirs exist before returning a python open() handle
    on it.

    Example:
    f = open_safe('/tmp/a/b/c/d/e', 'wb+')
    """
    if not os.path.exists(filename):
        # create all intermediate dirs if they don't exist
        try:
            os.makedirs(os.path.dirname(os.path.realpath(filename)))
        except OSError as exception:
            # to address rare race condition between the os.path.exists
            # and the os.makedirs calls
            if exception.errno != errno.EEXIST:
                raise

    return open(filename, *args, **kwargs)


def pickle_save(obj, filename):
    try:
        pickle.dump(obj, open_safe(filename, 'wb+'))
    except:
        log.exception('Exception pickle saving to %s', filename)


def pickle_load(filename):
    try:
        return pickle.load(open_safe(filename, 'rb'))
    except:
        raise
    

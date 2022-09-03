import os
import sys

from inspect import getsourcefile


def path_to(*args):
    try:
        _ = sys._MEIPASS
        base_dir = os.path.abspath(os.path.dirname(sys.executable))
    except:
        base_dir = os.path.abspath(os.path.dirname(getsourcefile(lambda: 0)))

    return os.path.join(base_dir, *args)

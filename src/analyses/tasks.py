from contextlib import contextmanager
import os


@contextmanager
def cd(newdir: str):
    """
    Context manager for changing working directory.

    Ref: http://stackoverflow.com/a/24176022

    Args:
        newdir (str): path to new working directory
    """
    prevdir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)

import sys
from fabric.api import local, task

@task
def start_db():
    if sys.platform.startswith('darwin'):
        # Mac OSX
        local('postgres -D /usr/local/var/postgres -s')

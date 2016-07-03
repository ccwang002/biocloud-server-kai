import sys
from pathlib import Path
from fabric.api import local, task, lcd, env
from fabric.contrib.console import confirm
from fabric.utils import abort

src_p = Path(env.real_fabfile).parent / 'src'


@task
def start_db():
    if sys.platform.startswith('darwin'):
        # Mac OSX
        local('postgres -D /usr/local/var/postgres -s')


@task
def start_smtp():
    local('python3 -m smtpd -n -c DebuggingServer localhost:1025')


@task
def backup():
    cmd_dumpdata = 'python manage.py dumpdata '
    with lcd(src_p.as_posix()):
        local(
            cmd_dumpdata + 'users.EmailUser data_sources.DataSource | '
            'tee ../db_dump/user_sources.json'
        )
        local(
            cmd_dumpdata + 'experiments | '
            'tee ../db_dump/experiments.json'
        )
        local(
            cmd_dumpdata + 'analyses.GenomeReference | '
            'tee ../db_dump/genome_reference.json'
        )


@task
def reborn():
    with lcd(src_p.as_posix()):
        db_dump_dir = Path(env.cwd, '../db_dump')
        if not (
            db_dump_dir.joinpath('user_sources.json').exists() and
            db_dump_dir.joinpath('genome_reference.json').exists() and
            db_dump_dir.joinpath('experiments.json').exists()
        ):
            abort('Backup the import database content first!')
        confirm('Destory and re-create the current database?', False)

        local('dropdb biocloud')
        local('createdb biocloud')
        local('python manage.py migrate')
        local('python manage.py loaddata ../db_dump/user_sources.json')
        local('python manage.py loaddata ../db_dump/genome_reference.json')
        local('python manage.py loaddata ../db_dump/experiments.json')

@task
def cloc():
    with lcd(src_p.parent.as_posix()):
        local(
            'cloc --exclude-dir=vendors,migrations,assets ./src'
        )

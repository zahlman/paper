from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from venv import create as make_venv
from zipfile import ZipFile


_paper_packages = [
    # All packages to install the first time.
    # FIXME: determine this list from the bootstrap wheels.
    ('paper_ui', '0.1.0'),
    ('rfbs', '0.1.0'),
    ('resolvelib', '1.1.0'),
    ('packaging', '25.0')
]


def _unpack(where):
    with ZipFile(str(Path(sys.argv[0]))) as me:
        for name in me.namelist():
            if name != '__main__.py':
                me.extract(name, str(where))


def _fix_sys_path(bootstrap):
    for wheel in bootstrap.iterdir():
        sys.path.insert(0, str(bootstrap / wheel))


def _copy_to_cache(bootstrap):
    from rfbs.setup import copy_distribution_into_cache
    for wheel in bootstrap.iterdir():
        try:
            copy_distribution_into_cache(wheel)
        except IOError:
            pass # keep going but don't overwrite


def _environments_path():
    return Path.home() / '.local' / 'share' / 'paper' / 'environments'


def _do_initial_install():
    from rfbs.env import ensure
    # Once `setup_from_cache` can handle updating a package already in the
    # environment, it should naturally become possible to upgrade existing
    # PAPER installations using the zipapp for a new version.
    # For now, this is likely to fail...
    from rfbs.setup import setup_from_cache
    # Use the distribution name for the Paper wheel on PyPI.
    env = _environments_path() / 'paper-ui'
    ensure(env, base_python=sys.executable)
    for name, version in _paper_packages:
        setup_from_cache(env, name, version, fetch=False)


def main():
    try:
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            _unpack(tmpdir)
            _fix_sys_path(tmpdir)
            _copy_to_cache(tmpdir)
            _do_initial_install()
        return 0
    except Exception as e:
        print(e)
        return 1


if __name__ == '__main__':
    print("Installing PAPER 0.1.0, using Python located at", sys.executable)
    sys.exit(main())

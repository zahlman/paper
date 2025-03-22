from pathlib import Path
import sys
from venv import create as make_venv
from zipfile import ZipFile


_bootstrap_wheels = [
    # Wheels whose code is needed for the initial install.
    # Most important last.
    'installer-0.7.0/installer-0.7.0-py3-none-any.whl',
    'rfbs-0.1.0/rfbs-0.1.0-py2.py3-none-any.whl',
]


_paper_packages = [
    # All packages to install the first time.
    ('paper', '0.1.0'),
    ('rfbs', '0.1.0'),
    ('installer', '0.7.0'),
    ('resolvelib', '1.1.0'),
]


def _cache_folder():
    result = Path.home() / '.cache'
    if (result / 'paper').exists():
        # Better safe than sorry, for now.
        raise IOError('Paper cache already found')
    return result


def _unpack_cache(where):
    with ZipFile(Path(sys.argv[0])) as me:
        for name in me.namelist():
            if not name.startswith('paper/'):
                continue
            me.extract(name, where)


def _fix_sys_path(paper_cache):
    for wheel in _bootstrap_wheels:
        sys.path.insert(0, str(paper_cache / wheel))


def _do_initial_install(paper_cache):
    from rfbs.setup import setup_from_cache
    from rfbs.env import create # For the zipapp, it shouldn't already exist.
    # Use the distribution name for the Paper wheel on PyPI.
    env = Path.home() / '.local' / 'share' / 'paper' / 'paper-ui'
    create(env)
    for name, version in _paper_packages:
        setup_from_cache(name, version, env, cache=paper_cache, fetch=False)


def main():
    try:
        cache_dir = _cache_folder()
        _unpack_cache(cache_dir)
        _fix_sys_path(cache_dir / 'paper')
        return _do_initial_install(cache_dir / 'paper')
    except Exception as e:
        print(e)
        return 1


if __name__ == '__main__':
    sys.exit(main())

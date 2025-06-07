from collections import namedtuple
from enum import Enum
from pathlib import Path
import subprocess, sys, venv


_my_path = Path(sys.executable).resolve()
_my_version = sys.version_info


# Is there something at this path?
# Is it a folder representing a valid Python virtual environment?
# What versions of Python does it contain?
# (The 'versions' map from interpreter path to interpreter version.)
EnvStatus = namedtuple('EnvStatus', ('exists', 'virtual', 'versions'))


class EnvError(ValueError): pass


def _version_tuple(s):
    return tuple(map(int, s.split('.')))


def _parse(info_string):
    try:
        python, version = info_string.split()
        if python != 'Python':
            return None
        return _version_tuple(version)
    except ValueError:
        return None


def _query(path):
    from subprocess import check_output, STDOUT
    try:
        # 2.x puts the version info on stderr instead.
        # In principle, although Paper must run in a 3.x env, it should
        # be able to manage 2.x envs.
        return check_output([path, '-V'], text=True, stderr=STDOUT)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return '' 


def _version(path):
    # Get the major and minor version of a Python executable.
    # When installing in a base environment, this is used to figure out
    # the subdirectory to use in site-packages, and to choose the Python
    # version for package resolution.
    # When creating a venv, this is used to rewrite pyvenv.cfg when the
    # Python exectuable is replaced.
    return _my_version if path == _my_path else _parse(_query(path))


def _name_for_version(version):
    major, minor, *_ = version
    return f'python{major}.{minor}'


def _normalize_cfg(config):
    try:
        config['version'] = _version_tuple(config['version'])
        config['home'] = Path(config['home'])
    except KeyError:
        raise ValueError
    try:
        config['executable'] = Path(config['executable'])
    except KeyError:
        # Make a best guess (needed for <= 3.10)
        name = _name_for_version(config['version'])
        config['executable'] = config['home'] / name
    config['executable'] = config['executable'].resolve()


def _parse_pyvenv_cfg(text):
    split = [l.partition('=') for l in text.splitlines()]
    if not all(_ for k, _, v in split):
        raise ValueError
    config = {k.strip(): v.strip() for k, _, v in split}
    _normalize_cfg(config)
    return config


def _get_base_pythons(bin_path):
    return {} # TODO


def _inspect(env_path):
    if not env_path.exists():
        return EnvStatus(False, False, {})
    try:
        config = _parse_pyvenv_cfg((env_path / 'pyvenv.cfg').read_text())
    except (FileNotFoundError, IsADirectoryError, ValueError):
        return EnvStatus(True, False, _get_base_pythons(env_path / 'bin'))
    return EnvStatus(True, True, {config['executable']: config['version']})


def _make(env, base):
    # TODO: use the current Python and adapt the result to the specified
    # Python (this way should support pre-3.x environments).
    # TODO: custom environment creation to facilitate relocatable venvs.
    env = str(Path(env))
    base = str(Path(base))
    if base == sys.executable: # fast path
        venv.create(env, symlinks=True)
    else:
        subprocess.call([base, '-m', 'venv', '--without-pip', env])


def _check_python(versions, base_python):
    if base_python is None:
        return
    if base_python.resolve() not in versions:
        raise EnvError("Environment exists, but doesn't include this Python")


def create(path, *, base_python=sys.executable):
    exists, virtual, versions = _inspect(Path(path))
    if exists:
        raise EnvError("Environment already exists; can't create it")
    assert not (virtual or versions)
    _make(path, base_python)


def ensure(path, *, base_python=None):
    exists, virtual, versions = _inspect(Path(path))
    if exists:
        _check_python(versions, base_python)
    else:
        if base_python is None:
            raise EnvError("Environment missing; must specify a base")
        _make(path, base_python)


def verify(path, *, base_python=None):
    exists, virtual, versions = _inspect(Path(path))
    if not exists:
        raise EnvError("Environment missing")
    _check_python(versions, base_python)

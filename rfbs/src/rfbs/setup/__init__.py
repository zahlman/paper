from pathlib import Path
from ..fetch import download
from .installer import destinations, install, sources
from .unpack import unpack_wheel
VenvDestination = destinations.SchemeDictionaryDestination
WheelFile = sources.WheelFile


def _parse_config_line(line):
    k, _, v = line.partition('=')
    return k.strip(), v.strip()


def _parse_config(path):
    with open(str(path / 'pyvenv.cfg')) as f:
        config = dict(map(_parse_config_line, f))
    home = Path(config['home'])
    try:
        interpreter = Path(config['executable'])
    except KeyError: # Make a best guess (needed for <=3.10)
        version = config['version'].split('.')
        executable_name = 'python' + '.'.join(version[:2])
        interpreter = home / executable_name
    return interpreter, home


def _compute_paths(root, interpreter, home):
    python_prefix = interpreter.parent.parent
    python_name = interpreter.name # also used as a folder name.
    # The `sysconfig` module can only tell us about the current running Python,
    # but we need to grok other venvs besides the one where Paper is installed.
    # Therefore, we reproduce its logic here.
    venv_lib = root / 'lib' / python_name
    # `installer` uses `os.path.join` on these values, which fails for Path
    # instances on 3.5. So we explicitly convert back to str.
    return {
        'stdlib': str(python_prefix / 'lib' / python_name),
        'platstdlib': str(venv_lib),
        'platlib': str(venv_lib / 'site-packages'),
        'purelib': str(venv_lib / 'site-packages'),
        'include': str(python_prefix / 'include' / python_name),
        'platinclude': str(python_prefix / 'include' / python_name),
        'scripts': str(root / 'bin'),
        'data': str(root)
    }


def _get_destination(venv_root):
    venv_root = Path(venv_root)
    interpreter, home = _parse_config(venv_root)
    paths = _compute_paths(venv_root, interpreter, home)
    # `installer` requires a string for `interpreter` to write a shebang.
    # We want to use the venv's executable (even if it's a symlink),
    # not the base one mentioned in the config file.
    return VenvDestination(paths, str(venv_root / 'bin' / 'python'), 'posix')


def setup_wheel(source_path, venv_root):
    metadata = { 'INSTALLER': b'paper 0.1.0' }
    with WheelFile.open(str(source_path)) as source:
        install(source, _get_destination(venv_root), metadata)


def _default_cache():
    # In the future, this may involve platformdirs, reading a config file etc.
    return Path.home() / '.cache' / 'paper'


def _find_distribution(where):
    # In the future this may find an sdist, or have to choose between wheels
    # according to platform info. It may also return an unpacked cache folder.
    for item in where.iterdir():
        if item.suffix == '.whl':
            return item


def _folder_for(cache, name, version):
    # Normalize distribution name.
    # This allows specifying the name as it appears on PyPI, while having
    # the cache use a normalized name.
    # This is useful since it disambiguates folder names in the cache:
    # the first hyphen must separate the name from the version.
    name = name.replace('-', '_')
    return cache / name / version


def _tags():
    # TODO
    return ('py2.py3', 'none', 'any')


def _unpacked_wheel_path(folder, tags):
    return folder / '-'.join(('wheel', *_tags()))


def _find_unpacked(folder, name, version):
    candidate = _unpacked_wheel_path(folder, _tags())
    return candidate if candidate.exists() else None


def _wheel_name(name, version, tags):
    return '-'.join((name, version, *tags)) + '.whl'


def _unpack_from_cache(folder, name, version):
    # TODO: search for appropriate wheel tags
    candidate = folder / _wheel_name(name, version, _tags())
    if not candidate.exists():
        return None
    unpack_path = _unpacked_wheel_path(folder, _tags())
    unpack_wheel(candidate, unpack_path)
    return folder / unpack_path


def _fetch_then_unpack(folder, name, version):
    download(folder, name, version, *_tags())
    return _unpack_from_cache(folder, name, version)


def _try_methods(methods, args, failure):
    results = (m(*args) for m in methods)
    successes = (r for r in results if r is not None)
    try:
        return next(successes)
    except StopIteration:
        raise ValueError(failure)


def _ensure_distribution(folder, name, version, fetch):
    if fetch:
        methods = (_find_unpacked, _unpack_from_cache, _fetch_then_unpack)
        failure = "Wheel couldn't be downloaded"
    else:
        methods = (_find_unpacked, _unpack_from_cache)
        failure = "Wheel not in cache"
    return _try_methods(methods, (folder, name, version), failure)


def _setup_unpacked(distribution, root):
    # hard-link main package files
    # copy .dist-info and .data segments (they may need to be writable)
    # make script wrappers
    # invoke `compileall` as appropriate
    ...


def setup_from_cache(root, name, version, cache=None, fetch=True):
    if cache is None:
        cache = _default_cache()
    folder = _folder_for(cache, name, version)
    distribution = _ensure_distribution(folder, name, version, fetch)
    _setup_unpacked(distribution, root)

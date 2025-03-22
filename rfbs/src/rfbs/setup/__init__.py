from pathlib import Path
from .installer import destinations, install, sources
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


def _folder_for(name, version):
    # Normalize distribution name.
    # This allows specifying the name as it appears on PyPI, while having the
    # cache use a normalized name.
    # This is useful since it disambiguates folder names in the cache:
    # the first hyphen must separate the name from the version.
    name = name.replace('-', '_')
    return '{}-{}'.format(name, version)


def setup_from_cache(name, version, venv_root, *, cache=None, fetch=True):
    if cache is None:
        cache = _default_cache()
    distribution = _find_distribution(cache / _folder_for(name, version))
    if distribution is None:
        # TODO: fetch the distribution if permitted.
        raise ValueError("couldn't find a distribution")
    setup_wheel(distribution, venv_root)

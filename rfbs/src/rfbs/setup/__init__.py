from pathlib import Path
from installer import destinations, install, sources
VenvDestination = destinations.SchemeDictionaryDestination
WheelFile = sources.WheelFile


def _parse_config_line(line):
    k, _, v = line.partition('=')
    return k.strip(), v.strip()


def _parse_config(path):
    with open(path / 'pyvenv.cfg') as f:
        config = dict(map(_parse_config_line, f))
    return Path(config['executable']), Path(config['home'])


def _compute_paths(root, interpreter, home):
    python_prefix = interpreter.parent.parent
    python_name = interpreter.name # also used as a folder name.
    # The `sysconfig` module can only tell us about the current running Python,
    # but we need to grok other venvs besides the one where Paper is installed.
    # Therefore, we reproduce its logic here.
    venv_lib = root / 'lib' / python_name
    return {
        'stdlib': python_prefix / 'lib' / python_name,
        'platstdlib': venv_lib,
        'platlib': venv_lib / 'site-packages',
        'purelib': venv_lib / 'site-packages',
        'include': python_prefix / 'include' / python_name,
        'platinclude': python_prefix / 'include' / python_name,
        'scripts': root / 'bin',
        'data': root 
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
    with WheelFile.open(source_path) as source:
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


def setup_from_cache(name, version, venv_root, *, cache=None, fetch=True):
    if cache is None:
        cache = _default_cache()
    distribution = _find_distribution(cache / f'{name}-{version}')
    if distribution is None:
        # TODO: fetch the distribution if permitted.
        raise ValueError("couldn't find a distribution")
    setup_wheel(distribution, venv_root)

from pathlib import Path
from shutil import copyfile
from ..fetch import download
from .unpack import unpack_wheel


def _copy_into(src, dst, force=False):
    dst.mkdir(parents=True, exist_ok=True)
    if (dst / src.name).exists() and not force:
        raise IOError("File already exists at destination")
    copyfile(src, dst / src.name)


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
    if cache is None:
        cache = _default_cache()
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
    folder = _folder_for(cache, name, version)
    distribution = _ensure_distribution(folder, name, version, fetch)
    _setup_unpacked(distribution, root)


def _parse_distribution_name(distribution_name):
    # Wheel and sdist names both start with the name and version.
    # sdist names have no other parts before the extension; but we need
    # to distinguish a multi-part extension from the version number.
    # We also need to do this in a 3.6-compatible manner, so no
    # .removesuffix() etc.
    if distribution_name.endswith('.tar.gz'):
        distribution_name = distribution_name[:-7]
    elif not distribution_name.endswith('.whl'):
        raise ValueError("file is not a recognized sdist or wheel")
    try:
        name, version, *_ = distribution_name.split('-')
        return name, version
    except ValueError:
        raise ValueError("file name doesn't follow convention")


# For now, wheels and sdists work the same way.
def copy_distribution_into_cache(distribution_path, cache=None, force=False):
    distribution_path = Path(distribution_path)
    distribution_name = distribution_path.name
    name, version = _parse_distribution_name(distribution_name)
    folder = _folder_for(cache, name, version)
    # Don't use hardlinks or other strategies, because the user should be able
    # to modify the source wheel independently later.
    _copy_into(distribution_path, folder, force)

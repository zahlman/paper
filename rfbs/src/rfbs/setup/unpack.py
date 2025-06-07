from pathlib import Path
from shutil import move
from tempfile import TemporaryDirectory
from zipfile import ZipFile


def _validate_item(path):
    if path.startswith('/'):
        raise ValueError("invalid absolute path found in wheel")
    if any(p in ('.', '..') for p in path.split('/')):
        raise ValueError("invalid path using '.' or '..' found in wheel")


def _validate_wheel(archive):
    badfile = archive.testzip()
    if badfile:
        raise ValueError("corrupt wheel entry {}".format(badfile))


def unpack_wheel_unsafe(src, dst):
    with ZipFile(src) as archive:
        for path in archive.namelist():
            archive.extract(path, dst)


def _unpack_wheel_safe(archive, where):
    _validate_wheel(archive)
    for path in archive.namelist():
        _validate_item(path)
        archive.extract(path, where)


def unpack_wheel(src, dst):
    with ZipFile(src) as archive, TemporaryDirectory() as td:
        _unpack_wheel_safe(archive, td)
        # If there were no errors, move to the real destination.
        # There isn't really a sane way to recover from an error in this part.
        # shutil.move will recurse, but we want to iterate one level down.
        # That will leave behind the temporary directory for the context
        # manager to clean up, and avoid an extra folder at the destination.
        for item in Path(td).iterdir():
            move(item, dst)

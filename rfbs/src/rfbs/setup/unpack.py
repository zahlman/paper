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


def unpack_wheel(src, dst, safe=True):
    with ZipFile(src) as archive:
        if safe:
            _validate_wheel(archive)
        for path in archive.namelist():
            if safe:
                _validate_item(path)
            archive.extract(path, dst)

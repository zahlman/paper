from pathlib import Path
from sys import argv, version_info
from venv import create as make_venv
from zipfile import ZipFile


root = Path.home() / '.local/paper'
here = Path(argv[0])
major, minor = version_info.major, version_info.minor
env_folder = root / 'env'
lib_folder = env_folder / f'lib/python{major}.{minor}/site-packages'
bin_folder = env_folder / 'bin'


def hardlink_tree(dst, src):
    if dst.exists(follow_symlinks=False):
        raise RuntimeError(f"destination '{dst}' unexpectedly already existed")
    if src.is_file():
        dst.hardlink_to(src)
    elif src.is_dir():
        dst.mkdir()
        for contents in src.iterdir():
            hardlink_tree(dst / contents.name, contents)
    else:
        raise RuntimeError(f"source '{src}' unexpectedly not a file or folder")


make_venv(root / 'env', symlinks=True)
with ZipFile(here) as me:
    for name in me.namelist():
        if not name.endswith('.whl'):
            continue
        me.extract(name, root / 'wheels')
        with ZipFile(root / 'wheels' / name) as wheel:
            wheel_folder = root / 'files' / name.removesuffix('.whl')
            wheel.extractall(wheel_folder)
            for folder in wheel_folder.iterdir():
                hardlink_tree(lib_folder / folder.name, folder)


# TODO: put an executable wrapper in ~/.local/paper/env/bin
# and symlink it in ~/.local/bin

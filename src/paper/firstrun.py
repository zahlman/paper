from venv import create as make_venv
from pathlib import Path
from rfbs.setup import setup_wheel
from . import main as welcome


def wheels(where):
    paths = (d / f for d, _, files in where.walk() for f in files)
    return (p for p in paths if p.suffix == '.whl')


def main():
    home = Path.home()
    welcome()
    venv_dir = home / '.local/share/paper'
    make_venv(venv_dir, symlinks=True)
    for wheel in wheels(home / '.cache' / 'paper'):
        setup_wheel(wheel, venv_dir)


if __name__ == '__main__':
    main()

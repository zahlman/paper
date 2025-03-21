from pathlib import Path
import sys
from venv import create as make_venv
from zipfile import ZipFile

# Unpack the cache/ folder from the wheel into a user cache directory,
# then find the `paper` wheel in that cache, put it on `sys.path`, and
# switch to its code.
dst = Path.home() / '.cache'
if (dst / 'paper').exists():
    # Better safe than sorry, for now.
    raise IOError('Paper cache already found')
with ZipFile(Path(sys.argv[0])) as me:
    for name in me.namelist():
        if name != '__main__.py':
            me.extract(name, dst)
wheel = dst / 'paper/paper-0.1.0/paper-0.1.0-py2.py3-none-any.whl'
sys.path.insert(0, str(wheel))
import paper
print('paper location:', paper.__file__)
paper.main()

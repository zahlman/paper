from os import PathLike, walk
from pathlib import Path
from typing import Any, Callable, List, Optional


def _visit(process_folder, process_file, src, dst, onerror):
    for path, dirs, files in walk(src, onerror=onerror):
        path = Path(path)
        dstpath = dst / (path.relative_to(src))
        dirs[:] = [d for d in dirs if process_folder(path / d, dstpath / d)]
        for f in files:
            process_file(path / f, dstpath / f)
            yield path / f


# Process a tree of files and folders (Visitor pattern).
# 
# process_folder -> an operation to perform on each folder path.
# process_file -> an operation to perform on each file path.
# source -> the source location.
# destination -> a destination.
# onerror -> per os.walk.
# 
# process_folder and process_file get passed pairs of Paths:
# a Path from the source, and a corresponding Path within the destination.
# 
# The source folder tree is walked top-down (using os.walk for maximum
# compatibility) and each encountered folder or file in turn is processed.
# If folder processing returns a falsy value, the path walking will not
# recurse into that folder.
# 
# Symbolic links are not followed; if this is needed, have the callbacks
# check for symbolic links and follow them. Per os.walk, symlinks to
# folders will be processed by process_folder.
# 
# The contents of the source directory should not be altered (the semantics
# of this are unspecified for this case). There is no check for overlap
# between source and destination folders.
# 
# Returns a list of processed files (for further processing, if needed).
def visit(
    process_folder: Callable[[Path, Path], Any],
    process_file: Callable[[Path, Path], Any],
    source: PathLike,
    destination: PathLike,
    *, onerror: Optional[Callable[[OSError], Any]]=None
) -> List[Path]:
    src, dst = Path(source), Path(destination)
    return list(_visit(process_folder, process_file, src, dst, onerror))

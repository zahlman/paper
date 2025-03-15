# The design of Paper

(These are just some rough notes for now, that will hopefully eventually turn into proper documentation while also guiding the development process. I'm including this in the public repository so that any onlookers will know what to expect.)

## Scope

Paper is generally intended to replace the most common use cases of `pip`, `pipx` and `python -m venv` (or `virtualenv`), and go slightly beyond that.

Specifically, the tools included with Paper are intended to:

* create relocatable virtual environments without Pip

* include metadata in created virtual environments, such as a dependency graph and PEP 751 lockfile for what was installed, a symbolic name, a migration script (so that when relocated manually, Paper can know where it went), etc.

* resolve dependencies specified in a package while installing it

* collect a package list from a PEP 751 lock file

* collect a package list from a project's requirements or other dependency groups in `pyproject.toml`

* download packages from PyPI (specified by PyPI name and optional version), wheels or sdists, legacy or modern, for any specified platform

* install wheels and/or modern sdists (which include a `pyproject.toml` file) for the current platform, into either an existing or new virtual environment

* set up permanent or temporary virtual environments for PEP 723 scripts

Despite the lockfile-related features, Paper does *not* see itself as a "package manager" - just as `requirements.txt` files by themselves don't make Pip one.

Paper is designed as a tool for Python *users*, so that they can install applications and libraries and write simple scripts that use an isolated environment. Developers (i.e. programmers who want to create and share complex projects) require additional functionality. In principle, PEP 723 allows some kinds of multi-file projects to be distributed by directly sending a folder of Python source code to someone else; but making code available through PyPI (which can be properly installed and used as a dependency by something else) is more involved.

Paper is explictly *not* intended to:

* install packages into the system environment, nor a user directory

* expose a wheel-building command, even if it builds wheels in order to install from sdists (it delegates to `wheel` and/or `pyproject-hooks` for the front end, and does not provide a back end - although of course I recommend `bbbb` as a back end)

* support legacy sdists

* Fetch packages from other indexes (this may be supported in the future, and the design of Paper should keep the possibility open)

Nor does it provide any kind of "workflow manager" functionality, such as:

* install or manage Python versions

* help determine a project's dependencies or decide what versions to use

* automatically activate virtual environments or provide a "shell"

* bootstrap new "projects", create per-project virtual environments, or otherwise associate virtual environments with projects

* provide a per-project lock file (it creates per-*environment* lock files, which are designed to allow for reproducing that environment regardless of purpose; of course you can retrieve and reuse these)

* upload packages to PyPI (seriously, there's nothing wrong with `twine`!)

* help update or verify `pyproject.toml`

* use subcommands to create the impression of an integrated development tool

## Bootstrapping Paper

Generally speaking, Paper works from outside the environment where the packages will be installed.


## The installation process




## API



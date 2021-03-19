#!/usr/bin/env python3

"""
    developer shell
    ~~~~~~~~~~~~~~~

    Just call this file, and the magic happens ;)
"""

import argparse
import signal
import subprocess
import sys
import venv
from pathlib import Path


try:
    import ensurepip  # noqa
except ImportError as err:
    print('Error: Pip not available!')
    print(f'\n(Origin error: {err}\n')
    print('Hint: "apt-get install python3-venv"')
    raise


assert sys.version_info >= (3, 7), 'Python version is too old!'


if sys.platform == 'win32':  # wtf
    # Files under Windows, e.g.: .../.venv/Scripts/python3.exe
    BIN_NAME = 'Scripts'
    FILE_EXT = '.exe'
else:
    # Files under Linux/Mac and all other than Windows, e.g.: .../.venv/bin/python3
    BIN_NAME = 'bin'
    FILE_EXT = ''

VENV_PATH = Path('.venv')
BIN_PATH = VENV_PATH / BIN_NAME
PYTHON_PATH = BIN_PATH / f'python3{FILE_EXT}'
PIP_PATH = BIN_PATH / f'pip{FILE_EXT}'
POETRY_PATH = BIN_PATH / f'poetry{FILE_EXT}'

# script file defined in pyproject.toml as [tool.poetry.scripts]
# (Under Windows: ".exe" not added!)
PROJECT_SHELL_SCRIPT = BIN_PATH / 'devshell'


def _subprocess(subprocess_func, popenargs):
    popenargs = [str(arg) for arg in popenargs]  # e.g.: Path() -> str for python 3.7
    print(f'\n\n+ {" ".join(popenargs)}\n')
    subprocess_func(popenargs)


def verbose_check_call(*popenargs):
    _subprocess(subprocess.check_call, popenargs)


def verbose_call(*popenargs):
    _subprocess(subprocess.call, popenargs)


def noop_signal_handler(signal_num, frame):
    """
    Signal handler that does nothing: Used to ignore "Ctrl-C" signals
    """
    pass


if __name__ == '__main__':
    if '--update' in sys.argv or '--help' in sys.argv:
        parser = argparse.ArgumentParser(
            prog=Path(__file__).name,
            description='Developer shell',
            epilog='...live long and prosper...'
        )
        parser.add_argument(
            '--update', default=False, action='store_true',
            help='Force create/upgrade virtual environment'
        )
        parser.add_argument(
            'command_args',
            nargs=argparse.ZERO_OR_MORE,
            help='arguments to pass to dev-setup shell/cli',
        )
        options = parser.parse_args()
        force_update = options.update
        extra_args = sys.argv[2:]
    else:
        force_update = False
        extra_args = sys.argv[1:]

    # Create virtual env in ".../.venv/":
    if not PYTHON_PATH.is_file() or force_update:
        print('Create virtual env here:', VENV_PATH.absolute())
        builder = venv.EnvBuilder(symlinks=True, upgrade=True, with_pip=True)
        builder.create(env_dir=VENV_PATH)

    # install/update "pip" and "poetry":
    if not POETRY_PATH.is_file() or force_update:
        # Note: Under Windows pip.exe can't replace this own .exe file, so use the module way:
        verbose_check_call(PYTHON_PATH, '-m', 'pip', 'install', '-U', 'pip')
        verbose_check_call(PIP_PATH, 'install', 'poetry')

    # install / update via poetry
    if not PROJECT_SHELL_SCRIPT.is_file():
        verbose_check_call(POETRY_PATH, 'install')
    elif force_update:
        verbose_check_call(POETRY_PATH, 'update')
        print('\nUpdate done.')

    # The cmd2 shell should not abort on Ctrl-C => ignore "Interrupt from keyboard" signal:
    signal.signal(signal.SIGINT, noop_signal_handler)

    # Run project cmd shell via "setup.py" entrypoint:
    # (Call it via python, because Windows sucks calling the file direct)
    verbose_call(PYTHON_PATH, PROJECT_SHELL_SCRIPT, *extra_args)

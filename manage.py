#!/usr/bin/env python3

"""
    bootstrap CLI
    ~~~~~~~~~~~~~

    Just call this file, and the magic happens ;)
"""

import hashlib
import os
import shlex
import signal
import subprocess
import sys
import venv
from pathlib import Path


def print_no_pip_error():
    print('Error: Pip not available!')
    print('Hint: "apt-get install python3-venv"\n')


try:
    from ensurepip import version
except ModuleNotFoundError as err:
    print(err)
    print('-' * 100)
    print_no_pip_error()
    raise
else:
    if not version():
        print_no_pip_error()
        sys.exit(-1)


assert sys.version_info >= (3, 11), f'Python version {sys.version_info} is too old!'


if sys.platform == 'win32':  # wtf
    # Files under Windows, e.g.: .../.venv/Scripts/python.exe
    BIN_NAME = 'Scripts'
    FILE_EXT = '.exe'
else:
    # Files under Linux/Mac and all other than Windows, e.g.: .../.venv/bin/python3
    BIN_NAME = 'bin'
    FILE_EXT = ''

BASE_PATH = Path(__file__).parent
VENV_PATH = BASE_PATH / '.venv'
BIN_PATH = VENV_PATH / BIN_NAME
PYTHON_PATH = BIN_PATH / f'python3{FILE_EXT}'
PIP_PATH = BIN_PATH / f'pip{FILE_EXT}'
UV_PATH = BIN_PATH / f'uv{FILE_EXT}'

DEP_LOCK_PATH = BASE_PATH / 'uv.lock'
DEP_HASH_PATH = VENV_PATH / '.dep_hash'

# script file defined in pyproject.toml as [console_scripts]
# (Under Windows: ".exe" not added!)
PROJECT_SHELL_SCRIPT = BIN_PATH / 'reversion_compare_project'


def get_dep_hash():
    """Get SHA512 hash from lock file content."""
    return hashlib.sha512(DEP_LOCK_PATH.read_bytes()).hexdigest()


def store_dep_hash():
    """Generate .venv/.dep_hash"""
    DEP_HASH_PATH.write_text(get_dep_hash())


def venv_up2date():
    """Is existing .venv is up-to-date?"""
    if DEP_HASH_PATH.is_file():
        return DEP_HASH_PATH.read_text() == get_dep_hash()
    return False


def verbose_check_call(*popen_args):
    print(f'\n+ {shlex.join(str(arg) for arg in popen_args)}\n')
    return subprocess.check_call(popen_args)


def noop_sigint_handler(signal_num, frame):
    """
    Don't exist cmd2 shell on "Interrupt from keyboard"
    e.g.: User stops the dev. server by CONTROL-C
    """


def main(argv):
    assert DEP_LOCK_PATH.is_file(), f'File not found: "{DEP_LOCK_PATH}" !'

    # Create virtual env in ".venv/":
    if not PYTHON_PATH.is_file():
        print(f'Create virtual env here: {VENV_PATH.absolute()}')
        builder = venv.EnvBuilder(symlinks=True, upgrade=True, with_pip=True)
        builder.create(env_dir=VENV_PATH)

    # Set environment variable for uv to use '.venv-app' as project environment:
    os.environ['UV_PROJECT_ENVIRONMENT'] = str(VENV_PATH.absolute())

    if not PROJECT_SHELL_SCRIPT.is_file() or not venv_up2date():
        # Update pip
        verbose_check_call(PYTHON_PATH, '-m', 'pip', 'install', '-U', 'pip')

        # Install uv
        verbose_check_call(PYTHON_PATH, '-m', 'pip', 'install', '-U', 'uv')

        # install requirements
        verbose_check_call(UV_PATH, 'sync', '--frozen')

        # install project
        verbose_check_call(PIP_PATH, 'install', '--no-deps', '-e', '.')

        # Activate git pre-commit hooks:
        verbose_check_call(PYTHON_PATH, '-m', 'pre_commit', 'install')

        store_dep_hash()

    signal.signal(signal.SIGINT, noop_sigint_handler)  # ignore "Interrupt from keyboard" signals

    # Call our entry point CLI:
    try:
        verbose_check_call(PROJECT_SHELL_SCRIPT, *argv[1:])
    except subprocess.CalledProcessError as err:
        sys.exit(err.returncode)
    except KeyboardInterrupt:
        print('Bye!')
        sys.exit(130)


if __name__ == '__main__':
    main(sys.argv)

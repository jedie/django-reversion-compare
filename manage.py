#!/usr/bin/env python3

"""
`./dev-cli.py` is a development bootstrap script and CLI entry point.
Just call this file, and the magic happens ;)

The `uv` tool is required to run the development CLI.

e.g.: Install `uv` via `pipx`
    apt-get install pipx
    pipx install uv
"""

import os
import shlex
import shutil
import signal
import subprocess
import sys
from pathlib import Path


assert sys.version_info >= (3, 12), f'Python version {sys.version_info} is too old!'

BASE_PATH = Path(__file__).resolve().parent

# Create and use  "/.venv/" for virtualenv:
VIRTUAL_ENV = str(BASE_PATH / '.venv')


# script name defined in pyproject.toml as [console_scripts]
PROJECT_SHELL_SCRIPT = 'reversion_compare_project'


def print_uv_error_and_exit():
    print('\nError: "uv" command not found in PATH. Please install "uv" first!\n')
    print('Hint:')
    print('\tapt-get install pipx\n')
    print('\tpipx install uv\n')
    sys.exit(1)


def verbose_check_call(*popen_args):
    print(f'\n+ {shlex.join(str(arg) for arg in popen_args)}\n')

    env = {
        'VIRTUAL_ENV': VIRTUAL_ENV,
        'UV_VENV': VIRTUAL_ENV,
        **os.environ,
    }
    for key, value in env.items():
        if 'ENV' in key:
            print(f'{key}={value}')
    return subprocess.check_call(
        popen_args,
        env=env,
        cwd=Path(__file__).parent,  # Needed if called from other working directory
    )


def noop_sigint_handler(signal_num, frame):
    """
    Don't exist cmd2 shell on "Interrupt from keyboard"
    e.g.: User stops the dev. server by CONTROL-C
    """


def main(argv):
    uv_bin = shutil.which('uv')  # Ensure 'uv' is available in PATH
    if not uv_bin:
        print_uv_error_and_exit()

    if not Path(VIRTUAL_ENV).is_dir():
        verbose_check_call(uv_bin, 'venv', VIRTUAL_ENV)

        # Activate git pre-commit hooks:
        verbose_check_call(uv_bin, 'run', '--active', '-m', 'pre_commit', 'install')

    signal.signal(signal.SIGINT, noop_sigint_handler)  # ignore "Interrupt from keyboard" signals

    # Call our entry point CLI:
    try:
        verbose_check_call(uv_bin, 'run', '--active', '-m', PROJECT_SHELL_SCRIPT, *argv[1:])
    except subprocess.CalledProcessError as err:
        sys.exit(err.returncode)
    except KeyboardInterrupt:
        print('Bye!')
        sys.exit(130)


if __name__ == '__main__':
    main(sys.argv)

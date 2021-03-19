import sys
from pathlib import Path

import cmd2
from creole.setup_utils import assert_rst_readme, update_rst_readme
from dev_shell.base_cmd2_app import DevShellBaseApp
from dev_shell.command_sets import DevShellBaseCommandSet
from dev_shell.command_sets.dev_shell_commands import DevShellCommandSet as OriginDevShellCommandSet
from dev_shell.command_sets.dev_shell_commands import run_linters
from dev_shell.config import DevShellConfig
from dev_shell.utils.subprocess_utils import verbose_check_call
from poetry_publish.publish import poetry_publish

import reversion_compare


PACKAGE_ROOT = Path(reversion_compare.__file__).parent.parent


def call_manage_py(*args):
    verbose_check_call('python3', '-m', 'reversion_compare_tests.manage', *args)


@cmd2.with_default_category('django-revision-compare commands')
class ReversionCompareCommandSet(DevShellBaseCommandSet):
    def do_manage(self, statement: cmd2.Statement):
        """
        Call django-revision-compare test "manage.py"
        """
        call_manage_py(*statement.arg_list)

    def do_run_testserver(self, statement: cmd2.Statement):
        """
        Start Django dev server with the test project
        """
        # Start the "[tool.poetry.scripts]" script via subprocess
        # This works good with django dev server reloads
        verbose_check_call('run_testserver', *statement.arg_list)

    def do_makemessages(self, statement: cmd2.Statement):
        """
        Make and compile locales message files
        """
        call_manage_py(
            'makemessages',
            '--all',
            '--no-location', '--no-obsolete',
            '--ignore=htmlcov', '--ignore=.*'
        )
        call_manage_py(
            'compilemessages',
            '--ignore=htmlcov', '--ignore=.*'
        )

    def do_update_rst_readme(self, statement: cmd2.Statement):
        """
        update README.rst from README.creole
        """
        update_rst_readme(
            package_root=PACKAGE_ROOT,
            filename='README.creole'
        )


class DevShellCommandSet(OriginDevShellCommandSet):

    # TODO:
    # pyupgrade --exit-zero-even-if-changed --py3-plus --py36-plus --py37-plus --py38-plus
    # `find . -name "*.py" -type f ! -path "./.tox/*" ! -path "./htmlcov/*" ! -path "*/volumes/*"

    def do_publish(self, statement: cmd2.Statement):
        """
        Publish "dev-shell" to PyPi
        """
        # don't publish if README is not up-to-date:
        assert_rst_readme(package_root=PACKAGE_ROOT, filename='README.creole')

        # don't publish if code style wrong:
        run_linters()

        # don't publish if test fails:
        verbose_check_call('pytest', '-x')

        poetry_publish(
            package_root=PACKAGE_ROOT,
            version=reversion_compare.__version__,
            creole_readme=True  # don't publish if README.rst is not up-to-date
        )


class DevShellApp(DevShellBaseApp):
    pass


def get_devshell_app_kwargs():
    """
    Generate the kwargs for the cmd2 App.
    (Separated because we needs the same kwargs in tests)
    """
    config = DevShellConfig(package_module=reversion_compare)

    # initialize all CommandSet() with context:
    kwargs = dict(
        config=config
    )

    app_kwargs = dict(
        config=config,
        command_sets=[
            ReversionCompareCommandSet(**kwargs),
            DevShellCommandSet(**kwargs),
        ]
    )
    return app_kwargs


def devshell_cmdloop():
    """
    Entry point to start the "dev-shell" cmd2 app.
    Used in: [tool.poetry.scripts]
    """
    c = DevShellApp(**get_devshell_app_kwargs())
    sys.exit(c.cmdloop())

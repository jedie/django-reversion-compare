"""
    Allow reversion_compare to be executable
    through `python -m reversion_compare`.
"""
from manage_django_project.manage import execute_django_from_command_line


def main():
    """
    entrypoint installed via pyproject.toml and [project.scripts] section.
    Must be set in ./manage.py and PROJECT_SHELL_SCRIPT
    """
    execute_django_from_command_line()


if __name__ == '__main__':
    main()

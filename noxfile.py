#
# https://github.com/wntrblm/nox/
# Documentation: https://nox.thea.codes/
#
import nox
from nox.sessions import Session


PYTHON_VERSIONS = ('3.14', '3.13', '3.12')
DJANGO_VERSIONS = ('6.0', '5.2')


@nox.session(
    python=PYTHON_VERSIONS,
    venv_backend='uv',
    download_python='auto',
)
@nox.parametrize('django', DJANGO_VERSIONS)
def tests(session: Session, django: str):
    session.install('uv')
    session.run(
        'uv',
        'sync',
        '--all-extras',
        '--python',
        session.python,
        env={'UV_PROJECT_ENVIRONMENT': session.virtualenv.location},
    )
    session.run(
        'uv',
        'pip',
        'install',
        f'django>={django},<={django}.999',
        env={'UV_PROJECT_ENVIRONMENT': session.virtualenv.location},
    )
    session.run('python', '-m', 'coverage', 'run', '--context', f'py{session.python}-django{django}')

import nox
from nox.sessions import Session


PYTHON_VERSIONS = ['3.13', '3.12', '3.11']
DJANGO_VERSIONS = ['5.2', '5.1', '4.2']


@nox.session(python=PYTHON_VERSIONS)
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

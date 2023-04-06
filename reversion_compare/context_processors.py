from reversion_compare import __version__


def reversion_compare_version_string(request):
    return {"version_string": f"v{__version__}"}

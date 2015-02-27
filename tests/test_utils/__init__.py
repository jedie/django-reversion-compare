import shutil


def cleanup_temp(temp_dir):
    print("\nCleanup %r: " % temp_dir, end="")
    try:
        shutil.rmtree(temp_dir)
    except (OSError, IOError) as err:
        print("Error: %s" % err)
    else:
        print("OK")
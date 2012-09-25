import os


def iter_filenames(paths):
    '''Recursively iter filenames starting from the given *paths*.
    Filenames are filtered and only Python files (those ending with .py) are
    yielded.
    '''
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for filename in (f for f in files if f.endswith('.py')):
                    yield os.path.join(root, filename)
        else:
            yield path

import os
import operator
import itertools
from functools import reduce
from pathfinder import find_paths, FnmatchFilter, NotFilter, FileFilter


def iter_filenames(paths, exclude=None):
    finder = lambda path: build_finder(path, build_filter(exclude))
    return itertools.chain(*map(finder, paths))


def build_finder(path, filter):
    if os.path.isfile(path):
        return (path,)
    return find_paths(path, filter=filter)


def build_filter(exclude=None):
    excluded = [FnmatchFilter(e) for e in (exclude or '').split(',') if e]
    f = FileFilter() & FnmatchFilter('*.py')
    if excluded:
        f &= NotFilter(
                reduce(operator.or_, excluded[1:], excluded[0])
             )
    return f

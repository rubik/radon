import os
import operator
import itertools
from functools import reduce
from pathfinder import find_paths, FnmatchFilter, NotFilter, FileFilter
from radon.visitors import Function
from radon.complexity import cc_rank


def iter_filenames(paths, exclude=None):
    '''A generator that yields all sub-paths of the ones specified in `paths`.
    Optional exclude filters can be passed as a comma-separated string of
    fnmatch patterns.'''
    finder = lambda path: build_finder(path, build_filter(exclude))
    return itertools.chain(*map(finder, paths))


def build_finder(path, filter):
    '''Construct a path finder for the specified `path` and with the specified
    `filter`. Hidden directories are ignored by default.'''
    if os.path.isfile(path):
        return (path,)
    return find_paths(path, filter=filter, ignore=FnmatchFilter('*/.*'))


def build_filter(exclude=None):
    '''Construct a filter from a comma-separated string of fnmatch patterns.'''
    excluded = [FnmatchFilter(e) for e in (exclude or '').split(',') if e]
    f = FileFilter() & FnmatchFilter('*.py')
    if excluded:
        f &= NotFilter(
                reduce(operator.or_, excluded[1:], excluded[0])
             )
    return f


def cc_to_dict(obj):
    '''Convert a list of results into a dictionary. This is meant for JSON
    dumping.'''
    def get_type(obj):
        if isinstance(obj, Function):
            return 'method' if obj.is_method else 'function'
        return 'class'

    result = {
        'type': get_type(obj),
        'rank': cc_rank(obj.complexity),
    }
    attrs = set(Function._fields) - set(('is_method', 'clojures'))
    for a in attrs:
        v = getattr(obj, a, None)
        if v is not None:
            result[a] = v
    for key in ('methods', 'clojures'):
        if hasattr(obj, key):
            result[key] = map(cc_to_dict, getattr(obj, key))
    return result


def _filter_by_rank(results, min, max):
    '''Yield results whose rank is between `min` and `max`.'''
    for result in results:
        if min <= cc_rank(result.complexity) <= max:
            yield result

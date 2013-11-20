import os
import operator
import itertools
from functools import reduce
from pathfinder import find_paths, FnmatchFilter, NotFilter, FileFilter
from radon.visitors import Function
from radon.complexity import cc_rank


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


def cc_to_dict(obj):
    def get_type(obj):
        if isinstance(obj, Function):
            return 'method' if obj.is_method else 'function'
        return 'class'

    result = {}
    result['type'] = get_type(obj)
    #TODO: Avoid hard-coding attributes
    attrs = ['name', 'lineno', 'col_offset', 'endline', 'classname',
             'complexity', 'real_complexity']
    for a in attrs:
        v = getattr(obj, a, None)
        if v is not None:
            result[a] = v
    for key in ('methods', 'clojures'):
        if hasattr(obj, key):
            result[key] = map(cc_to_dict, getattr(obj, key))
    return result


def _filter_by_rank(results, min, max):
    for result in results:
        if min <= cc_rank(result.complexity) <= max:
            yield result

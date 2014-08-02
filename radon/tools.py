import os
import operator
import itertools
import xml.etree.cElementTree as et
from functools import reduce
from radon.pathfinder import (find_paths, FnmatchFilter, NotFilter, FileFilter,
                              AlwaysAcceptFilter)
from radon.visitors import Function
from radon.complexity import cc_rank


def iter_filenames(paths, exclude=None, ignore=None):
    '''A generator that yields all sub-paths of the ones specified in `paths`.
    Optional exclude filters can be passed as a comma-separated string of
    fnmatch patterns.
    If paths contains only a single hyphen, stdin is implied, return as is.'''
    if set(paths) == set(('-',)):
        return paths
    finder = lambda path: build_finder(path, build_filter(exclude),
                                       build_ignore(ignore))
    return itertools.chain(*list(map(finder, paths)))


def build_finder(path, filter, ignore):
    '''Construct a path finder for the specified `path` and with the specified
    `filter`. Hidden directories are ignored by default.'''
    if os.path.isfile(path):
        return (path,)
    return find_paths(path, filter=filter, ignore=ignore)


def build_filter(exclude):
    '''Construct a filter from a comma-separated string of fnmatch patterns.'''
    return build_custom(exclude, FileFilter() & FnmatchFilter('*.py'),
                        NotFilter)


def build_ignore(ignore):
    '''Construct an ignore filter from a comma-separated string of fnmatch
    patterns.'''
    return build_custom(ignore, None, add=[FnmatchFilter('*/.*')])


def build_custom(pattern, start=None, final=lambda x: x, op=operator.or_,
                 add=None):
    patt = ([FnmatchFilter(p) for p in (pattern or '').split(',') if p] +
            (add or []))
    start = start or AlwaysAcceptFilter()
    if patt:
        start &= final(
            reduce(op, patt[1:], patt[0])
        )
    return start


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
            result[key] = list(map(cc_to_dict, getattr(obj, key)))
    return result


def raw_to_dict(obj):
    '''Convert a list of results into a dictionary. This is meant for JSON
    dumping.'''
    result = {}
    for a in obj._fields:
        v = getattr(obj, a, None)
        if v is not None:
            result[a] = v
    return result


def dict_to_xml(results):
    '''Convert a dictionary holding analysis result into a string containing
    xml.'''
    ccm = et.Element('ccm')
    for filename, blocks in results.items():
        for block in blocks:
            metric = et.SubElement(ccm, 'metric')
            complexity = et.SubElement(metric, 'complexity')
            complexity.text = str(block['complexity'])
            unit = et.SubElement(metric, 'unit')
            name = block['name']
            if 'classname' in block:
                name = '{0}.{1}'.format(block['classname'], block['name'])
            unit.text = name
            classification = et.SubElement(metric, 'classification')
            classification.text = block['rank']
            file = et.SubElement(metric, 'file')
            file.text = filename
    return et.tostring(ccm).decode('utf-8')

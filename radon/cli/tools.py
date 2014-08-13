import os
import re
import sys
import fnmatch
import xml.etree.cElementTree as et
from contextlib import contextmanager
from radon.visitors import Function
from radon.complexity import cc_rank
from radon.cli.colors import (LETTERS_COLORS, RANKS_COLORS, TEMPLATE, BRIGHT,
                              RESET)


@contextmanager
def _open(path):
    '''Mock of the built-in `open()` function. Can read stdin.

    :param path <str>: file path to open ('-' for stdin)
    :returns file: open file object
    '''
    if path == '-':
        yield sys.stdin
    else:
        with open(path) as f:
            yield f


def iter_filenames(paths, exclude=None, ignore=None):
    '''A generator that yields all sub-paths of the ones specified in
    `paths`. Optional exclude filters can be passed as a comma-separated
    string of regexes, while ignore filters are a comma-separated list of
    directory names to ignore. If paths contains only a single hyphen,
    stdin is implied, return as is.
    '''
    if set(paths) == set(('-',)):
        yield '-'
        return
    for path in paths:
        if os.path.isfile(path):
            yield path
            continue
        for filename in explore_directories(path, exclude, ignore):
            yield filename


def explore_directories(start, exclude, ignore):
    exclude = (exclude or '').split(',')
    ignore = '.*,{0}'.format(ignore).split(',') if ignore else ['.*']
    if not exclude[0]:
        exclude = []
    for root, dirs, files in os.walk(start):
        dirs[:] = list(filter_ignores(dirs, ignore))
        for filename in filter_out(root, files, exclude):
            if (not os.path.basename(filename).startswith('.') and
                    filename.endswith('.py')):
                yield filename


def filter_ignores(dirs, ignore):
    for dir in dirs:
        if all(not fnmatch.fnmatch(dir, i) for i in ignore):
            yield dir


def filter_out(root, paths, exclude):
    for path in paths:
        fullpath = os.path.normpath(os.path.join(root, path))
        if all(re.match(e, fullpath) is None for e in exclude):
            yield fullpath


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
            result[a] = int(v)
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


def cc_to_terminal(path, results, show_complexity, min, max, total_average):
    '''Print Cyclomatic Complexity results.

    :param path: the path of the module that has been analyzed
    :param show_complexity: if True, show the complexity score in addition to
        the complexity rank.
    '''
    res = []
    counted = 0
    average_cc = .0
    for line in results:
        ranked = cc_rank(line.complexity)
        if min <= ranked <= max:
            average_cc += line.complexity
            counted += 1
            res.append(_format_line(line, ranked, show_complexity))
        elif total_average:
            average_cc += line.complexity
            counted += 1
    return res, average_cc, counted


def _format_line(line, ranked, show_complexity=False):
    '''Format a single line. *ranked* is the rank given by the
    `~radon.complexity.rank` function. If *show_complexity* is True, then
    the complexity score is added.
    '''
    letter_colored = LETTERS_COLORS[line.letter] + line.letter
    rank_colored = RANKS_COLORS[ranked] + ranked
    compl = '' if not show_complexity else ' ({0}) '.format(line.complexity)
    return TEMPLATE.format(BRIGHT, letter_colored, line.lineno,
                           line.col_offset, line.fullname, rank_colored,
                           compl, reset=RESET)

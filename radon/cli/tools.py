'''This module contains various utility functions used in the CLI interface.'''

import hashlib
import os
import re
import sys
import json
import fnmatch
import xml.etree.cElementTree as et
from contextlib import contextmanager
from radon.visitors import Function
from radon.complexity import cc_rank
from radon.cli.colors import (LETTERS_COLORS, RANKS_COLORS, TEMPLATE, BRIGHT,
                              RESET)


@contextmanager
def _open(path):
    '''Mock of the built-in `open()` function. If `path` is `-` then
    `sys.stdin` is returned.
    '''
    if path == '-':
        yield sys.stdin
    else:
        with open(path) as f:
            yield f


def iter_filenames(paths, exclude=None, ignore=None):
    '''A generator that yields all sub-paths of the ones specified in
    `paths`. Optional `exclude` filters can be passed as a comma-separated
    string of regexes, while `ignore` filters are a comma-separated list of
    directory names to ignore. Ignore patterns are can be plain names or glob
    patterns. If paths contains only a single hyphen, stdin is implied,
    returned as is.
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
    '''Explore files and directories under `start`. `explore` and `ignore`
    arguments are the same as in :func:`iter_filenames`.
    '''
    e = '*[!p][!y]'
    exclude = '{0},{1}'.format(e, exclude).split(',') if exclude else [e]
    ignore = '.*,{0}'.format(ignore).split(',') if ignore else ['.*']
    for root, dirs, files in os.walk(start):
        dirs[:] = list(filter_out(dirs, ignore))
        fullpaths = (os.path.normpath(os.path.join(root, p)) for p in files)
        for filename in filter_out(fullpaths, exclude):
            if (not os.path.basename(filename).startswith('.') and
                    filename.endswith('.py')):
                yield filename


def filter_out(strings, patterns):
    '''Filter out any string that matches any of the specified patterns.'''
    for s in strings:
        if all(not fnmatch.fnmatch(s, p) for p in patterns):
            yield s


def cc_to_dict(obj):
    '''Convert an object holding CC results into a dictionary. This is meant
    for JSON dumping.'''
    def get_type(obj):
        '''The object can be of type *method*, *function* or *class*.'''
        if isinstance(obj, Function):
            return 'method' if obj.is_method else 'function'
        return 'class'

    result = {
        'type': get_type(obj),
        'rank': cc_rank(obj.complexity),
    }
    attrs = set(Function._fields) - set(('is_method', 'closures'))
    for a in attrs:
        v = getattr(obj, a, None)
        if v is not None:
            result[a] = v
    for key in ('methods', 'closures'):
        if hasattr(obj, key):
            result[key] = list(map(cc_to_dict, getattr(obj, key)))
    return result


def raw_to_dict(obj):
    '''Convert an object holding raw analysis results into a dictionary. This
    is meant for JSON dumping.'''
    result = {}
    for a in obj._fields:
        v = getattr(obj, a, None)
        if v is not None:
            result[a] = v
    return result


def dict_to_xml(results):
    '''Convert a dictionary holding CC analysis result into a string containing
    xml.'''
    ccm = et.Element('ccm')
    for filename, blocks in results.items():
        for block in blocks:
            metric = et.SubElement(ccm, 'metric')
            et.SubElement(metric, 'complexity').text = str(block['complexity'])

            unit = et.SubElement(metric, 'unit')
            name = block['name']
            if 'classname' in block:
                name = '{0}.{1}'.format(block['classname'], block['name'])
            unit.text = name

            et.SubElement(metric, 'classification').text = block['rank']
            et.SubElement(metric, 'file').text = filename
            et.SubElement(metric, 'startLineNumber').text = \
                str(block['lineno'])
            et.SubElement(metric, 'endLineNumber').text = str(block['endline'])
    return et.tostring(ccm).decode('utf-8')


def dict_to_codeclimate_issues(results, threshold='B'):
    '''Convert a dictionary holding CC analysis results into Code Climate
     issue json.'''
    codeclimate_issues = []
    content = get_content()
    error_content = 'We encountered an error attempting to analyze this line.'

    for path in results:
        info = results[path]
        if type(info) is dict and info.get('error'):
            description = 'Error: {0}'.format(info.get('error', error_content))
            beginline = re.search(r'\d+', description)
            error_category = 'Bug Risk'

            if beginline:
                beginline = int(beginline.group())
            else:
                beginline = 1

            endline = beginline
            remediation_points = 1000000
            fingerprint = get_fingerprint(path, ['error'])
            codeclimate_issues.append(
                format_cc_issue(path, description, error_content,
                                error_category, beginline, endline,
                                remediation_points, fingerprint))
        else:
            for offender in info:
                beginline = offender['lineno']
                endline = offender['endline']
                complexity = offender['complexity']
                category = 'Complexity'
                description = ('Cyclomatic complexity is too high in {0} {1}. '
                               '({2})'.format(offender['type'],
                                              offender['name'],
                                              complexity))
                remediation_points = get_remediation_points(
                    complexity, threshold)
                fingerprint = get_fingerprint(path, [offender['type'],
                                                     offender['name']])

                if remediation_points > 0:
                    codeclimate_issues.append(
                        format_cc_issue(path, description, content, category,
                                        beginline, endline,
                                        remediation_points, fingerprint))
    return codeclimate_issues


def cc_to_terminal(results, show_complexity, min, max, total_average):
    '''Transfom Cyclomatic Complexity results into a 3-elements tuple:

        ``(res, total_cc, counted)``

    `res` is a list holding strings that are specifically formatted to be
    printed to a terminal.
    `total_cc` is a number representing the total analyzed cyclomatic
    complexity.
    `counted` holds the number of the analyzed blocks.

    If *show_complexity* is `True`, then the complexity of a block will be
    shown in the terminal line alongside its rank.
    *min* and *max* are used to control which blocks are shown in the resulting
    list. A block is formatted only if its rank is `min <= rank <= max`.
    If *total_average* is `True`, the `total_cc` and `counted` count every
    block, regardless of the fact that they are formatted in `res` or not.
    '''
    res = []
    counted = 0
    total_cc = .0
    for line in results:
        ranked = cc_rank(line.complexity)
        if min <= ranked <= max:
            total_cc += line.complexity
            counted += 1
            res.append(_format_line(line, ranked, show_complexity))
        elif total_average:
            total_cc += line.complexity
            counted += 1
    return res, total_cc, counted


def _format_line(block, ranked, show_complexity=False):
    '''Format a single block as a line.

    *ranked* is the rank given by the `~radon.complexity.rank` function. If
    *show_complexity* is True, then the complexity score is added alongside.
    '''
    letter_colored = LETTERS_COLORS[block.letter] + block.letter
    rank_colored = RANKS_COLORS[ranked] + ranked
    compl = '' if not show_complexity else ' ({0})'.format(block.complexity)
    return TEMPLATE.format(BRIGHT, letter_colored, block.lineno,
                           block.col_offset, block.fullname, rank_colored,
                           compl, reset=RESET)


def format_cc_issue(path, description, content, category, beginline, endline,
                    remediation_points, fingerprint):
    '''Return properly formatted Code Climate issue json.'''
    issue = {
        'type': 'issue',
        'check_name': 'Complexity',
        'description': description,
        'content': {
            'body': content,
        },
        'categories': [category],
        'fingerprint': fingerprint,
        'location': {
            'path': path,
            'lines': {
                'begin': beginline,
                'end': endline,
            },
        },
        'remediation_points': remediation_points,
    }
    return json.dumps(issue)


def get_remediation_points(complexity, grade_threshold):
    '''Calculate quantity of remediation work needed to reduce complexity to grade
    threshold permitted.'''
    grade_to_max_permitted_cc = {
        'B': 5,
        'C': 10,
        'D': 20,
        'E': 30,
        'F': 40,
    }

    threshold = grade_to_max_permitted_cc.get(grade_threshold, 5)

    if complexity and complexity > threshold:
        return 1000000 + 100000 * (complexity - threshold)
    else:
        return 0


def get_content():
    '''Return explanation string for Code Climate issue document.'''
    content = ['##Cyclomatic Complexity',
               'Cyclomatic Complexity corresponds to the number of decisions '
               'a block of code contains plus 1. This number (also called '
               'McCabe number) is equal to the number of linearly independent '
               'paths through the code. This number can be used as a guide '
               'when testing conditional logic in blocks.\n',
               'Radon analyzes the AST tree of a Python program to compute '
               'Cyclomatic Complexity. Statements have the following effects '
               'on Cyclomatic Complexity:\n\n',
               '| Construct | Effect on CC | Reasoning |',
               '| --------- | ------------ | --------- |',
               '| if | +1 | An *if* statement is a single decision. |',
               '| elif| +1| The *elif* statement adds another decision. |',
               '| else| +0| The *else* statement does not cause a new '
               'decision. The decision is at the *if*. |',
               '| for| +1| There is a decision at the start of the loop. |',
               '| while| +1| There is a decision at the *while* statement. |',
               '| except| +1| Each *except* branch adds a new conditional '
               'path of execution. |',
               '| finally| +0| The finally block is unconditionally '
               'executed. |',
               '| with| +1| The *with* statement roughly corresponds to a '
               'try/except block (see PEP 343 for details). |',
               '| assert| +1| The *assert* statement internally roughly '
               'equals a conditional statement. |',
               '| Comprehension| +1| A list/set/dict comprehension of '
               'generator expression is equivalent to a for loop. |',
               '| Boolean Operator| +1| Every boolean operator (and, or) '
               'adds a decision point. |\n',
               'Source: http://radon.readthedocs.org/en/latest/intro.html']
    return '\n'.join(content)

def get_fingerprint(path, additional_parts):
    '''Return fingerprint string for Code Climate issue document.'''
    m = hashlib.md5()
    parts = [path, 'Complexity'] + additional_parts
    key = '|'.join(parts)
    m.update(key.encode('utf-8'))
    return m.hexdigest()

'''This module contains various utility functions used in the CLI interface.
Attributes:
    _encoding (str): encoding with all files will be opened. Configured by
    environment variable RADONFILESENCODING
'''

import fnmatch
import hashlib
import json
import locale
import os
import platform
import re
import sys
import xml.etree.cElementTree as et
from contextlib import contextmanager

from radon.cli.colors import (BRIGHT, LETTERS_COLORS, RANKS_COLORS, RESET,
                              TEMPLATE)
from radon.complexity import cc_rank
from radon.visitors import Function

try:
    import nbformat

    SUPPORTS_IPYNB = True
except ImportError:
    SUPPORTS_IPYNB = False

# PyPy doesn't support encoding parameter in `open()` function and works with
# UTF-8 encoding by default
if platform.python_implementation() == 'PyPy':

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


else:
    if sys.version_info[:2] >= (3, 0):
        default_encoding = 'utf-8'
    else:
        default_encoding = locale.getpreferredencoding(False)
    # Add customized file encoding to fix #86.
    # By default `open()` function uses `locale.getpreferredencoding(False)`
    # encoding (see https://docs.python.org/3/library/functions.html#open).
    # This code allows to change `open()` encoding by setting an environment
    # variable.
    _encoding = os.getenv(
        'RADONFILESENCODING', default_encoding
    )

    if sys.version_info[:2] < (2, 7):
        # This open function treats line-endings slighly differently than
        # io.open. But the latter is implemented in pure Python in version 2.6,
        # so we'll live with the differences instead of taking a hit on the
        # speed. Radon does a lot of file reading, so the difference in speed
        # is significant.
        from codecs import open as _open_function
    elif sys.version_info[:2] < (3, 0):
        from codecs import BOM_UTF8, lookup
        from io import TextIOWrapper
        from io import open as _io_open_function

        cookie_re = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)')
        blank_re = re.compile(r'^[ \t\f]*(?:[#\r\n]|$)')

        def _get_normal_name(orig_enc):
            '''Imitates get_normal_name in tokenizer.c.'''
            # Only care about the first 12 characters.
            enc = orig_enc[:12].lower().replace('_', '-')
            if enc == 'utf-8' or enc.startswith('utf-8-'):
                return 'utf-8'
            if enc in (
                'latin-1',
                'iso-8859-1',
                'iso-latin-1',
            ) or enc.startswith(('latin-1-', 'iso-8859-1-', 'iso-latin-1-')):
                return 'iso-8859-1'
            return orig_enc

        def detect_encoding(readline):
            '''
            The detect_encoding() function is used to detect the encoding that
            should be used to decode a Python source file. It requires one
            argument, readline, in the same way as the tokenize() generator.

            It will call readline a maximum of twice, and return the encoding
            used (as a string) and a list of any lines (left as bytes) it has
            read in.

            It detects the encoding from the presence of a utf-8 bom or an
            encoding cookie as specified in pep-0263. If both a bom and a
            cookie are present, but disagree, a SyntaxError will be raised. If
            the encoding cookie is an invalid charset, raise a SyntaxError.
            Note that if a utf-8 bom is found, 'utf-8-sig' is returned.

            If no encoding is specified, then the default of 'utf-8' will be
            returned.  The third argument indicates whether the encoding cookie
            was found or not.
            '''
            try:
                filename = readline.__self__.name
            except AttributeError:
                filename = None
            bom_found = False
            encoding = None
            default = 'utf-8'

            def read_or_stop():
                try:
                    return readline()
                except StopIteration:
                    return b''

            def find_cookie(line):
                try:
                    # Decode as UTF-8. Either the line is an encoding
                    # declaration, in which case it should be pure ASCII, or it
                    # must be UTF-8 per default encoding.
                    line_string = line.decode('utf-8')
                except UnicodeDecodeError:
                    msg = 'invalid or missing encoding declaration'
                    if filename is not None:
                        msg = '{} for {!r}'.format(msg, filename)
                    raise SyntaxError(msg)

                match = cookie_re.match(line_string)
                if not match:
                    return None
                encoding = _get_normal_name(match.group(1))
                try:
                    lookup(encoding)
                except LookupError:
                    # This behaviour mimics the Python interpreter
                    if filename is None:
                        msg = 'unknown encoding: ' + encoding
                    else:
                        msg = 'unknown encoding for {!r}: ' '{}'.format(
                            filename, encoding
                        )
                    raise SyntaxError(msg)

                if bom_found:
                    if encoding != 'utf-8':
                        # This behaviour mimics the Python interpreter
                        if filename is None:
                            msg = 'encoding problem: utf-8'
                        else:
                            msg = 'encoding problem for ' '{!r}: utf-8'.format(
                                filename
                            )
                        raise SyntaxError(msg)
                    encoding += '-sig'
                return encoding

            first = read_or_stop()
            if first.startswith(BOM_UTF8):
                bom_found = True
                first = first[3:]
                default = 'utf-8-sig'
            if not first:
                return default, [], False

            encoding = find_cookie(first)
            if encoding:
                return encoding, [first], True
            if not blank_re.match(first):
                return default, [first], False

            second = read_or_stop()
            if not second:
                return default, [first], False

            encoding = find_cookie(second)
            if encoding:
                return encoding, [first, second], True

            return default, [first, second], False

        def _open_function(filename, encoding=None):
            '''Open a file in read only mode using the encoding detected by
            detect_encoding().
            '''
            # Note: Python 3 uses builtins.open here..
            buffer = _io_open_function(filename, 'rb')
            try:
                encoding, lines, found = detect_encoding(buffer.readline)
                # Note: Python 3's tokenize does buffer seek(0), but that
                # leaves the encoding cookie in the file and ast.parse
                # does not like Unicode text with an encoding cookie.
                # If the encoding was not found we seek to the start anyway
                if found:
                    buffer.seek(sum(len(line) for line in lines))
                else:
                    buffer.seek(0)
                text = TextIOWrapper(buffer, encoding, line_buffering=True)
                text.mode = 'r'
                return text
            except Exception:
                buffer.close()
                raise

    else:
        _open_function = open

    @contextmanager
    def _open(path):
        '''Mock of the built-in `open()` function. If `path` is `-` then
        `sys.stdin` is returned.
        '''
        if path == '-':
            yield sys.stdin
        else:
            with _open_function(path, encoding=_encoding) as f:
                yield f


def _is_python_file(filename):
    '''Check if a file is a Python source file.'''
    if (
        filename == '-'
        or filename.endswith('.py')
        or (SUPPORTS_IPYNB and filename.endswith('.ipynb'))
    ):
        return True
    try:
        with open(filename) as fobj:
            first_line = fobj.readline()
            if first_line.startswith('#!') and 'python' in first_line:
                return True
    except Exception:
        return False
    return False


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
    exclude = exclude.split(',') if exclude else []
    ignore = '.*,{0}'.format(ignore).split(',') if ignore else ['.*']
    for path in paths:
        if (
            os.path.isfile(path)
            and _is_python_file(path)
            and (
                not exclude
                or not any(fnmatch.fnmatch(path, p) for p in exclude)
            )
        ):
            yield path
            continue
        for filename in explore_directories(path, exclude, ignore):
            yield filename


def explore_directories(start, exclude, ignore):
    '''Explore files and directories under `start`. `explore` and `ignore`
    arguments are the same as in :func:`iter_filenames`.
    '''
    for root, dirs, files in os.walk(start):
        dirs[:] = list(filter_out(dirs, ignore))
        fullpaths = (os.path.normpath(os.path.join(root, p)) for p in files)
        for filename in filter_out(fullpaths, exclude):
            if not os.path.basename(filename).startswith(
                '.'
            ) and _is_python_file(filename):
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
            et.SubElement(metric, 'startLineNumber').text = str(
                block['lineno']
            )
            et.SubElement(metric, 'endLineNumber').text = str(block['endline'])
    return et.tostring(ccm).decode('utf-8')


def dict_to_md(results):
    md_string = '''
| Filename | Name | Type | Start:End Line | Complexity | Classification |
| -------- | ---- | ---- | -------------- | ---------- | -------------- |
'''
    type_letter_map = {'class': 'C',
                       'method': 'M',
                       'function': 'F'}
    for filename, blocks in results.items():
        for block in blocks:
            raw_classname = block.get("classname")
            raw_name = block.get("name")
            name = "{}.{}".format(
                raw_classname,
                raw_name) if raw_classname else block["name"]
            type = type_letter_map[block["type"]]
            md_string += "| {} | {} | {} | {}:{} | {} | {} |\n".format(
                filename,
                name,
                type,
                block["lineno"],
                block["endline"],
                block["complexity"],
                block["rank"])
    return md_string


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
                format_cc_issue(
                    path,
                    description,
                    error_content,
                    error_category,
                    beginline,
                    endline,
                    remediation_points,
                    fingerprint,
                )
            )
        else:
            for offender in info:
                beginline = offender['lineno']
                endline = offender['endline']
                complexity = offender['complexity']
                category = 'Complexity'
                description = (
                    'Cyclomatic complexity is too high in {0} {1}. '
                    '({2})'.format(
                        offender['type'], offender['name'], complexity
                    )
                )
                remediation_points = get_remediation_points(
                    complexity, threshold
                )
                fingerprint = get_fingerprint(
                    path, [offender['type'], offender['name']]
                )

                if remediation_points > 0:
                    codeclimate_issues.append(
                        format_cc_issue(
                            path,
                            description,
                            content,
                            category,
                            beginline,
                            endline,
                            remediation_points,
                            fingerprint,
                        )
                    )
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
    total_cc = 0.0
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
    return TEMPLATE.format(
        BRIGHT,
        letter_colored,
        block.lineno,
        block.col_offset,
        block.fullname,
        rank_colored,
        compl,
        reset=RESET,
    )


def format_cc_issue(
    path,
    description,
    content,
    category,
    beginline,
    endline,
    remediation_points,
    fingerprint,
):
    '''Return properly formatted Code Climate issue json.'''
    issue = {
        'type': 'issue',
        'check_name': 'Complexity',
        'description': description,
        'content': {'body': content,},
        'categories': [category],
        'fingerprint': fingerprint,
        'location': {
            'path': path,
            'lines': {'begin': beginline, 'end': endline,},
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
    content = [
        '##Cyclomatic Complexity',
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
        '| finally| +0| The finally block is unconditionally ' 'executed. |',
        '| with| +1| The *with* statement roughly corresponds to a '
        'try/except block (see PEP 343 for details). |',
        '| assert| +1| The *assert* statement internally roughly '
        'equals a conditional statement. |',
        '| Comprehension| +1| A list/set/dict comprehension of '
        'generator expression is equivalent to a for loop. |',
        '| Boolean Operator| +1| Every boolean operator (and, or) '
        'adds a decision point. |\n',
        'Source: http://radon.readthedocs.org/en/latest/intro.html',
    ]
    return '\n'.join(content)


def get_fingerprint(path, additional_parts):
    '''Return fingerprint string for Code Climate issue document.'''
    m = hashlib.md5()
    parts = [path, 'Complexity'] + additional_parts
    key = '|'.join(parts)
    m.update(key.encode('utf-8'))
    return m.hexdigest()


def strip_ipython(code):
    return '\n'.join(
        [line for line in code.split('\n') if not line.startswith('%')]
    )

try:
    import baker
except ImportError:
    raise ImportError('You need the baker module in order to use '
                      'the CLI tool')

try:
    import colorama
    colorama.init()
    GREEN, YELLOW, RED = (colorama.Fore.GREEN, colorama.Fore.YELLOW,
                          colorama.Fore.RED)
    MAGENTA, CYAN, WHITE = (colorama.Fore.MAGENTA, colorama.Fore.CYAN,
                            colorama.Fore.WHITE)
    BRIGHT, RESET = colorama.Style.BRIGHT, colorama.Style.RESET_ALL
except ImportError:
    # No colorama, so let's fallback to no-color mode
    GREEN = YELLOW = RED = MAGENTA = CYAN = WHITE = BRIGHT = RESET = ''

import os
import sys
import json as json_mod
import collections
import radon.complexity as cc_mod
from radon.tools import iter_filenames, cc_to_dict, _filter_by_rank
from radon.complexity import cc_visit, cc_rank, sorted_results
from radon.raw import analyze
from radon.metrics import mi_visit, mi_rank

if not sys.stdout.isatty():
    GREEN = YELLOW = RED = MAGENTA = CYAN = WHITE = BRIGHT = RESET = ''


RANKS_COLORS = {'A': GREEN, 'B': GREEN,
                'C': YELLOW, 'D': YELLOW,
                'E': RED, 'F': RED}

LETTERS_COLORS = {'F': MAGENTA,
                  'C': CYAN,
                  'M': WHITE}

MI_RANKS = {'A': GREEN, 'B': YELLOW, 'C': RED}

TEMPLATE = '{0}{1} {reset}{2}:{3} {4} - {5}{6}{reset}'
BAKER = baker.Baker()


def log(msg, *args, **kwargs):
    '''Log a message, passing `*args` to `.format()`.

    `indent`, if present as a keyword argument, specifies the indent level, so
    that `indent=0` will log normally, `indent=1` will indent the message by 4
    spaces, &c..
    `noformat`, if present and True, will cause the message not to be formatted
    in any way.'''
    indent = 4 * kwargs.get('indent', 0)
    m = msg if kwargs.get('noformat', False) else msg.format(*args)
    sys.stdout.write(' ' * indent + m + '\n')


def log_list(lst, **kwargs):
    '''Log an entire list, line by line.'''
    for line in lst:
        log(line, **kwargs)


def log_error(msg, *args, **kwargs):
    '''Log an error message. Arguments are the same as log().'''
    log('{0}{1}ERROR{2}: {3}'.format(BRIGHT, RED, RESET, msg), *args, **kwargs)


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


def _print_cc_results(path, results, show_complexity):
    '''Print Cyclomatic Complexity results.

    :param path: the path of the module that has been analyzed
    :param show_complexity: if True, show the complexity score in addition to
        the complexity rank
    '''
    res = []
    average_cc = .0
    for line in results:
        ranked = cc_rank(line.complexity)
        average_cc += line.complexity
        res.append(_format_line(line, ranked, show_complexity))
    if res:
        log(path)
        log_list(res, indent=1)
    return average_cc, len(results)


def analyze_cc(paths, exclude, min, max, order_function):
    '''Analyze the files located under `paths`.

    :param paths: A list of paths to analyze.
    :param exclude: A comma-separated string of fnmatch patterns.
    :param min: The minimum rank to output.
    :param max: The maximum rank to output.
    :param order_function: Can be `SCORE`, `LINES` or `ALPHA`, to sort the
        results respectively by CC score, line number or name.'''
    for name in iter_filenames(paths, exclude):
        with open(name) as fobj:
            try:
                results = sorted_results(cc_visit(fobj.read()), order_function)
                yield name, list(_filter_by_rank(results, min, max))
            except Exception as e:
                log(name, indent=1)
                log_error(e, indent=1)
                continue


@BAKER.command(shortopts={'multi': 'm', 'exclude': 'e', 'show': 's'})
def mi(multi=True, exclude=None, show=False, *paths):
    '''Analyze the given Python modules and compute the Maintainability Index.

    The maintainability index (MI) is a compound metric, with the primary aim
    being to determine how easy it will be to maintain a particular body of
    code.

    -e <str>, --exclude <str>  Comma separated list of patterns to exclude
    -m, --multi  If set, multiline strings are counted as comments
    -s, --show  If set, the actual MI value is shown in results
    paths  The modules or packages to analyze.
    '''
    for name in iter_filenames(paths, exclude):
        with open(name) as fobj:
            try:
                result = mi_visit(fobj.read(), multi)
            except Exception as e:
                log(name, indent=1)
                log_error(e, indent=1)
                continue
            except KeyboardInterrupt:
                log(name)
                return
            rank = mi_rank(result)
            color = MI_RANKS[rank]
            to_show = '' if not show else ' ({0:.2f})'.format(result)
            log('{0} - {1}{2}{3}{4}', name, color, rank, to_show, RESET)


@BAKER.command(shortopts={'min': 'n', 'max': 'x', 'show_complexity': 's',
                          'average': 'a', 'exclude': 'e', 'order': 'o',
                          'json': 'j'})
def cc(min='A', max='F', show_complexity=False, average=False,
       exclude=None, order='SCORE', json=False, *paths):
    '''Analyze the given Python modules and compute Cyclomatic
    Complexity (CC).

    The output can be filtered using the *min* and *max* flags. In addition
    to that, by default complexity score is not displayed.

    -n, --min  The minimum complexity to display (default to A).
    -x, --max  The maximum complexity to display (default to F).
    -e, --exclude  Comma separated list of patterns to exclude. By default
        hidden directories (those starting with '.') are excluded.
    -s, --show_complexity  Whether or not to show the actual complexity score
        together with the A-F rank. Default to False.
    -a, --average  If True, at the end of the analysis display the average
        complexity. Default to False.
    -o, --order  The ordering function. Can be SCORE, LINES or ALPHA.
    -j, --json  Format results in JSON.
    paths  The modules or packages to analyze.
    '''
    min = min.upper()
    max = max.upper()
    average_cc = .0
    analyzed = 0
    order_function = getattr(cc_mod, order.upper(), getattr(cc_mod, 'SCORE'))
    cc_data = analyze_cc(paths, exclude, min, max, order_function)
    if json:
        result = {}
        for key, data in cc_data:
            result[key] = map(cc_to_dict, data)
        log(json_mod.dumps(result), noformat=True)
    else:
        for name, results in cc_data:
            cc, blocks = _print_cc_results(name, results, show_complexity)
            average_cc += cc
            analyzed += blocks

    if average and analyzed:
        cc = average_cc / analyzed
        ranked_cc = cc_rank(cc)
        log('\n{0} blocks (classes, functions, methods) analyzed.', analyzed)
        log('Average complexity: {0}{1} ({2}){3}', RANKS_COLORS[ranked_cc],
            ranked_cc, cc, RESET)


@BAKER.command(shortopts={'exclude': 'e', 'summary': 's'})
def raw(exclude=None, summary=False, *paths):
    '''Analyze the given Python modules and compute raw metrics.

    Raw metrics include:

        * LOC: The number of lines of code (total)
        * LLOC: The number of logical lines of code
        * SLOC: The number of source lines of code (not necessarily
            corresponding to the LLOC)
        * comments: The number of Python comment lines
        * multi: The number of lines which represent multi-line strings
        * blank: The number of blank lines (or whitespace-only ones)

    The equation:

        sloc + blanks = loc

    should always hold.

    -e, --exclude  Comma separated list of patterns to exclude. By default
        hidden directories (those starting with '.') are excluded.
    -s, --summary  If True, at the end of the analysis display the summary
        of the gathered metrics. Default to False.
    paths: The modules or packages to analyze.
    '''
    headers = ['LOC', 'LLOC', 'SLOC', 'Comments', 'Multi', 'Blank']
    sum_metrics = collections.defaultdict(int, zip(headers, [0] * 6))

    for path in iter_filenames(paths, exclude):
        with open(path) as fobj:
            log(path)
            try:
                mod = analyze(fobj.read())
            except Exception as e:
                log_error(e, indent=1)
                continue
            for header, value in zip(headers, mod):
                log('{0}: {1}', header, value, indent=1)
                sum_metrics[header] = sum_metrics[header] + value
            if not mod.loc:
                continue
            log('- Comment Stats', indent=1)
            comments = mod.comments
            log('(C % L): {0:.0%}', comments / (float(mod.loc) or 1), indent=2)
            log('(C % S): {0:.0%}', comments / (float(mod.sloc) or 1), indent=2)
            log('(C + M % L): {0:.0%}', (comments + mod.multi) / float(mod.loc),
                indent=2)

    if summary:
        log('** Total **')
        for header in sum_metrics:
            log('{0}: {1}', header, sum_metrics[header], indent=1)

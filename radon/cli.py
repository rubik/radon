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
import fnmatch
import radon.complexity as cc_mod
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
    '''Log a message, passing `*args` and `**kwargs` to `.format()`.'''
    sys.stdout.write(msg.format(*args, **kwargs) + '\n')


def log_list(lst):
    '''Log an entire list, line by line.'''
    for line in lst:
        log(line)


def walk_paths(paths):
    '''Recursively iter filenames starting from the given *paths*.
    Filenames are filtered and only Python files (those ending with .py) are
    yielded.
    '''
    for path in paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for filename in (f for f in files if f.endswith('.py')):
                    yield os.path.join(root, filename)
        elif path.endswith('.py'):
            yield path


def iter_filenames(paths, exclude):
    exclude = filter(None, (exclude or '').split(','))
    for path in walk_paths(paths):
        if all(not fnmatch.fnmatch(path, pattern) for pattern in exclude):
            yield path


def _format_line(line, ranked, show_complexity=False):
    '''Format a single line. *ranked* is the rank given by the
    `~radon.complexity.rank` function. If *show_complexity* is True, then
    the complexity score is added.
    '''
    letter_colored = LETTERS_COLORS[line.letter] + line.letter
    rank_colored = RANKS_COLORS[ranked] + ranked
    compl = ' ({0}) '.format(line.complexity) if show_complexity else ''
    return TEMPLATE.format(BRIGHT, letter_colored, line.lineno,
                           line.col_offset, line.fullname, rank_colored,
                           compl, reset=RESET)


def _print_cc_results(path, results, min, max, show_complexity):
    '''Print Cyclomatic Complexity results.

    :param path: the path of the module that has been analyzed
    :param min: the minimum complexity rank to show
    :param max: the maximum complexity rank to show
    :param show_complexity: if True, show the complexity score in addition to
        the complexity rank
    '''
    res = []
    average_cc = .0
    for line in results:
        ranked = cc_rank(line.complexity)
        average_cc += line.complexity
        if not min <= ranked <= max:
            continue
        res.append('{0}{1}'.format(' ' * 4, _format_line(line, ranked,
                                                         show_complexity)))
    if res:
        log(path)
        log_list(res)
    return average_cc, len(results)


@BAKER.command(shortopts={'multi': 'm', 'exclude': 'e', 'show': 's'})
def mi(multi=True, exclude=None, show=False, *paths):
    '''Analyze the given Python modules and compute the Maintainability Index.

    The maintainability index (MI) is a compound metric, with the primary aim
    of to determine how easy it will be to maintain a particular body of code.

    :param multi: Whether or not to count multiline strings as comments. Most
        of the time this is safe since multiline strings are used as functions
        docstrings, but one should be aware that their use is not limited to
        that and sometimes it would be wrong to count them as comment lines.
    :param paths: The modules or packages to analyze.
    '''
    for name in iter_filenames(paths, exclude):
        with open(name) as fobj:
            try:
                result = mi_visit(fobj.read(), multi)
            except Exception as e:
                log('{0}\n{1}ERROR: {2}', name, ' ' * 4, str(e))
                continue
            except KeyboardInterrupt:
                log(name)
                return
            rank = mi_rank(result)
            color = MI_RANKS[rank]
            to_show = ''
            if show:
                to_show = ' ({0:.2f})'.format(result)
            log('{0} - {1}{2}{3}{4}', name, color, rank, to_show, RESET)


@BAKER.command(shortopts={'min': 'n', 'max': 'x', 'show_complexity': 's',
                          'average': 'a', 'exclude': 'e', 'order': 'o'})
def cc(min='A', max='F', show_complexity=False, average=False,
       exclude=None, order='SCORE', *paths):
    '''Analyze the given Python modules and compute Cyclomatic
    Complexity (CC).

    The output can be filtered using the *min* and *max* flags. In addition
    to that, by default complexity score is not displayed.

    :param min: The minimum complexity to display (default to A).
    :param max: The maximum complexity to display (default to F).
    :param show_complexity: Whether or not to show the actual complexity
        score together with the A-F rank. Default to False.
    :param average: If True, at the end of the analysis display the average
        complexity. Default to False.
    :param paths: The modules or packages to analyze.
    '''
    min = min.upper()
    max = max.upper()
    average_cc = .0
    analyzed = 0
    order_function = getattr(cc_mod, order.upper(), getattr(cc_mod, 'SCORE'))
    for name in iter_filenames(paths, exclude or []):
        with open(name) as fobj:
            try:
                results = sorted_results(cc_visit(fobj.read()), order_function)
            except Exception as e:
                log('{0}\n{1}ERROR: {2}', name, ' ' * 4, str(e))
                continue
        cc, blocks = _print_cc_results(name, results, min, max,
                                       show_complexity)
        average_cc += cc
        analyzed += blocks

    if average and analyzed:
        cc = average_cc / analyzed
        ranked_cc = cc_rank(cc)
        log('\n{0} blocks (classes, functions, methods) analyzed.', analyzed)
        log('Average complexity: {0}{1} ({2}){3}', RANKS_COLORS[ranked_cc],
            ranked_cc, cc, RESET)


@BAKER.command(shortopts={'exclude': 'e'})
def raw(exclude=None, *paths):
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

    :param paths: The modules or packages to analyze.
    '''
    for path in iter_filenames(paths, exclude or []):
        with open(path) as fobj:
            log(path)
            try:
                mod = analyze(fobj.read())
            except Exception as e:
                log('{0}ERROR: {1}', ' ' * 4, str(e))
                continue
            for header, value in zip(['LOC', 'LLOC', 'SLOC', 'Comments',
                                      'Multi', 'Blank'], mod):
                log('{0}{1}: {2}', ' ' * 4, header, value)
            if not mod.loc:
                continue
            log(' ' * 4 + '- Comment Stats')
            indent = ' ' * 8
            comments = mod.comments
            log('{0}(C % L): {1:.0%}', indent, comments / float(mod.loc))
            log('{0}(C % S): {1:.0%}', indent, comments / float(mod.sloc))
            log('{0}(C + M % L): {1:.0%}', indent,
                (comments + mod.multi) / float(mod.loc))

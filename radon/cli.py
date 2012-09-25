try:
    import baker
except ImportError:
    raise ImportError('You need the baker module in order to use '
                      'the CLI tool')

try:
    import colorama
    GREEN, YELLOW, RED = (colorama.Fore.GREEN, colorama.Fore.YELLOW,
                          colorama.Fore.RED)
    MAGENTA, CYAN, WHITE = (colorama.Fore.MAGENTA, colorama.Fore.CYAN,
                            colorama.Fore.WHITE)
    BRIGHT, RESET = colorama.Style.BRIGHT, colorama.Style.RESET_ALL

    colorama_init = colorama.init
    colorama_deinit = colorama.deinit
except ImportError:
    # No colorama, so let's fallback to no-color mode
    GREEN = YELLOW = RED = MAGENTA = CYAN = WHITE = BRIGHT = RESET = ''
    colorama_init = colorama_deinit = lambda: True

from radon.complexity import cc_visit, rank
from radon.utils import iter_filenames
from radon.raw import analyze
from radon.metrics import mi_visit


RANKS_COLORS = {'A': GREEN, 'B': GREEN,
                'C': YELLOW, 'D': YELLOW,
                'E': RED, 'F': RED}

LETTERS_COLORS = {'F': MAGENTA,
                  'C': CYAN,
                  'M': WHITE}

TEMPLATE = '{}{} {reset}{}:{} {} - {}{}{reset}'
BAKER = baker.Baker()


def _format_line(line, ranked, show_complexity=False):
    '''Format a single line. *ranked* is the rank given by the
    `~radon.complexity.rank` function. If *show_complexity* is True, then
    the complexity score is added.
    '''
    letter_colored = LETTERS_COLORS[line.letter] + line.letter
    rank_colored = RANKS_COLORS[ranked] + ranked
    compl = ' ({}) '.format(line.complexity) if show_complexity else ''
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
        ranked = rank(line.complexity)
        average_cc += line.complexity
        if not min <= ranked <= max:
            continue
        res.append('{}{}'.format(' ' * 4, _format_line(line, ranked,
                                                       show_complexity)))
    if res:
        print path
        for r in res:
            print r
    return average_cc, len(results)


@BAKER.command(shortopts={'multi': 'm'})
def mi(multi=True, *paths):
    '''Analyze the given Python modules and compute the Maintainability Index.

    The maintainability index (MI) is a compound metric, with the primary aim
    of to determine how easy it will be to maintain a particular body of code.

    :param multi: Whether or not to count multiline strings as comments. Most
        of the time this is safe since multiline strings are used as functions
        docstrings, but one should be aware that their use is not limited to
        that and sometimes it would be wrong to count them as comment lines.
    :param paths: The modules or packages to analyze.
    '''
    for name in iter_filenames(paths):
        with open(name) as fobj:
            try:
                result = mi_visit(fobj.read(), multi)
            except Exception as e:
                print '{}ERROR: {}'.format(' ' * 4, str(e))
                continue
            print '{}\n{}{}'.format(name, ' ' * 4, result)


@BAKER.command(shortopts={'min': 'n', 'max': 'x', 'show_complexity': 's',
                          'average': 'a'})
def cc(min='A', max='F', show_complexity=False, average=False, *paths):
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
    for name in iter_filenames(paths):
        with open(name) as fobj:
            try:
                results = cc_visit(fobj.read())
            except Exception as e:
                print '{}ERROR: {}'.format(' ' * 4, str(e))
        cc, blocks =  _print_cc_results(name, results, min, max,
                                        show_complexity)
        average_cc += cc
        analyzed += blocks

    if average and analyzed:
        cc = average_cc / analyzed
        ranked_cc = rank(cc)
        print '\n{} blocks (classes, functions, methods) ' \
              'analyzed.'.format(analyzed)
        print 'Average complexity: {}{} ({}){}'.format(RANKS_COLORS[ranked_cc],
                                                       ranked_cc, cc, RESET)

@BAKER.command
def raw(*paths):
    for path in iter_filenames(paths):
        with open(path) as fobj:
            print path
            mod = analyze(fobj.read())
            for header, value in zip(['LOC', 'LLOC', 'SLOC', 'Comments',
                                      'Multi', 'Blank'], mod):
                print '{}{}: {}'.format(' ' * 4, header, value)
            if not mod.loc:
                continue
            print ' ' * 4 + '- Stats'
            indent = ' ' * 8
            comments = mod.comments
            print '{}(C % L): {:.0%}'.format(indent, comments / float(mod.loc))
            print '{}(C % S): {:.0%}'.format(indent, comments / float(mod.sloc))
            print '{}(C + M % L): {:.0%}'.format(indent, (comments + mod.multi) /
                                                 float(mod.loc))

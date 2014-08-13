'''In this module the CLI interface is created.'''

import sys
from mando import Program

import radon.complexity as cc_mod
from radon.cli.colors import BRIGHT, RED, RESET
from radon.cli.harvest import CCHarvester, RawHarvester, MIHarvester


program = Program(version=sys.modules['radon'].__version__)


class Config(object):

    def __init__(self, **kwargs):
        self.config_values = kwargs

    def __getattr__(self, attr):
        if attr in self.config_values:
            return self.config_values[attr]
        return self.__getattribute__(attr)


@program.command
@program.arg('paths', nargs='+')
def cc(paths, min='A', max='F', show_complexity=False, average=False,
       exclude=None, ignore=None, order='SCORE', json=False, no_assert=False,
       total_average=False, xml=False):
    '''Analyze the given Python modules and compute Cyclomatic
    Complexity (CC).

    The output can be filtered using the *min* and *max* flags. In addition
    to that, by default complexity score is not displayed.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -n, --min <str>: The minimum complexity to display (default to A).
    :param -x, --max <str>: The maximum complexity to display (default to F).
    :param -e, --exclude <str>: Comma separated list of patterns to exclude.
        By default hidden directories (those starting with '.') are excluded.
    :param -i, --ignore <str>: Comma separated list of patterns to ignore.
        If they are directory names, radon won't even descend into them.
    :param -s, --show-complexity: Whether or not to show the actual complexity
        score together with the A-F rank. Default to False.
    :param -a, --average: If True, at the end of the analysis display the
        average complexity. Default to False.
    :param --total-average: Like `-a, --average`, but it is not influenced by
        `min` and `max`. Every analyzed block is counted, no matter whether it
        is displayed or not.
    :param -o, --order <str>: The ordering function. Can be SCORE, LINES or
        ALPHA.
    :param -j, --json: Format results in JSON.
    :param --xml: Format results in XML (compatible with CCM).
    :param --no-assert: Do not count `assert` statements when computing
        complexity.
    '''

    config = Config(
        min=min.upper(),
        max=max.upper(),
        exclude=exclude,
        ignore=ignore,
        show_complexity=show_complexity,
        average=average,
        total_average=total_average,
        order=getattr(cc_mod, order.upper(), getattr(cc_mod, 'SCORE')),
        no_assert=no_assert,
    )
    harvester = CCHarvester(paths, config)
    log_result(harvester, json=json, xml=xml)


@program.command
@program.arg('paths', nargs='+')
def raw(paths, exclude=None, ignore=None, summary=False, json=False):
    '''Analyze the given Python modules and compute raw metrics.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -e, --exclude <str>: Comma separated list of patterns to exclude.
        By default hidden directories (those starting with '.') are excluded.
    :param -i, --ignore <str>: Comma separated list of patterns to ignore.
        Radon won't even descend into those directories.
    :param -s, --summary:  If given, at the end of the analysis display the
        summary of the gathered metrics. Default to False.
    :param -j, --json: Format results in JSON.
    '''

    config = Config(
        exclude=exclude,
        ignore=ignore,
        summary=summary,
    )
    harvester = RawHarvester(paths, config)
    log_result(harvester, json=json)


@program.command
@program.arg('paths', nargs='+')
def mi(paths, min='A', max='C', multi=True, exclude=None, ignore=None,
       show=False, json=False):
    '''Analyze the given Python modules and compute the Maintainability Index.

    The maintainability index (MI) is a compound metric, with the primary aim
    being to determine how easy it will be to maintain a particular body of
    code.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -n, --min <str>: The minimum MI to display (default to A).
    :param -x, --max <str>: The maximum MI to display (default to C).
    :param -e, --exclude <str>: Comma separated list of patterns to exclude.
    :param -i, --ignore <str>: Comma separated list of patterns to ignore.
        Radon won't even descend into those directories.
    :param -m, --multi: If given, multiline strings are not counted as
        comments.
    :param -s, --show: If given, the actual MI value is shown in results.
    :param -j, --json: Format results in JSON.
    '''

    config = Config(
        min=min.upper(),
        max=max.upper(),
        exclude=exclude,
        ignore=ignore,
        multi=multi,
        show=show,
    )

    harvester = MIHarvester(paths, config)
    log_result(harvester, json=json)


def log_result(harvester, **kwargs):
    if kwargs.get('json'):
        log(harvester.as_json(), noformat=True)
    elif kwargs.get('xml'):
        log(harvester.as_xml(), noformat=True)
    else:
        for msg, args, kwargs in harvester.to_terminal():
            if 'error' in kwargs:
                log(msg)
                log_error(args[0], indent=1)
                continue
            msg = [msg] if not isinstance(msg, list) else msg
            log_list(msg, *args, **kwargs)


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


def log_list(lst, *args, **kwargs):
    '''Log an entire list, line by line.'''
    for line in lst:
        log(line, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    '''Log an error message. Arguments are the same as log().'''
    log('{0}{1}ERROR{2}: {3}'.format(BRIGHT, RED, RESET, msg), *args, **kwargs)

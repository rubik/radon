'''In this module the CLI interface is created.'''

import sys
import inspect
from contextlib import contextmanager
from mando import Program

import radon.complexity as cc_mod
from radon.cli.colors import BRIGHT, RED, RESET
from radon.cli.harvest import CCHarvester, RawHarvester, MIHarvester, HCHarvester


program = Program(version=sys.modules['radon'].__version__)


@program.command
@program.arg('paths', nargs='+')
def cc(paths, min='A', max='F', show_complexity=False, average=False,
       exclude=None, ignore=None, order='SCORE', json=False, no_assert=False,
       show_closures=False, total_average=False, xml=False, codeclimate=False,
       output_file=None, ):
    '''Analyze the given Python modules and compute Cyclomatic
    Complexity (CC).

    The output can be filtered using the *min* and *max* flags. In addition
    to that, by default complexity score is not displayed.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -n, --min <str>: The minimum complexity to display (default to A).
    :param -x, --max <str>: The maximum complexity to display (default to F).
    :param -e, --exclude <str>: Exclude files only when their path matches one
        of these glob patterns. Usually needs quoting at the command line.
    :param -i, --ignore <str>: Ignore directories when their name matches one
        of these glob patterns: radon won't even descend into them. By default,
        hidden directories (starting with '.') are ignored.
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
    :param --codeclimate: Format results for Code Climate.
    :param --no-assert: Do not count `assert` statements when computing
        complexity.
    :param --show-closures: Add closures/inner classes to the output.
    :param -O, --output-file <str>: The output file (default to stdout).
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
        show_closures=show_closures,
    )
    harvester = CCHarvester(paths, config)
    with outstream(output_file) as stream:
        log_result(harvester, json=json, xml=xml, codeclimate=codeclimate,
                   stream=stream)


@program.command
@program.arg('paths', nargs='+')
def raw(paths, exclude=None, ignore=None, summary=False, json=False,
        output_file=None):
    '''Analyze the given Python modules and compute raw metrics.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -e, --exclude <str>: Exclude files only when their path matches one
        of these glob patterns. Usually needs quoting at the command line.
    :param -i, --ignore <str>: Ignore directories when their name matches one
        of these glob patterns: radon won't even descend into them. By default,
        hidden directories (starting with '.') are ignored.
    :param -s, --summary:  If given, at the end of the analysis display the
        summary of the gathered metrics. Default to False.
    :param -j, --json: Format results in JSON.
    :param -O, --output-file <str>: The output file (default to stdout).
    '''
    config = Config(
        exclude=exclude,
        ignore=ignore,
        summary=summary,
    )
    harvester = RawHarvester(paths, config)
    with outstream(output_file) as stream:
        log_result(harvester, json=json, stream=stream)


@program.command
@program.arg('paths', nargs='+')
def mi(paths, min='A', max='C', multi=True, exclude=None, ignore=None,
       show=False, json=False, sort=False, output_file=None):
    '''Analyze the given Python modules and compute the Maintainability Index.

    The maintainability index (MI) is a compound metric, with the primary aim
    being to determine how easy it will be to maintain a particular body of
    code.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -n, --min <str>: The minimum MI to display (default to A).
    :param -x, --max <str>: The maximum MI to display (default to C).
    :param -e, --exclude <str>: Exclude files only when their path matches one
        of these glob patterns. Usually needs quoting at the command line.
    :param -i, --ignore <str>: Ignore directories when their name matches one
        of these glob patterns: radon won't even descend into them. By default,
        hidden directories (starting with '.') are ignored.
    :param -m, --multi: If given, multiline strings are not counted as
        comments.
    :param -s, --show: If given, the actual MI value is shown in results.
    :param -j, --json: Format results in JSON.
    :param --sort: If given, results are sorted in ascending order.
    :param -O, --output-file <str>: The output file (default to stdout).
    '''
    config = Config(
        min=min.upper(),
        max=max.upper(),
        exclude=exclude,
        ignore=ignore,
        multi=multi,
        show=show,
        sort=sort,
    )

    harvester = MIHarvester(paths, config)
    with outstream(output_file) as stream:
        log_result(harvester, json=json, stream=stream)


@program.command
@program.arg("paths", nargs="+")
def hal(paths, exclude=None, ignore=None, json=False, functions=False,
        output_file=None):
    """
    Analyze the given Python modules and compute their Halstead metrics.

    The Halstead metrics are a series of measurements meant to quantitatively
    measure the complexity of code, including the difficulty a programmer would
    have in writing it.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -e, --exclude <str>: Exclude files only when their path matches one
        of these glob patterns. Usually needs quoting at the command line.
    :param -i, --ignore <str>: Ignore directories when their name matches one
        of these glob patterns: radon won't even descend into them. By default,
        hidden directories (starting with '.') are ignored.
    :param -j, --json: Format results in JSON.
    :param -f, --functions: Analyze files by top-level functions instead of as a whole.
    :param -O, --output-file <str>: The output file (default to stdout).
    """
    config = Config(
        exclude=exclude,
        ignore=ignore,
        by_function=functions,
    )

    harvester = HCHarvester(paths, config)
    with outstream(output_file) as stream:
        log_result(harvester, json=json, xml=False, stream=stream)


class Config(object):
    '''An object holding config values.'''

    def __init__(self, **kwargs):
        '''Configuration values are passed as keyword parameters.'''
        self.config_values = kwargs

    def __getattr__(self, attr):
        '''If an attribute is not found inside the config values, the request
        is handed to `__getattribute__`.
        '''
        if attr in self.config_values:
            return self.config_values[attr]
        return self.__getattribute__(attr)

    def __repr__(self):
        '''The string representation of the Config object is just the one of
        the dictionary holding the configuration values.
        '''
        return repr(self.config_values)

    def __eq__(self, other):
        '''Two Config objects are equals if their contents are equal.'''
        return self.config_values == other.config_values

    @classmethod
    def from_function(cls, func):
        '''Construct a Config object from a function's defaults.'''
        kwonlydefaults = {}
        try:
            argspec = inspect.getfullargspec(func)
            kwonlydefaults = argspec.kwonlydefaults or {}
        except AttributeError:  # pragma: no cover
            argspec = inspect.getargspec(func)
        args, _, _, defaults = argspec[:4]
        values = dict(zip(reversed(args), reversed(defaults or [])))
        values.update(kwonlydefaults)
        return cls(**values)


def log_result(harvester, **kwargs):
    '''Log the results of an :class:`~radon.cli.harvest.Harvester object.

    Keywords parameters determine how the results are formatted. If *json* is
    `True`, then `harvester.as_json()` is called. If *xml* is `True`, then
    `harvester.as_xml()` is called. If *codeclimate* is True, then
    `harvester.as_codeclimate_issues()` is called.
    Otherwise, `harvester.to_terminal()` is executed and `kwargs` is directly
    passed to the :func:`~radon.cli.log` function.
    '''
    if kwargs.get('json'):
        log(harvester.as_json(), noformat=True, **kwargs)
    elif kwargs.get('xml'):
        log(harvester.as_xml(), noformat=True, **kwargs)
    elif kwargs.get('codeclimate'):
        log_list(harvester.as_codeclimate_issues(), delimiter='\0',
                 noformat=True, **kwargs)
    else:
        for msg, h_args, h_kwargs in harvester.to_terminal():
            kw = kwargs.copy()
            kw.update(h_kwargs)
            if h_kwargs.get('error', False):
                log(msg, **kw)
                log_error(h_args[0], indent=1)
                continue
            msg = [msg] if not isinstance(msg, (list, tuple)) else msg
            log_list(msg, *h_args, **kw)


def log(msg, *args, **kwargs):
    '''Log a message, passing *args* to the strings' `format()` method.

    *indent*, if present as a keyword argument, specifies the indent level, so
    that `indent=0` will log normally, `indent=1` will indent the message by 4
    spaces, &c..
    *noformat*, if present and True, will cause the message not to be formatted
    in any way.
    '''
    indent = 4 * kwargs.get('indent', 0)
    delimiter = kwargs.get('delimiter', '\n')
    m = msg if kwargs.get('noformat', False) else msg.format(*args)
    stream = kwargs.get('stream', sys.stdout)
    stream.write(' ' * indent + m + delimiter)


def log_list(lst, *args, **kwargs):
    '''Log an entire list, line by line. All the arguments are directly passed
    to :func:`~radon.cli.log`.
    '''
    for line in lst:
        log(line, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    '''Log an error message. Arguments are the same as log().'''
    log('{0}{1}ERROR{2}: {3}'.format(BRIGHT, RED, RESET, msg), *args, **kwargs)


@contextmanager
def outstream(outfile=None):
    '''Encapsulate output stream creation as a context manager'''
    if outfile:
        with open(outfile, 'w') as outstream:
            yield outstream
    else:
        yield sys.stdout

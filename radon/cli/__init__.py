'''In this module the CLI interface is created.'''

import inspect
import os
import sys
from contextlib import contextmanager

from mando import Program

import radon.complexity as cc_mod
from radon.cli.colors import BRIGHT, RED, RESET
from radon.cli.harvest import (
    CCHarvester,
    HCHarvester,
    MIHarvester,
    RawHarvester,
)

if sys.version_info[0] == 2:
    import ConfigParser as configparser
else:
    import configparser


CONFIG_SECTION_NAME = 'radon'


class FileConfig(object):
    '''
    Yield default options by reading local configuration files.
    '''

    def __init__(self):
        self.file_cfg = self.file_config()

    def get_value(self, key, type, default):
        if not self.file_cfg.has_option(CONFIG_SECTION_NAME, key):
            return default
        if type == int:
            return self.file_cfg.getint(
                CONFIG_SECTION_NAME, key, fallback=default
            )
        if type == bool:
            return self.file_cfg.getboolean(
                CONFIG_SECTION_NAME, key, fallback=default
            )
        else:
            return self.file_cfg.get(
                CONFIG_SECTION_NAME, key, fallback=default
            )

    @staticmethod
    def file_config():
        '''Return any file configuration discovered'''
        config = configparser.ConfigParser()
        for path in (os.getenv('RADONCFG', None), 'radon.cfg'):
            if path is not None and os.path.exists(path):
                config.read_file(open(path))
        config.read(['setup.cfg', os.path.expanduser('~/.radon.cfg')])
        return config


_cfg = FileConfig()

program = Program(version=sys.modules['radon'].__version__)


@program.command
@program.arg('paths', nargs='+')
def cc(
    paths,
    min=_cfg.get_value('cc_min', str, 'A'),
    max=_cfg.get_value('cc_max', str, 'F'),
    show_complexity=_cfg.get_value('show_complexity', bool, False),
    average=_cfg.get_value('average', bool, False),
    exclude=_cfg.get_value('exclude', str, None),
    ignore=_cfg.get_value('ignore', str, None),
    order=_cfg.get_value('order', str, 'SCORE'),
    json=False,
    no_assert=_cfg.get_value('no_assert', bool, False),
    show_closures=_cfg.get_value('show_closures', bool, False),
    total_average=_cfg.get_value('total_average', bool, False),
    xml=False,
    md=False,
    codeclimate=False,
    output_file=_cfg.get_value('output_file', str, None),
    include_ipynb=_cfg.get_value('include_ipynb', bool, False),
    ipynb_cells=_cfg.get_value('ipynb_cells', bool, False),
):
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
    :param --md: Format results in Markdown.
    :param --codeclimate: Format results for Code Climate.
    :param --no-assert: Do not count `assert` statements when computing
        complexity.
    :param --show-closures: Add closures/inner classes to the output.
    :param -O, --output-file <str>: The output file (default to stdout).
    :param --include-ipynb: Include IPython Notebook files
    :param --ipynb-cells: Include reports for individual IPYNB cells
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
        include_ipynb=include_ipynb,
        ipynb_cells=ipynb_cells,
    )
    harvester = CCHarvester(paths, config)
    with outstream(output_file) as stream:
        log_result(
            harvester,
            json=json,
            xml=xml,
            md=md,
            codeclimate=codeclimate,
            stream=stream,
        )


@program.command
@program.arg('paths', nargs='+')
def raw(
    paths,
    exclude=_cfg.get_value('exclude', str, None),
    ignore=_cfg.get_value('ignore', str, None),
    summary=False,
    json=False,
    output_file=_cfg.get_value('output_file', str, None),
    include_ipynb=_cfg.get_value('include_ipynb', bool, False),
    ipynb_cells=_cfg.get_value('ipynb_cells', bool, False),
):
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
    :param --include-ipynb: Include IPython Notebook files
    :param --ipynb-cells: Include reports for individual IPYNB cells
    '''
    config = Config(
        exclude=exclude,
        ignore=ignore,
        summary=summary,
        include_ipynb=include_ipynb,
        ipynb_cells=ipynb_cells,
    )
    harvester = RawHarvester(paths, config)
    with outstream(output_file) as stream:
        log_result(harvester, json=json, stream=stream)


@program.command
@program.arg('paths', nargs='+')
def mi(
    paths,
    min=_cfg.get_value('mi_min', str, 'A'),
    max=_cfg.get_value('mi_max', str, 'C'),
    multi=_cfg.get_value('multi', bool, True),
    exclude=_cfg.get_value('exclude', str, None),
    ignore=_cfg.get_value('ignore', str, None),
    show=_cfg.get_value('show_mi', bool, False),
    json=False,
    sort=False,
    output_file=_cfg.get_value('output_file', str, None),
    include_ipynb=_cfg.get_value('include_ipynb', bool, False),
    ipynb_cells=_cfg.get_value('ipynb_cells', bool, False),
):
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
    :param --include-ipynb: Include IPython Notebook files
    :param --ipynb-cells: Include reports for individual IPYNB cells
    '''
    config = Config(
        min=min.upper(),
        max=max.upper(),
        exclude=exclude,
        ignore=ignore,
        multi=multi,
        show=show,
        sort=sort,
        include_ipynb=include_ipynb,
        ipynb_cells=ipynb_cells,
    )

    harvester = MIHarvester(paths, config)
    with outstream(output_file) as stream:
        log_result(harvester, json=json, stream=stream)


@program.command
@program.arg("paths", nargs="+")
def hal(
    paths,
    exclude=_cfg.get_value('exclude', str, None),
    ignore=_cfg.get_value('ignore', str, None),
    json=False,
    functions=_cfg.get_value('functions', bool, False),
    output_file=_cfg.get_value('output_file', str, None),
    include_ipynb=_cfg.get_value('include_ipynb', bool, False),
    ipynb_cells=_cfg.get_value('ipynb_cells', bool, False),
):
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
    :param -f, --functions: Analyze files by top-level functions instead of as
        a whole.
    :param -O, --output-file <str>: The output file (default to stdout).
    :param --include-ipynb: Include IPython Notebook files
    :param --ipynb-cells: Include reports for individual IPYNB cells
    """
    config = Config(
        exclude=exclude,
        ignore=ignore,
        by_function=functions,
        include_ipynb=include_ipynb,
        ipynb_cells=ipynb_cells,
    )

    harvester = HCHarvester(paths, config)
    with outstream(output_file) as stream:
        log_result(harvester, json=json, xml=False, md=False, stream=stream)


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
        log_list(
            harvester.as_codeclimate_issues(),
            delimiter='\0',
            noformat=True,
            **kwargs
        )
    elif kwargs.get('md'):
        log(harvester.as_md(), noformat=True, **kwargs)
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

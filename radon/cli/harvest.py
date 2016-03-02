'''This module holds the base Harvester class and all its subclassess.'''

import json
import collections
from radon.raw import analyze
from radon.metrics import mi_visit, mi_rank
from radon.complexity import (cc_visit, sorted_results, cc_rank,
                              add_inner_blocks)
from radon.cli.colors import RANKS_COLORS, MI_RANKS, RESET
from radon.cli.tools import (iter_filenames, _open, cc_to_dict, dict_to_xml,
                             dict_to_codeclimate_issues, cc_to_terminal,
                             raw_to_dict)


class Harvester(object):
    '''Base class defining the interface of a Harvester object.

    A Harvester has the following lifecycle:

    1. **Initialization**: `h = Harvester(paths, config)`

    2. **Execution**: `r = h.results`. `results` holds an iterable object.
       The first time `results` is accessed, `h.run()` is called. This method
       should not be subclassed. Instead, the :meth:`gobble` method should be
       implemented.

    3. **Reporting**: the methods *as_json* and *as_xml* return a string
       with the corrisponding format. The method *to_terminal* is a generator
       that yields the lines to be printed in the terminal.

    This class is meant to be subclasses and cannot be used directly, since
    the methods :meth:`gobble`, :meth:`as_xml` and :meth:`to_terminal` are
    not implemented.
    '''

    def __init__(self, paths, config):
        '''Initialize the Harvester.

        *paths* is a list of paths to analyze.
        *config* is a :class:`~radon.cli.Config` object holding the
        configuration values specific to the Harvester.
        '''
        self.paths = paths
        self.config = config
        self._results = []

    def _iter_filenames(self):
        '''A wrapper around :func:`~radon.cli.tools.iter_filenames`.'''
        return iter_filenames(self.paths, self.config.exclude,
                              self.config.ignore)

    def gobble(self, fobj):
        '''Subclasses must implement this method to define behavior.

        This method is called for every file to analyze. *fobj* is the file
        object. This method should return the results from the analysis,
        preferably a dictionary.
        '''
        raise NotImplementedError

    def run(self):
        '''Start the analysis. For every file, this method calls the
        :meth:`gobble` method. Results are yielded as tuple:
        ``(filename, analysis_results)``.
        '''
        for name in self._iter_filenames():
            with _open(name) as fobj:
                try:
                    yield (name, self.gobble(fobj))
                except Exception as e:
                    yield (name, {'error': str(e)})

    @property
    def results(self):
        '''This property holds the results of the analysis.

        The first time it is accessed, an iterator is returned. Its
        elements are cached into a list as it is iterated over. Therefore, if
        `results` is accessed multiple times after the first one, a list will
        be returned.
        '''
        def caching_iterator(it, r):
            '''An iterator that caches another iterator.'''
            for t in it:
                yield t
                r.append(t)

        if self._results:
            return self._results
        return caching_iterator(self.run(), self._results)

    def as_json(self):
        '''Format the results as JSON.'''
        return json.dumps(dict(self.results))

    def as_xml(self):
        '''Format the results as XML.'''
        raise NotImplementedError

    def as_codeclimate_issues(self):
        '''Format the results as Code Climate issues.'''
        raise NotImplementedError

    def to_terminal(self):
        '''Yields tuples representing lines to be printed to a terminal.

        The tuples have the following format: ``(line, args, kwargs)``.
        The line is then formatted with `line.format(*args, **kwargs)`.
        '''
        raise NotImplementedError


class CCHarvester(Harvester):
    '''A class that analyzes Python modules' Cyclomatic Complexity.'''

    def gobble(self, fobj):
        '''Analyze the content of the file object.'''
        r = cc_visit(fobj.read(), no_assert=self.config.no_assert)
        if self.config.show_closures:
            r = add_inner_blocks(r)
        return sorted_results(r, order=self.config.order)

    def _to_dicts(self):
        '''Format the results as a dictionary of dictionaries.'''
        result = {}
        for key, data in self.results:
            if 'error' in data:
                result[key] = data
                continue
            values = [v for v in map(cc_to_dict, data)
                      if self.config.min <= v['rank'] <= self.config.max]
            if values:
                result[key] = values
        return result

    def as_json(self):
        '''Format the results as JSON.'''
        return json.dumps(self._to_dicts())

    def as_xml(self):
        '''Format the results as XML. This is meant to be compatible with
        Jenkin's CCM plugin. Therefore not all the fields are kept.
        '''
        return dict_to_xml(self._to_dicts())

    def as_codeclimate_issues(self):
        '''Format the result as Code Climate issues.'''
        return dict_to_codeclimate_issues(self._to_dicts(), self.config.min)

    def to_terminal(self):
        '''Yield lines to be printed in a terminal.'''
        average_cc = .0
        analyzed = 0
        for name, blocks in self.results:
            if 'error' in blocks:
                yield name, (blocks['error'],), {'error': True}
                continue
            res, cc, n = cc_to_terminal(blocks, self.config.show_complexity,
                                        self.config.min, self.config.max,
                                        self.config.total_average)
            average_cc += cc
            analyzed += n
            if res:
                yield name, (), {}
                yield res, (), {'indent': 1}

        if (self.config.average or self.config.total_average) and analyzed:
            cc = average_cc / analyzed
            ranked_cc = cc_rank(cc)
            yield ('\n{0} blocks (classes, functions, methods) analyzed.',
                   (analyzed,), {})
            yield ('Average complexity: {0}{1} ({2}){3}',
                   (RANKS_COLORS[ranked_cc], ranked_cc, cc, RESET), {})


class RawHarvester(Harvester):
    '''A class that analyzes Python modules' raw metrics.'''

    headers = ['LOC', 'LLOC', 'SLOC', 'Comments', 'Single comments', 'Multi',
               'Blank']

    def gobble(self, fobj):
        '''Analyze the content of the file object.'''
        return raw_to_dict(analyze(fobj.read()))

    def as_xml(self):
        '''Placeholder method. Currently not implemented.'''
        raise NotImplementedError('Cannot export results as XML')

    def to_terminal(self):
        '''Yield lines to be printed to a terminal.'''
        sum_metrics = collections.defaultdict(int)
        for path, mod in self.results:
            if 'error' in mod:
                yield path, (mod['error'],), {'error': True}
                continue
            yield path, (), {}
            for header in self.headers:
                value = mod[header.lower().replace(' ', '_')]
                yield '{0}: {1}', (header, value), {'indent': 1}
                sum_metrics[header] += value

            loc, comments = mod['loc'], mod['comments']
            yield '- Comment Stats', (), {'indent': 1}
            yield ('(C % L): {0:.0%}', (comments / (float(loc) or 1),),
                   {'indent': 2})
            yield ('(C % S): {0:.0%}', (comments / (float(mod['sloc']) or 1),),
                   {'indent': 2})
            yield ('(C + M % L): {0:.0%}',
                   ((comments + mod['multi']) / (float(loc) or 1),),
                   {'indent': 2})

        if self.config.summary:
            yield '** Total **', (), {}
            for header in self.headers:
                yield '{0}: {1}', (header, sum_metrics[header]), {'indent': 1}


class MIHarvester(Harvester):
    '''A class that analyzes Python modules' Maintainability Index.'''

    def gobble(self, fobj):
        '''Analyze the content of the file object.'''
        mi = mi_visit(fobj.read(), self.config.multi)
        rank = mi_rank(mi)
        return {'mi': mi, 'rank': rank}

    @property
    def filtered_results(self):
        '''Filter results with respect with their rank.'''
        for key, value in self.results:
            if ('error' in value or
               self.config.min <= value['rank'] <= self.config.max):
                yield (key, value)

    def as_json(self):
        '''Format the results as JSON.'''
        return json.dumps(dict(self.filtered_results))

    def as_xml(self):
        '''Placeholder method. Currently not implemented.'''
        raise NotImplementedError('Cannot export results as XML')

    def to_terminal(self):
        '''Yield lines to be printed to a terminal.'''
        for name, mi in self.filtered_results:
            if 'error' in mi:
                yield name, (mi['error'],), {'error': True}
                continue
            rank = mi['rank']
            color = MI_RANKS[rank]
            to_show = ''
            if self.config.show:
                to_show = ' ({0:.2f})'.format(mi['mi'])
            yield '{0} - {1}{2}{3}{4}', (name, color, rank, to_show, RESET), {}

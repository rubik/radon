import json
import collections
from radon.raw import analyze
from radon.metrics import mi_visit, mi_rank
from radon.complexity import cc_visit, sorted_results, cc_rank
from radon.cli.colors import RANKS_COLORS, MI_RANKS, RESET
from radon.cli.tools import (iter_filenames, _open, cc_to_dict, dict_to_xml,
                             cc_to_terminal, raw_to_dict)


class Harvester(object):

    def __init__(self, paths, config):
        self.paths = paths
        self.config = config
        self._results = []

    def _iter_filenames(self):
        return iter_filenames(self.paths, self.config.exclude,
                              self.config.ignore)

    def gobble(self):
        raise NotImplementedError

    def run(self):
        for name in self._iter_filenames():
            with _open(name) as fobj:
                try:
                    yield (name, self.gobble(fobj))
                except Exception as e:
                    yield (name, {'error': str(e)})

    @property
    def results(self):
        def caching_iterator(it, r):
            for t in it:
                yield t
                r.append(t)

        if self._results:
            return self._results
        return caching_iterator(self.run(), self._results)

    def as_json(self):
        return json.dumps(dict(self.results))


class CCHarvester(Harvester):

    def gobble(self, fobj):
        r = cc_visit(fobj.read(), no_assert=self.config.no_assert)
        return sorted_results(r, order=self.config.order)

    def _to_dicts(self):
        result = {}
        for key, data in self.results:
            result[key] = list(map(cc_to_dict, data))
        return result

    def as_json(self):
        return json.dumps(self._to_dicts())

    def as_xml(self):
        return dict_to_xml(self._to_dicts())

    def to_terminal(self):
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

    headers = ['LOC', 'LLOC', 'SLOC', 'Comments', 'Multi', 'Blank']

    def gobble(self, fobj):
        return raw_to_dict(analyze(fobj.read()))

    def to_terminal(self):
        sum_metrics = collections.defaultdict(int)
        for path, mod in self.results:
            if 'error' in mod:
                yield path, (mod['error'],), {'error': True}
                continue
            yield path, (), {}
            for header in self.headers:
                value = mod[header.lower()]
                yield '{0}: {1}', (header, value), {'indent': 1}
                sum_metrics[header] += value

            loc, comments = mod['loc'], mod['comments']
            yield '- Comment Stats', (), {'indent': 1}
            yield ('(C % L): {0:.0%}', (comments / (float(loc) or 1),),
                   {'indent': 2})
            yield ('(C % S): {0:.0%}', (comments / (float(mod['sloc']) or 1),),
                   {'indent': 2})
            yield ('(C + M % L): {0:.0%}',
                   ((comments + mod['multi']) / float(loc),), {'indent': 2})

        if self.config.summary:
            yield '** Total **', (), {}
            for header in self.headers:
                yield '{0}: {1}', (header, sum_metrics[header]), {'indent': 1}


class MIHarvester(Harvester):

    def gobble(self, fobj):
        return {'mi': mi_visit(fobj.read(), self.config.multi)}

    def to_terminal(self):
        for name, mi in self.results:
            if 'error' in mi:
                yield name, (mi['error'],), {'error': True}
                continue
            rank = mi_rank(mi['mi'])
            if not self.config.min <= rank <= self.config.max:
                continue
            color = MI_RANKS[rank]
            to_show = ''
            if self.config.show:
                to_show = ' ({0:.2f})'.format(mi['mi'])
            yield '{0} - {1}{2}{3}{4}', (name, color, rank, to_show, RESET), {}

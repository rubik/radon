import os
import sys
import unittest
import radon.cli.tools as tools
from radon.visitors import Function, Class
from radon.raw import Module
try:
    import unittest.mock as mock
except ImportError:
    import mock
from paramunittest import parametrized


def fake_isfile(filename):
    if filename == 'file.py':
        return True
    return False


def fake_walk(start):
    dirs = ['tests', 'sub', '.hid']
    contents = {'tests': ['test_amod.py', 'run.py', '.hid.py'],
                'sub': ['amod.py', 'bmod.py']}
    yield '.', dirs, ['tox.ini', 'amod.py', 'test_all.py', 'fake.yp', 'noext']
    for d in dirs:
        yield './{0}'.format(d), [], contents[d]


class TestGenericTools(unittest.TestCase):

    def test_open(self):
        with tools._open('-') as fobj:
            self.assertTrue(fobj is sys.stdin)

        m = mock.mock_open()
        with mock.patch('radon.cli.tools.open', m, create=True):
            tools._open('randomfile.py').__enter__()
        m.assert_called_with('randomfile.py')


class TestIterFilenames(unittest.TestCase):

    def setUp(self):
        self.iter_files = lambda *a, **kw: list(tools.iter_filenames(*a, **kw))

    def assertPEqual(self, a, b):
        paths = [list(map(os.path.normpath, p)) for p in (a, b)]
        self.assertEqual(*paths)

    def test_stdin(self):
        self.assertEqual(self.iter_files(['-']), ['-'])

    @mock.patch('radon.cli.tools.os.path')
    @mock.patch('radon.cli.tools.os')
    def test_all(self, os_mod, os_path_mod):
        os_path_mod.normpath = os.path.normpath
        os_path_mod.basename = os.path.basename
        os_path_mod.join = os.path.join
        os_path_mod.isfile.side_effect = fake_isfile
        os_mod.walk = fake_walk

        self.assertPEqual(self.iter_files(['file.py', 'random/path']),
                          ['file.py', 'amod.py', 'test_all.py',
                           'tests/test_amod.py', 'tests/run.py', 'sub/amod.py',
                           'sub/bmod.py'])

        self.assertPEqual(self.iter_files(['file.py', 'random/path'],
                                          'test_*'),
                          ['file.py', 'amod.py', 'tests/test_amod.py',
                           'tests/run.py', 'sub/amod.py', 'sub/bmod.py'])

        self.assertPEqual(self.iter_files(['file.py', 'random/path'],
                                          '*test_*'),
                          ['file.py', 'amod.py', 'tests/run.py', 'sub/amod.py',
                           'sub/bmod.py'])

        self.assertPEqual(self.iter_files(['file.py', 'random/path'],
                                          '*/test_*,amod*'),
                          ['file.py', 'test_all.py', 'tests/run.py',
                           'sub/amod.py', 'sub/bmod.py'])

        self.assertPEqual(self.iter_files(['file.py', 'random/path'], None,
                                          'tests'),
                          ['file.py', 'amod.py', 'test_all.py', 'sub/amod.py',
                           'sub/bmod.py'])

        self.assertPEqual(self.iter_files(['file.py', 'random/path'], None,
                                          'tests,sub'),
                          ['file.py', 'amod.py', 'test_all.py'])


CC_RESULTS_CASES = [
    ([
        Function('name', 12, 0, 16, False, None, [], 6),
    ], {
        'type': 'function', 'name': 'name', 'lineno': 12, 'col_offset': 0,
        'endline': 16, 'clojures': [], 'complexity': 6, 'rank': 'B',
    }),
    ([
        Class('Classname', 17, 0, 29, [
            Function('name', 19, 4, 26, True, 'Classname', [], 7),
        ], 7),
    ], {
        'type': 'class', 'name': 'Classname', 'lineno': 17, 'col_offset': 0,
        'endline': 29, 'complexity': 8, 'rank': 'B', 'methods': [
            {
                'type': 'method', 'lineno': 19, 'col_offset': 4, 'endline': 26,
                'clojures': [], 'complexity': 7, 'rank': 'B', 'classname':
                'Classname', 'name': 'name',
            }
        ],
    }),
    ([
        Function('name', 12, 0, 16, False, None, [
            Function('aux', 13, 4, 17, False, None, [], 4),
        ], 10),
    ], {
        'type': 'function', 'name': 'name', 'lineno': 12, 'col_offset': 0,
        'endline': 16, 'complexity': 10, 'rank': 'B', 'clojures': [
            {
                'name': 'aux', 'lineno': 13, 'col_offset': 4, 'endline': 17,
                'clojures': [], 'complexity': 4, 'rank': 'A', 'type':
                'function',
            }
        ]
    }),
]


@parametrized(*CC_RESULTS_CASES)
class TestCCToDict(unittest.TestCase):

    def setParameters(self, blocks, **dict_result):
        self.blocks = blocks
        self.dict_result = dict_result

    def testCCToDict(self):
        self.assertEqual(tools.cc_to_dict(self.blocks), self.dict_result)


CC_TO_XML_CASE = [
    {'clojures': [], 'endline': 16, 'complexity': 6, 'lineno': 12, 'is_method':
     False, 'name': 'name', 'col_offset': 0, 'rank': 'B'},

    {'complexity': 8, 'endline': 29, 'rank': 'B', 'lineno': 17, 'name':
     'Classname', 'col_offset': 0},

    {'classname': 'Classname', 'clojures': [], 'endline': 26, 'complexity': 7,
     'lineno': 19, 'is_method': True, 'name': 'name', 'col_offset': 4,
     'rank': 'B'},

    {'clojures': [], 'endline': 17, 'complexity': 4, 'lineno': 13, 'is_method':
     False, 'name': 'aux', 'col_offset': 4, 'rank': 'A'},

    {'endline': 16, 'complexity': 10, 'lineno': 12, 'is_method': False, 'name':
     'name', 'col_offset': 0, 'rank': 'B'},
]


class TestDictConversion(unittest.TestCase):

    def test_raw_to_dict(self):
        self.assertEqual(tools.raw_to_dict(Module(103, 123, 98, 8, 19, 5)),
                         {'loc': 103, 'lloc': 123, 'sloc': 98, 'comments': 8,
                          'multi': 19, 'blank': 5})

    def test_cc_to_xml(self):
        self.assertEqual(tools.dict_to_xml({'filename': CC_TO_XML_CASE}),
                         '''<ccm>
                              <metric>
                                <complexity>6</complexity>
                                <unit>name</unit>
                                <classification>B</classification>
                                <file>filename</file>
                              </metric>
                              <metric>
                                <complexity>8</complexity>
                                <unit>Classname</unit>
                                <classification>B</classification>
                                <file>filename</file>
                              </metric>
                              <metric>
                                <complexity>7</complexity>
                                <unit>Classname.name</unit>
                                <classification>B</classification>
                                <file>filename</file>
                              </metric>
                              <metric>
                                <complexity>4</complexity>
                                <unit>aux</unit>
                                <classification>A</classification>
                                <file>filename</file>
                              </metric>
                              <metric>
                                <complexity>10</complexity>
                                <unit>name</unit>
                                <classification>B</classification>
                                <file>filename</file>
                              </metric>
                            </ccm>'''.replace('\n', '').replace(' ', ''))


CC_TO_TERMINAL_CASES = [
    Class(name='Classname', lineno=17, col_offset=0, endline=29,
          methods=[Function(name='meth', lineno=19, col_offset=4, endline=26,
                            is_method=True, classname='Classname', clojures=[],
                            complexity=3)], real_complexity=3),
    Function(name='meth', lineno=19, col_offset=4, endline=26, is_method=True,
             classname='Classname', clojures=[], complexity=7),
    Function(name='f1', lineno=12, col_offset=0, endline=16, is_method=False,
             classname=None, clojures=[], complexity=14),
    Function(name='f2', lineno=12, col_offset=0, endline=16, is_method=False,
             classname=None, clojures=[], complexity=22),
    Function(name='f3', lineno=12, col_offset=0, endline=16, is_method=False,
             classname=None, clojures=[], complexity=32),
    Function(name='f4', lineno=12, col_offset=0, endline=16, is_method=False,
             classname=None, clojures=[], complexity=41),
]


class TestCCToTerminal(unittest.TestCase):

    def test_cc_to_terminal(self):
        # do the patching
        tools.LETTERS_COLORS = dict((l, '<!{0}!>'.format(l)) for l in 'FMC')
        tools.RANKS_COLORS = dict((r, '<|{0}|>'.format(r)) for r in 'ABCDEF')
        tools.BRIGHT = '@'
        tools.RESET = '__R__'

        results = CC_TO_TERMINAL_CASES
        res = [
            '@<!C!>C __R__17:0 Classname - <|A|>A (4)__R__',
            '@<!M!>M __R__19:4 Classname.meth - <|B|>B (7)__R__',
            '@<!F!>F __R__12:0 f1 - <|C|>C (14)__R__',
            '@<!F!>F __R__12:0 f2 - <|D|>D (22)__R__',
            '@<!F!>F __R__12:0 f3 - <|E|>E (32)__R__',
            '@<!F!>F __R__12:0 f4 - <|F|>F (41)__R__',
        ]
        res_noshow = ['{0}__R__'.format(r[:r.index('(') - 1]) for r in res]

        self.assertEqual(tools.cc_to_terminal(results, False, 'A', 'F', False),
                         (res_noshow, 120, 6))
        self.assertEqual(tools.cc_to_terminal(results, True, 'A', 'F', False),
                         (res, 120, 6))
        self.assertEqual(tools.cc_to_terminal(results, True, 'A', 'D', False),
                         (res[:-2], 47, 4))
        self.assertEqual(tools.cc_to_terminal(results, False, 'A', 'D', False),
                         (res_noshow[:-2], 47, 4))
        self.assertEqual(tools.cc_to_terminal(results, True, 'C', 'F', False),
                         (res[2:], 109, 4))
        self.assertEqual(tools.cc_to_terminal(results, True, 'B', 'E', False),
                         (res[1:-1], 75, 4))
        self.assertEqual(tools.cc_to_terminal(results, True, 'B', 'F', True),
                         (res[1:], 120, 6))

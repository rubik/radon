#
# Copyright 2009 keyes.ie
#
# License: http://jkeyes.mit-license.org/
#

import os
import unittest

from radon.pathfinder import find_paths
from radon.pathfinder import walk_and_filter
from radon.pathfinder.filters import *

BASEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
pathfind = lambda *a, **kw: list(find_paths(*a, **kw))

class FindTest(unittest.TestCase):

    def test_just_dirs(self):
        """ Test just_dirs parameter."""
        # only find directories
        paths = pathfind(BASEPATH, just_dirs=True)
        self.assertEqual(5, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4') in paths)

        # use Filter.find
        paths_2 = DirectoryFilter().find(BASEPATH)
        self.assertEqual(paths, paths_2)

    def test_just_files(self):
        """ Test just_files parameter."""
        # only find files
        paths = pathfind(BASEPATH, just_files=True)
        self.assertEqual(17, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'file1.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file2.dat') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file3.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.jpg') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'transparent_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory', 'sub.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file4.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file5.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file6.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file7.html') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', 'file8') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', '.file9') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4', 'file10') in paths)

        # use Filter.find
        paths_2 = FileFilter().find(BASEPATH)
        self.assertEqual(paths, paths_2)

    def test_regex(self):
        """ Test regex parameter."""
        # find all files and directories
        paths = pathfind(BASEPATH, regex=".*")
        self.assertEqual(22, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file1.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file2.dat') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file3.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.jpg') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'transparent_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory', 'sub.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file4.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file5.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file6.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file7.html') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', 'file8') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', '.file9') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4', 'file10') in paths)

        # use Filter.find
        paths_2 = RegexFilter('.*').find(BASEPATH)
        self.assertEqual(paths, paths_2)

        # find only files and directories with a t in the extension
        paths = pathfind(BASEPATH, regex=".*\..*t.*$")
        self.assertEqual(6, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'file1.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file2.dat') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file3.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory', 'sub.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file4.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file7.html') in paths)

        # find only files and directories with 1 anywhere in the path
        paths = pathfind(BASEPATH, regex=".*1.*")
        self.assertTrue(7, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file1.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory', 'sub.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file4.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file5.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4', 'file10') in paths)

    def test_fnmatch(self):
        """ Test fnmatch parameter."""
        # find all files and directories
        paths = pathfind(BASEPATH, fnmatch="*")
        self.assertEqual(22, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file1.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file2.dat') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file3.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.jpg') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'transparent_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory', 'sub.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file4.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file5.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file6.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file7.html') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', 'file8') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', '.file9') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4', 'file10') in paths)

        # find only files or directories with a .txt extension
        paths = pathfind(BASEPATH, fnmatch="*.txt")
        self.assertEqual(4, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'file1.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file3.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory', 'sub.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file4.txt') in paths)

    def test_all(self):
        """ Test with no parameters. """
        # find all paths
        paths = pathfind(BASEPATH)
        self.assertEqual(22, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file1.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file2.dat') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file3.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.jpg') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'transparent_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory', 'sub.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file4.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file5.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file6.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file7.html') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', 'file8') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', '.file9') in paths)

    def test_and(self):
        """ Test AndFilter."""
        # find directories with a 2 anywhere in the path
        filt = AndFilter(DirectoryFilter(), RegexFilter('.*2.*'))
        paths = pathfind(BASEPATH, filter=filt)
        self.assertEqual(1, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir2') in paths)

        # test overridden __and__
        filt = DirectoryFilter() & RegexFilter('.*2.*')
        paths_2 = pathfind(BASEPATH, filter=filt)
        self.assertEqual(paths, paths_2)

        # use Filter.find
        paths_3 = AndFilter(DirectoryFilter(), RegexFilter('.*2.*')).find(BASEPATH)
        self.assertEqual(paths, paths_3)

    def test_or(self):
        """ Test OrFilter."""
        # find all directories and any files (or directories)
        # with 2 in the path
        filt = OrFilter(DirectoryFilter(), RegexFilter('.*2.*'))
        paths = pathfind(BASEPATH, filter=filt)
        self.assertEqual(8, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file2.dat') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file6.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file7.html') in paths)

        # test overridden __or__
        filt = DirectoryFilter() | RegexFilter('.*2.*')
        paths_2 = pathfind(BASEPATH, filter=filt)
        self.assertEqual(paths, paths_2)

        # use Filter.find
        paths_3 = OrFilter(DirectoryFilter(), RegexFilter('.*2.*')).find(BASEPATH)
        self.assertEqual(paths, paths_3)

    def test_not(self):
        """ Test NotFilter."""
        # find all files and directories with a .txt extension
        # except ones that end in 3.txt
        filt = AndFilter(NotFilter(FnmatchFilter('*3.txt')), FnmatchFilter('*.txt'))
        paths = pathfind(BASEPATH, filter=filt)
        self.assertEqual(3, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'file1.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory', 'sub.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file4.txt') in paths)

    def test_ignore(self):
        """ Test ignore parameter."""
        # find all directories and all files and directories
        # with a 2 in the path and no directories that begin
        # with a dot
        filt = OrFilter(DirectoryFilter(), RegexFilter('.*2.*'))
        ignore = DotDirectoryFilter()
        paths = pathfind(BASEPATH, filter=filt, ignore=ignore)
        self.assertEqual(7, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file2.dat') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file6.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file7.html') in paths)

        filt = FnmatchFilter("*.txt")
        ignore = FnmatchFilter("*4.txt")

        all_paths = pathfind(BASEPATH, filter=filt)
        self.assertEqual(4, len(all_paths))
        self.assertTrue("4.txt" in " ".join(all_paths))

        ignore_paths = pathfind(BASEPATH, filter=filt, ignore=ignore)
        self.assertEqual(3, len(ignore_paths))
        self.assertFalse("4.txt" in " ".join(ignore_paths))

    def test_abspath(self):
        """ Make sure all paths are absolute paths."""
        cwd = os.getcwd()
        paths = pathfind(BASEPATH, filter=DirectoryFilter(), abspath=True)
        self.assertEqual(5, len(paths))
        self.assertTrue(os.path.join(cwd, BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(cwd, BASEPATH, 'dir1', 'subdirectory') in paths)
        self.assertTrue(os.path.join(cwd, BASEPATH, 'dir2') in paths)
        self.assertTrue(os.path.join(cwd, BASEPATH, 'dir3') in paths)
        self.assertTrue(os.path.join(cwd, BASEPATH, '.dir4') in paths)

        paths = pathfind(BASEPATH, just_files=True, abspath=True)
        self.assertEqual(17, len(paths))
        self.assertTrue(os.path.join(cwd, BASEPATH, 'python_logo.png') in paths)

    def test_depth(self):
        """ Only descend a certain depth into a tree."""
        paths = pathfind(BASEPATH, filter=DirectoryFilter(), depth=1)
        self.assertEqual(4, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4') in paths)

        paths = pathfind(BASEPATH, filter=DirectoryFilter(), depth=2)
        self.assertEqual(5, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory') in paths)

    def test_find_filepath(self):
        """ Test when the root path to a find is a file and not a directory. """
        a_paths = pathfind(os.path.join(BASEPATH, 'python_logo.png'), just_files=True)
        b_paths = pathfind(BASEPATH, just_files=True)
        self.assertEqual(a_paths, b_paths)

    def test_generator(self):
        """ Test with no parameters. """
        # find all paths
        paths = []
        for path in find_paths(BASEPATH):
            paths.append(path)
        self.assertEqual(22, len(paths))
        self.assertTrue(os.path.join(BASEPATH, 'dir1') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3') in paths)
        self.assertTrue(os.path.join(BASEPATH, '.dir4') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file1.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file2.dat') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'file3.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.gif') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.jpg') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'python_logo_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'transparent_gs.png') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'subdirectory', 'sub.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file4.txt') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir1', 'file5.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file6.log') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir2', 'file7.html') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', 'file8') in paths)
        self.assertTrue(os.path.join(BASEPATH, 'dir3', '.file9') in paths)

"""
pathfinder - making it easy to find paths
"""
import fnmatch
import os
import re

class Filter(object):

    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)

    def find(self, filepath):
        from radon.pathfinder import walk_and_filter
        return walk_and_filter(filepath, self)

class AlwaysAcceptFilter(Filter):
    """ Accept every path. """

    def accepts(self, _):
        """ Always returns True. """
        return True

class DirectoryFilter(Filter):
    """ Accept directory paths. """

    def accepts(self, filepath):
        """ Returns True if filepath represents a directory. """
        return os.path.isdir(filepath)

class FileFilter(Filter):
    """ Accept file paths. """

    def accepts(self, filepath):
        """ Returns True if filepath represents a file. """
        return os.path.isfile(filepath)

class RegexFilter(Filter):
    """ Accept paths if they match the specified regular expression. """

    def __init__(self, regex):
        """ Initialize the filter with the specified regular expression. """
        super(RegexFilter, self).__init__()
        self.regex = re.compile(regex)

    def accepts(self, filepath):
        """ Returns True if the regular expression matches the filepath. """
        return self.regex.match(filepath) is not None

class FnmatchFilter(Filter):
    """ Accept paths if they match the specifed fnmatch pattern. """

    def __init__(self, pattern):
        """ Initialize the filter with the specified fnmatch pattern. """
        super(FnmatchFilter, self).__init__()
        self.pattern = pattern

    def accepts(self, filepath):
        """ Returns True if the fnmatch pattern matches the filepath. """
        return fnmatch.fnmatch(filepath, self.pattern)

class AndFilter(Filter, list):
    """ Accept paths if all of it's filters accept the path. """

    def __init__(self, *args):
        """ Initialize the filter with the list of filters. """
        list.__init__(self, args)

    def accepts(self, filepath):
        """ Returns True if all of the filters in this filter return True. """
        return all(sub_filter.accepts(filepath) for sub_filter in self)

class OrFilter(Filter, list):
    """ Accept paths if any of it's filters accept the path. """

    def __init__(self, *args):
        """ Initialize the filter with the list of filters. """
        list.__init__(self, args)

    def accepts(self, filepath):
        """ Returns True if any of the filters in this filter return True. """
        return any(sub_filter.accepts(filepath) for sub_filter in self)

class NotFilter(Filter):
    """ Negate the accept of the specified filter. """

    def __init__(self, pathfilter):
        """ Initialize the filter with the filter it is to negate. """
        super(NotFilter, self).__init__()
        self.pathfilter = pathfilter

    def accepts(self, filepath):
        """ Returns True of the sub-filter returns False. """
        return not self.pathfilter.accepts(filepath)

class DotDirectoryFilter(AndFilter):
    """ Do not accept a path for a directory that begins with a period. """

    def __init__(self):
        """
        Initialise the filter to ignore directories beginning with
        a period.
        """
        super(DotDirectoryFilter, self).__init__(
                DirectoryFilter(),
                RegexFilter(r'.*%s*\..*$' % (os.sep)))

class SizeFilter(FileFilter):

    def __init__(self, max_bytes=None, min_bytes=None):
        self.file_filter = FileFilter()
        self.max_bytes = max_bytes
        self.min_bytes = min_bytes

    def accepts(self, filepath):
        if super(SizeFilter, self).accepts(filepath):
            stat = os.stat(filepath)
            if self.max_bytes is not None:
                if stat.st_size > self.max_bytes:
                    return False
            if self.min_bytes is not None:
                if stat.st_size < self.min_bytes:
                    return False
            return True
        return False

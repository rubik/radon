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
        from pathfinder import walk_and_filter
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

class ImageFilter(Filter):
    """ Accept paths for Image files. """

    def __init__(self):
        self.file_filter = OrFilter(
            FnmatchFilter("*.jpg"),
            FnmatchFilter("*.jpeg"),
            FnmatchFilter("*.png"),
            FnmatchFilter("*.gif"),
            FnmatchFilter("*.bmp"),
            FnmatchFilter("*.tiff")
        )

    def accepts(self, filepath):
        return self.file_filter.accepts(filepath)

class ImageDimensionFilter(ImageFilter):
    """ Accept paths for Image files. """

    def __init__(self, max_width=None, max_height=None, min_width=None, min_height=None):
        super(ImageDimensionFilter, self).__init__()

        if min_height is None:
            min_height = 0
        if min_width is None:
            min_width = 0

        self.max_width = max_width
        self.max_height = max_height
        self.min_width = min_width
        self.min_height = min_height

    def accepts(self, filepath):
        if super(ImageDimensionFilter, self).accepts(filepath):
            if self.min_height == 0 and self.min_width == 0 \
                and self.max_height is None and self.max_width is None:
                return True

            from PIL import Image
            image = Image.open(filepath)
            size = image.size
            if self.max_width and size[0] > self.max_width:
                return False
            if self.max_height and size[1] > self.max_height:
                return False
            if self.min_width and size[0] < self.min_width:
                return False
            if self.min_height and size[1] < self.min_height:
                return False
            return True
        return False

class GreyscaleImageFilter(ImageFilter):

    def accepts(self, filepath):
        if super(GreyscaleImageFilter, self).accepts(filepath):
            from PIL import Image
            from PIL import ImageStat

            image = Image.open(filepath)
            palette = image.getpalette()

            if palette:
                # GIF support
                return is_greyscale_palette(palette)
            else:
                s = ImageStat.Stat(image)

                # B&W JPEG
                if image.mode == "L":
                    return True
                return stdv(s.mean[:3]) < 1
        return False


class ColorImageFilter(ImageFilter):

    def accepts(self, filepath):
        if super(ColorImageFilter, self).accepts(filepath):
            from PIL import Image
            from PIL import ImageStat

            image = Image.open(filepath)
            palette = image.getpalette()

            if palette:
                # GIF SUPPORT
                return is_color_palette(palette)
            else:
                s = ImageStat.Stat(image)

                # B&W JPEG
                if image.mode == "L":
                    return False
                return stdv(s.mean[:3]) > 1
        return False

from math import sqrt

def stdv(x):
    n, _sum, mean, std = len(x), sum(x), 0, 0
    mean = _sum / float(n)
    sum_diff = sum([(a - mean) ** 2 for a in x])
    std = sqrt(sum_diff / float(n - 1))
    return std

def is_greyscale_palette(palette):
    for i in range(256):
        j = i * 3
        if palette[j] != palette[j+1] != palette[j+2]:
            return False
    return True

def is_color_palette(palette):
    return not is_greyscale_palette(palette)

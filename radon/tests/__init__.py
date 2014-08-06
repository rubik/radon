try:
    import unittest.util
except ImportError:  # Python 2.6 monkey-patching
    import sys
    import unittest2.util
    sys.modules['unittest.util'] = unittest2.util

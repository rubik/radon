if __name__ == '__main__':
    import sys
    import pytest

    pytest_args = ['--strict-markers']

    ret = pytest.main(pytest_args)
    sys.exit(ret)

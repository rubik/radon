if __name__ == '__main__':
    import pytest

    # see: https://docs.pytest.org/en/6.2.x/deprecations.html#the-strict-command-line-option
    # This check can be removed once Python 2.x support is dropped as the new
    # pytest option (--strict-markers) is available in pytest for all Python 3.x
    from packaging import version
    if version.parse(pytest.__version__) < version.parse('6.2'):
        pytest_args = ['--strict']
    else:
        pytest_args = ['--strict-markers']

    ret = pytest.main(pytest_args)
    exit(ret)

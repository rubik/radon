__version__ = '0.4.4'


def main():
    '''The entry point for Setuptools.'''
    from radon.cli import BAKER, log_error

    try:
        BAKER.run()
    except Exception as e:
        log_error(e)
        raise


if __name__ == '__main__':
    main()

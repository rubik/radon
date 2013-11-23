__version__ = '0.4.4'


def main():
    '''The entry point for Setuptools.'''
    from radon.cli import BAKER, log_error
    import mando

    try:
        #BAKER.run()
        mando.main()
    except Exception as e:
        log_error(e)
        raise


if __name__ == '__main__':
    main()

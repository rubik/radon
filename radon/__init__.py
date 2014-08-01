__version__ = '0.5.3'


def main():
    '''The entry point for Setuptools.'''
    import sys
    from radon.cli import program, log_error

    if not sys.argv[1:]:
        sys.argv.append('-h')
    try:
        program()
    except Exception as e:
        log_error(e)


if __name__ == '__main__':
    main()

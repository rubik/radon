__version__ = '0.5.1'


def main():
    '''The entry point for Setuptools.'''
    from radon.cli import program, log_error

    try:
        program()
    except Exception as e:
        log_error(e)


if __name__ == '__main__':
    main()

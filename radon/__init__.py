__version__ = '0.3.1'


def main():
    '''The entry point for Setuptools.'''
    from radon.cli import BAKER

    BAKER.run()


if __name__ == '__main__':
    main()

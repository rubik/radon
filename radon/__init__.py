__version__ = '0.4.3'


def main():
    '''The entry point for Setuptools.'''
    from radon.cli import BAKER

    BAKER.run()


if __name__ == '__main__':
    main()

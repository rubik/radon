__version__ = '0.1'


def main():
    from radon.cli import BAKER, colorama_init, colorama_deinit
    
    try:
        colorama_init()
        BAKER.run()
    finally:
        colorama_deinit()


if __name__ == '__main__':
    main()

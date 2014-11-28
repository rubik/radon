if __name__ == '__main__':
    import nose
    try:
        import rednose
    except ImportError:
        argv = None
    else:
        argv = ['nosetests', '--rednose', '--nocapture', '--pdb']
    nose.main(argv=argv)

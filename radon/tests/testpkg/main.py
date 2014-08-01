# from plumbum

class AtomicFile(object):
    """
    Atomic file operations implemented using file-system advisory locks (``flock`` on POSIX,
    ``LockFile`` on Windows).

    .. note::
        On Linux, the manpage says ``flock`` might have issues with NFS mounts. You should
        take this into account.

    .. versionadded:: 1.3
    """

    CHUNK_SIZE = 32 * 1024

    def __init__(self, filename, ignore_deletion = False):
        self.path = local.path(filename)
        self._ignore_deletion = ignore_deletion
        self._thdlock = threading.Lock()
        self._owned_by = None
        self._fileobj = None
        self.reopen()

    def __repr__(self):
        return "<AtomicFile: %s>" % (self.path,) if self._fileobj else "<AtomicFile: closed>"

    def __del__(self):
        self.close()
    def __enter__(self):
        return self
    def __exit__(self, t, v, tb):
        self.close()

    def close(self):
        if self._fileobj is not None:
            self._fileobj.close()
            self._fileobj = None

    def reopen(self):
        """
        Close and reopen the file; useful when the file was deleted from the file system
        by a different process
        """
        self.close()
        self._fileobj = os.fdopen(os.open(str(self.path), os.O_CREAT | os.O_RDWR, 384), "r+b", 0)

    @contextmanager
    def locked(self, blocking = True):
        """
        A context manager that locks the file; this function is reentrant by the thread currently
        holding the lock.

        :param blocking: if ``True``, the call will block until we can grab the file system lock.
                         if ``False``, the call may fail immediately with the underlying exception
                         (``IOError`` or ``WindowsError``)
        """
        if self._owned_by == threading.get_ident():
            yield
            return
        with self._thdlock:
            with locked_file(self._fileobj.fileno(), blocking):
                if not self.path.exists() and not self._ignore_deletion:
                    raise ValueError("Atomic file removed from filesystem")
                self._owned_by = threading.get_ident()
                try:
                    yield
                finally:
                    self._owned_by = None

    def delete(self):
        """
        Atomically delete the file (holds the lock while doing it)
        """
        with self.locked():
            self.path.delete()

    def _read_all(self):
        self._fileobj.seek(0)
        data = []
        while True:
            buf = self._fileobj.read(self.CHUNK_SIZE)
            data.append(buf)
            if len(buf) < self.CHUNK_SIZE:
                break
        return six.b("").join(data)

    def read_atomic(self):
        """Atomically read the entire file"""
        with self.locked():
            return self._read_all()

    def read_shared(self):
        """Read the file **without** holding the lock"""
        return self._read_all()

    def write_atomic(self, data):
        """Writes the given data atomically to the file. Note that it overwrites the entire file;
        ``write_atomic("foo")`` followed by ``write_atomic("bar")`` will result in only ``"bar"``.
        """
        with self.locked():
            self._fileobj.seek(0)
            while data:
                chunk = data[:self.CHUNK_SIZE]
                self._fileobj.write(chunk)
                data = data[len(chunk):]
            self._fileobj.flush()
            self._fileobj.truncate()

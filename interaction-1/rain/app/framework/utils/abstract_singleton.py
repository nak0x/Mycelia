# MicroPython-friendly Singleton (ESP32)
# - No `threading`
# - Uses `_thread.allocate_lock()` when available
# - Ensures __init__ logic runs only once

try:
    import _thread
    _SINGLETON_LOCK = _thread.allocate_lock()
except ImportError:
    # Fallback: no threading support in this build/port
    class _NoLock:
        def acquire(self): return True
        def release(self): return True
    _SINGLETON_LOCK = _NoLock()


class SingletonBase:
    _instance = None
    _inited = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            _SINGLETON_LOCK.acquire()
            try:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
            finally:
                _SINGLETON_LOCK.release()
        return cls._instance

    def __init__(self, *args, **kwargs):
        # Prevent re-running initialization if user calls Class() multiple times
        if self.__class__._inited:
            return
        _SINGLETON_LOCK.acquire()
        try:
            if not self.__class__._inited:
                # Put your one-time init in `_init_once`
                self._init_once(*args, **kwargs)
                self.__class__._inited = True
        finally:
            _SINGLETON_LOCK.release()

    def _init_once(self, *args, **kwargs):
        # Override in subclasses
        pass
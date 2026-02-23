"""Shared exceptions so base decompiler code does not import APK/Java-specific modules."""


class CorruptAPKException(Exception):
    """Raised when an APK file is detected as corrupt and cannot be processed."""
    pass


class CantDecompileJavaException(Exception):
    pass

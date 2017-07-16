# qpass: Frontend for pass (the standard unix password manager).
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: July 16, 2017
# URL: https://github.com/xolox/python-qpass

"""Custom exceptions raised by :mod:`qpass`."""

# Public identifiers that require documentation.
__all__ = (
    'EmptyPasswordStoreError',
    'MissingPasswordStoreError',
    'NoMatchingPasswordError',
    'PasswordStoreError',
)


class PasswordStoreError(Exception):

    """Base class for custom exceptions raised by :mod:`qpass`."""


class MissingPasswordStoreError(PasswordStoreError):

    """Raised when the password store directory doesn't exist."""


class EmptyPasswordStoreError(PasswordStoreError):

    """Raised when the password store is empty."""


class NoMatchingPasswordError(PasswordStoreError):

    """Raised when no matching password can be selected."""

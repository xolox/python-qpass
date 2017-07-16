# qpass: Frontend for pass (the standard unix password manager).
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: July 16, 2017
# URL: https://github.com/xolox/python-qpass

"""
Frontend for pass_, the standard unix password manager.

.. _pass: https://www.passwordstore.org/
"""

# Standard library modules.
import logging
import os
import platform
import re

# External dependencies.
from executor import execute
from executor.contexts import LocalContext
from humanfriendly import Timer, format_path, parse_path
from humanfriendly.terminal import HIGHLIGHT_COLOR, ansi_wrap, terminal_supports_colors
from humanfriendly.prompts import prompt_for_choice
from humanfriendly.text import concatenate, format, pluralize, split, trim_empty_lines
from natsort import natsort
from proc.gpg import get_gpg_variables
from property_manager import PropertyManager, cached_property, clear_property, mutable_property, set_property
from verboselogs import VerboseLogger

# Modules included in our package.
from qpass.exceptions import (
    EmptyPasswordStoreError,
    MissingPasswordStoreError,
    NoMatchingPasswordError,
)

# Public identifiers that require documentation.
__all__ = (
    'DEFAULT_DIRECTORY',
    'DIRECTORY_VARIABLE',
    'PasswordStore',
    '__version__',
    'create_fuzzy_pattern',
    'logger',
)

# Semi-standard module versioning.
__version__ = '1.0'

DEFAULT_DIRECTORY = '~/.password-store'
"""
The default password storage directory (a string).

The value of :data:`DEFAULT_DIRECTORY` is normalized using
:func:`~humanfriendly.parse_path()`.
"""

DIRECTORY_VARIABLE = 'PASSWORD_STORE_DIR'
"""The environment variable that sets the password storage directory (a string)."""

KEY_VALUE_PATTERN = re.compile(r'^(.+\S):\s+(\S.*)$')
"""A compiled regular expression to recognize "Key: Value" lines."""

# Initialize a logger for this module.
logger = VerboseLogger(__name__)


class PasswordStore(PropertyManager):

    """Python API for the `qpass` program."""

    @mutable_property(cached=True)
    def clipboard_enabled(self):
        """
        :data:`True` to use the clipboard, :data:`False` otherwise.

        This property is :data:`True` on macOS (when the output of
        :func:`platform.system()` is 'Darwin') or when the environment variable
        ``$DISPLAY`` is set, otherwise it defaults to :data:`False`.
        """
        return platform.system().lower() == 'darwin' or bool(os.environ.get('DISPLAY'))

    @mutable_property(cached=True)
    def context(self):
        """
        An execution context created using :mod:`executor.contexts`.

        The value of :attr:`context` defaults to a
        :class:`~executor.contexts.LocalContext` object with the following
        characteristics:

        - The working directory of the execution context is set to the
          value of :attr:`directory`.

        - The environment variable given by :data:`DIRECTORY_VARIABLE` is set
          to the value of :attr:`directory`.

        :raises: :exc:`.MissingPasswordStoreError` when :attr:`directory`
                 doesn't exist.
        """
        # Make sure the directory exists.
        self.ensure_directory_exists()
        # Prepare the environment variables.
        environment = {DIRECTORY_VARIABLE: self.directory}
        try:
            # Try to enable the GPG agent in headless sessions.
            environment.update(get_gpg_variables())
        except Exception:
            # If we failed then let's at least make sure that the
            # $GPG_TTY environment variable is set correctly.
            environment.update(GPG_TTY=execute('tty', capture=True, tty=True, silent=True))
        return LocalContext(directory=self.directory, environment=environment)

    @mutable_property(cached=True)
    def directory(self):
        """
        The pathname of the password storage directory (a string).

        When the environment variable given by :data:`DIRECTORY_VARIABLE` is
        set the value of that environment variable is used, otherwise
        :data:`DEFAULT_DIRECTORY` is used. In either case the resulting
        directory pathname is normalized using
        :func:`~humanfriendly.parse_path()`.

        When you set the :attr:`directory` property, the value you set will be
        normalized using :func:`~humanfriendly.parse_path()` and the computed
        value of the :attr:`context` property is cleared.
        """
        return parse_path(os.environ.get(DIRECTORY_VARIABLE, DEFAULT_DIRECTORY))

    @directory.setter
    def directory(self, value):
        """Normalize the value of :attr:`directory` when it's set."""
        # Normalize the value of `directory'.
        set_property(self, 'directory', parse_path(value))
        # Clear the computed values of `context' and `entries'.
        clear_property(self, 'context')
        clear_property(self, 'entries')

    @cached_property
    def entries(self):
        """The names of the passwords stored in :attr:`directory` (a list of strings)."""
        timer = Timer()
        passwords = []
        logger.info("Scanning %s ..", format_path(self.directory))
        listing = self.context.capture('find', '-type', 'f', '-name', '*.gpg', '-print0')
        for filename in split(listing, '\0'):
            basename, extension = os.path.splitext(filename)
            if extension == '.gpg':
                # We use os.path.normpath() to remove the leading `./' prefixes
                # that `find' adds because it searches the working directory.
                passwords.append(os.path.normpath(basename))
        logger.verbose("Found %s in %s.", pluralize(len(passwords), "password"), timer)
        return natsort(passwords)

    def copy_password(self, name):
        """
        Copy a password to the clipboard.

        :param name: The name of the entry (a string).

        The password is only copied when :attr:`clipboard_enabled` is
        :data:`True`.
        """
        if self.clipboard_enabled:
            self.context.execute('pass', 'show', '--clip', name)

    def ensure_directory_exists(self):
        """
        Make sure :attr:`directory` exists.

        :raises: :exc:`.MissingPasswordStoreError` when the password storage
                 directory doesn't exist.
        """
        if not os.path.isdir(self.directory):
            msg = "The password storage directory doesn't exist! (%s)"
            raise MissingPasswordStoreError(msg % self.directory)

    def get_text(self, name):
        """
        Get the text of an entry in the password store.

        :param name: The name of the entry (a string).
        :returns: The entry's text (a string).
        """
        return self.context.capture('pass', 'show', name)

    def get_password(self, name):
        """
        Get the password of an entry in the password store.

        :param name: The name of the entry (a string).
        :returns: The entry's password (a string).
        """
        text = self.get_text(name)
        lines = text.splitlines()
        return lines[0]

    def format_entry(self, name, use_colors=None):
        """
        Format an entry's text for viewing on a terminal.

        :param name: The name of the entry (a string).
        :param use_colors: :data:`True` to use ANSI escape sequences,
                           :data:`False` otherwise. When this is :data:`None`
                           :func:`~humanfriendly.terminal.terminal_supports_colors()`
                           will be used to detect whether ANSI escape sequences
                           are supported.
        :returns: The formatted entry (a string).
        """
        # Determine whether we can use ANSI escape sequences.
        if use_colors is None:
            use_colors = terminal_supports_colors()
        # Get the entry's text.
        entry = self.get_text(name)
        # Extract the password (first line) from the entry.
        lines = entry.splitlines()
        password = lines.pop(0).strip()
        entry = trim_empty_lines('\n'.join(lines))
        # Show the password only when the clipboard is disabled.
        if not self.clipboard_enabled:
            entry = "Password: %s\n%s" % (password, entry)
        # Add the name to the entry (only when there's something to show).
        if entry and not entry.isspace():
            title = ' / '.join(split(name, '/'))
            if use_colors:
                title = ansi_wrap(title, bold=True)
            entry = "%s\n\n%s" % (title, entry)
        # Highlight the entry's text using ANSI escape sequences.
        lines = []
        for line in entry.splitlines():
            # Check for a "Key: Value" line.
            match = KEY_VALUE_PATTERN.match(line)
            if match:
                key = "%s:" % match.group(1).strip()
                value = match.group(2).strip()
                if use_colors:
                    # Highlight the key.
                    key = ansi_wrap(key, color=HIGHLIGHT_COLOR)
                    # Underline hyperlinks in the value.
                    tokens = value.split()
                    for i in range(len(tokens)):
                        if '://' in tokens[i]:
                            tokens[i] = ansi_wrap(tokens[i], underline=True)
                    # Replace the line with a highlighted version.
                    line = key + ' ' + ' '.join(tokens)
            lines.append('  ' + line)
        return '\n%s\n' % '\n'.join(lines)

    def fuzzy_search(self, *filters):
        """
        Perform a "fuzzy" search that matches the given characters in the given order.

        :param filters: The pattern(s) to search for.
        :returns: The matched password names (a list of strings).
        """
        matches = []
        logger.verbose("Performing fuzzy search on %s (%s) ..",
                       pluralize(len(filters), "pattern"),
                       concatenate(map(repr, filters)))
        patterns = list(map(create_fuzzy_pattern, filters))
        for passwd in self.entries:
            if all(p.search(passwd) for p in patterns):
                matches.append(passwd)
        logger.log(logging.INFO if matches else logging.VERBOSE,
                   "Matched %s using fuzzy search.", pluralize(len(matches), "password"))
        return matches

    def select_entry(self, *arguments):
        """
        Select a password from the available choices.

        :param arguments: Refer to :func:`smart_search()`.
        :returns: The name of a password (a string) or :data:`None`
                  (when no password matched the given `arguments`).
        """
        matches = self.smart_search(*arguments)
        if len(matches) > 1:
            logger.info("More than one match, prompting for choice ..")
            return prompt_for_choice(matches)
        else:
            logger.info("Matched one entry: %s", matches[0])
            return matches[0]

    def simple_search(self, *keywords):
        """
        Perform a simple search for case insensitive substring matches.

        :param keywords: The string(s) to search for.
        :returns: The matched password names (a generator of strings).

        Only passwords whose names matches *all*  of the given keywords are
        returned.
        """
        matches = []
        keywords = [kw.lower() for kw in keywords]
        logger.verbose("Performing simple search on %s (%s) ..",
                       pluralize(len(keywords), "keyword"),
                       concatenate(map(repr, keywords)))
        for passwd in self.entries:
            normalized = passwd.lower()
            if all(kw in normalized for kw in keywords):
                matches.append(passwd)
        logger.log(logging.INFO if matches else logging.VERBOSE,
                   "Matched %s using simple search.", pluralize(len(matches), "password"))
        return matches

    def smart_search(self, *arguments):
        """
        Perform a smart search on the given keywords or patterns.

        :param arguments: The keywords or patterns to search for.
        :returns: The matched password names (a list of strings).
        :raises: The following exceptions can be raised:

                 - :exc:`.NoMatchingPasswordError` when no matching passwords are found.
                 - :exc:`.EmptyPasswordStoreError` when the password store is empty.

        This method first tries :func:`simple_search()` and if that doesn't
        produce any matches it will fall back to :func:`fuzzy_search()`. If no
        matches are found an exception is raised (see above).
        """
        matches = self.simple_search(*arguments)
        if not matches:
            logger.verbose("Falling back from substring search to fuzzy search ..")
            matches = self.fuzzy_search(*arguments)
        if not matches:
            if len(self.entries) > 0:
                raise NoMatchingPasswordError(format(
                    "No passwords matched the given arguments! (%s)",
                    concatenate(map(repr, arguments)),
                ))
            else:
                raise EmptyPasswordStoreError(format(
                    "You don't have any passwords yet! (no *.gpg files found in %s)",
                    format_path(self.directory),
                ))
        return matches


def create_fuzzy_pattern(pattern):
    """
    Convert a string into a fuzzy regular expression pattern.

    :param pattern: The input pattern (a string).
    :returns: A compiled regular expression object.

    This function works by adding ``.*`` between each of the characters in the
    input pattern and compiling the resulting expression into a case
    insensitive regular expression.
    """
    return re.compile('.*'.join(map(re.escape, pattern)), re.IGNORECASE)

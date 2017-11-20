# Test suite for the `qpass' Python package.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: November 20, 2017
# URL: https://github.com/xolox/python-qpass

"""Test suite for the `qpass` package."""

# Standard library modules.
import logging
import os
import platform

# External dependencies.
from humanfriendly.testing import (
    CaptureOutput,
    MockedHomeDirectory,
    MockedProgram,
    PatchedAttribute,
    PatchedItem,
    TemporaryDirectory,
    TestCase,
    random_string,
    run_cli,
    touch,
)
from humanfriendly.terminal import ansi_strip
from humanfriendly.text import dedent
from property_manager import set_property

# The module we're testing.
import qpass
from qpass import DIRECTORY_VARIABLE, PasswordEntry, PasswordStore, is_clipboard_supported
from qpass.cli import main
from qpass.exceptions import (
    EmptyPasswordStoreError,
    MissingPasswordStoreError,
    NoMatchingPasswordError,
)

# Initialize a logger for this module.
logger = logging.getLogger(__name__)


class QuickPassTestCase(TestCase):

    """:mod:`unittest` compatible container for `qpass` tests."""

    def test_cli_defaults(self):
        """Test default password store discovery in command line interface."""
        with MockedHomeDirectory() as home:
            touch(os.path.join(home, '.password-store', 'the-only-entry.gpg'))
            returncode, output = run_cli(main, '-l')
            assert returncode == 0
            entries = output.splitlines(False)
            assert entries == ['the-only-entry']

    def test_cli_invalid_option(self):
        """Test error handling of invalid command line options."""
        returncode, output = run_cli(main, '-x', merged=True)
        assert returncode != 0
        assert "Error:" in output

    def test_cli_list(self):
        """Test the output of ``qpass --list``."""
        with TemporaryDirectory() as directory:
            touch(os.path.join(directory, 'foo.gpg'))
            touch(os.path.join(directory, 'foo/bar.gpg'))
            touch(os.path.join(directory, 'Also with spaces.gpg'))
            returncode, output = run_cli(main, '--password-store=%s' % directory, '--list')
            assert returncode == 0
            entries = output.splitlines()
            assert 'foo' in entries
            assert 'foo/bar' in entries
            assert 'Also with spaces' in entries

    def test_cli_usage(self):
        """Test the command line usage message."""
        for options in [], ['-h'], ['--help']:
            returncode, output = run_cli(main, *options)
            assert "Usage:" in output

    def test_clipboard_enabled(self):
        """Test the detection whether the clipboard should be used."""
        # Make sure the clipboard is enabled by default on macOS.
        if platform.system().lower() == 'darwin':
            assert is_clipboard_supported() is True
        else:
            # Make sure the clipboard is used when $DISPLAY is set.
            with PatchedItem(os.environ, 'DISPLAY', ':0'):
                assert is_clipboard_supported() is True
            # Make sure the clipboard is not used when $DISPLAY isn't set.
            environment = os.environ.copy()
            environment.pop('DISPLAY', None)
            with PatchedAttribute(os, 'environ', environment):
                assert is_clipboard_supported() is False

    def test_directory_variable(self):
        """Test support for ``$PASSWORD_STORE_DIR``."""
        with TemporaryDirectory() as directory:
            with PatchedItem(os.environ, DIRECTORY_VARIABLE, directory):
                program = PasswordStore()
                assert program.directory == directory

    def test_edit_entry(self):
        """Test editing of an entry on the command line."""
        # Create a fake password store that we can test against.
        with TemporaryDirectory() as directory:
            touch(os.path.join(directory, 'Personal', 'Zabbix.gpg'))
            touch(os.path.join(directory, 'Work', 'Zabbix.gpg'))
            # Make sure we're not running the real `pass' program because its
            # intended purpose is user interaction, which has no place in an
            # automated test suite :-).
            with MockedProgram('pass'):
                returncode, output = run_cli(
                    main,
                    '--password-store=%s' % directory,
                    '--edit',
                    'p/z',
                    merged=True,
                )
                assert returncode == 0
                assert 'Matched one entry: Personal/Zabbix' in output

    def test_empty_password_store_error(self):
        """Test the EmptyPasswordStoreError exception."""
        with TemporaryDirectory() as directory:
            program = PasswordStore(directory=directory)
            self.assertRaises(EmptyPasswordStoreError, program.smart_search)

    def test_format_text(self):
        """Test human friendly formatting of password store entries."""
        entry = PasswordEntry(name='some/random/password', store=object())
        set_property(entry, 'text', random_string())
        self.assertEquals(
            # We enable ANSI escape sequences but strip them before we
            # compare the generated string. This may seem rather pointless
            # but it ensures that the relevant code paths are covered :-).
            dedent(ansi_strip(entry.format_text(include_password=True, use_colors=True))),
            dedent('''
                some / random / password

                Password: {value}
            ''', value=entry.text))

    def test_fuzzy_search(self):
        """Test fuzzy searching."""
        with TemporaryDirectory() as directory:
            touch(os.path.join(directory, 'Personal/Zabbix.gpg'))
            touch(os.path.join(directory, 'Work/Zabbix.gpg'))
            touch(os.path.join(directory, 'Something else.gpg'))
            program = PasswordStore(directory=directory)
            # Test a fuzzy search with multiple matches.
            matches = program.fuzzy_search('zbx')
            assert len(matches) == 2
            assert any(entry.name == 'Personal/Zabbix' for entry in matches)
            assert any(entry.name == 'Work/Zabbix' for entry in matches)
            # Test a fuzzy search with a single match.
            matches = program.fuzzy_search('p/z')
            assert len(matches) == 1
            assert matches[0].name == 'Personal/Zabbix'
            # Test a fuzzy search with `the other' match.
            matches = program.fuzzy_search('w/z')
            assert len(matches) == 1
            assert matches[0].name == 'Work/Zabbix'

    def test_get_password(self):
        """Test getting a password from an entry."""
        random_password = random_string()
        entry = PasswordEntry(name='some/random/password', store=object())
        set_property(entry, 'text', '\n'.join([random_password, '', 'This is the description']))
        self.assertEquals(random_password, entry.password)

    def test_missing_password_store_error(self):
        """Test the MissingPasswordStoreError exception."""
        with TemporaryDirectory() as directory:
            missing = os.path.join(directory, 'missing')
            program = PasswordStore(directory=missing)
            self.assertRaises(MissingPasswordStoreError, program.ensure_directory_exists)

    def test_no_matching_password_error(self):
        """Test the NoMatchingPasswordError exception."""
        with TemporaryDirectory() as directory:
            touch(os.path.join(directory, 'Whatever.gpg'))
            program = PasswordStore(directory=directory)
            self.assertRaises(NoMatchingPasswordError, program.smart_search, 'x')

    def test_password_discovery(self):
        """Test password discovery."""
        with TemporaryDirectory() as directory:
            touch(os.path.join(directory, 'foo.gpg'))
            touch(os.path.join(directory, 'foo/bar.gpg'))
            touch(os.path.join(directory, 'foo/bar/baz.gpg'))
            touch(os.path.join(directory, 'Also with spaces.gpg'))
            program = PasswordStore(directory=directory)
            assert len(program.entries) == 4
            assert program.entries[0].name == 'Also with spaces'
            assert program.entries[1].name == 'foo'
            assert program.entries[2].name == 'foo/bar'
            assert program.entries[3].name == 'foo/bar/baz'

    def test_select_entry(self):
        """Test password selection."""
        with TemporaryDirectory() as directory:
            touch(os.path.join(directory, 'foo.gpg'))
            touch(os.path.join(directory, 'bar.gpg'))
            touch(os.path.join(directory, 'baz.gpg'))
            program = PasswordStore(directory=directory)
            # Substring search.
            entry = program.select_entry('fo')
            assert entry.name == 'foo'
            # Fuzzy search.
            entry = program.select_entry('bz')
            assert entry.name == 'baz'

    def test_select_entry_interactive(self):
        """Test interactive password selection."""
        with TemporaryDirectory() as directory:
            touch(os.path.join(directory, 'foo.gpg'))
            touch(os.path.join(directory, 'bar.gpg'))
            touch(os.path.join(directory, 'baz.gpg'))
            # Select entries using the command line filter 'a' and then use
            # interactive selection to narrow the choice down to 'baz' by
            # specifying the unique substring 'z'.
            program = PasswordStore(directory=directory)
            with CaptureOutput(input='z'):
                entry = program.select_entry('a')
                assert entry.name == 'baz'

    def test_show_entry(self):
        """Test showing of an entry on the terminal."""
        password = random_string()
        # Some voodoo to mock methods in classes that
        # have yet to be instantiated follows :-).
        mocked_class = type(
            'TestPasswordEntry',
            (PasswordEntry,),
            dict(text=password),
        )
        with PatchedAttribute(qpass, 'PasswordEntry', mocked_class):
            with TemporaryDirectory() as directory:
                name = 'some/random/password'
                touch(os.path.join(directory, '%s.gpg' % name))
                returncode, output = run_cli(
                    main,
                    '--password-store=%s' % directory,
                    '--no-clipboard',
                    name,
                )
                assert returncode == 0
                assert dedent(output) == dedent(
                    """
                    {title}

                    Password: {password}
                    """,
                    title=name.replace('/', ' / '),
                    password=password,
                )

    def test_simple_search(self):
        """Test simple substring searching."""
        with TemporaryDirectory() as directory:
            touch(os.path.join(directory, 'foo.gpg'))
            touch(os.path.join(directory, 'bar.gpg'))
            touch(os.path.join(directory, 'baz.gpg'))
            program = PasswordStore(directory=directory)
            matches = program.simple_search('fo')
            assert len(matches) == 1
            assert matches[0].name == 'foo'
            matches = program.simple_search('a')
            assert len(matches) == 2
            assert matches[0].name == 'bar'
            assert matches[1].name == 'baz'
            matches = program.simple_search('b', 'z')
            assert len(matches) == 1
            assert matches[0].name == 'baz'

    def test_smart_search(self):
        """Test smart searching."""
        with TemporaryDirectory() as directory:
            touch(os.path.join(directory, 'abcdef.gpg'))
            touch(os.path.join(directory, 'aabbccddeeff.gpg'))
            touch(os.path.join(directory, 'Google.gpg'))
            program = PasswordStore(directory=directory)
            # Test a substring match that avoids fuzzy matching.
            matches = program.smart_search('abc')
            assert len(matches) == 1
            assert matches[0].name == 'abcdef'
            # Test a fuzzy match to confirm that the fall back works.
            matches = program.smart_search('gg')
            assert len(matches) == 1
            assert matches[0].name == 'Google'

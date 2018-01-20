# qpass: Frontend for pass (the standard unix password manager).
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: November 20, 2017
# URL: https://github.com/xolox/python-qpass

"""
Usage: qpass [OPTIONS] KEYWORD..

Search your password store for the given keywords or patterns and copy the
password of the matching entry to the clipboard. When more than one entry
matches you will be prompted to select the password to copy.

If you provide more than one KEYWORD all of the given keywords must match,
in other words you're performing an AND search instead of an OR search.

Instead of matching on keywords you can also enter just a few of the characters
in the name of a password, as long as those characters are in the right order.
Some examples to make this more concrete:

- The pattern 'pe/zbx' will match the name 'Personal/Zabbix'.
- The pattern 'ba/cc' will match the name 'Bank accounts/Creditcard'.

Supported options:

  -e, --edit

    Edit the matching entry instead of copying it to the clipboard.

  -l, --list

    List the matching entries on standard output.

  -n, --no-clipboard

    Don't copy the password of the matching entry to the clipboard, instead
    show the password on the terminal (by default the password is copied to
    the clipboard but not shown on the terminal).

  -p, --password-store=DIRECTORY

    Search the password store in DIRECTORY. If this option isn't given
    the password store is located using the $PASSWORD_STORE_DIR
    environment variable. If that environment variable isn't
    set the directory ~/.password-store is used.

    You can use the -p, --password-store option multiple times to search more
    than one password store at the same time. No distinction is made between
    passwords in different password stores, so the names of passwords need to
    be recognizable and unique.

  -s, --show-pass

    Show passwords and any extended information in terminal.

  -v, --verbose

    Increase logging verbosity (can be repeated).

  -q, --quiet

    Decrease logging verbosity (can be repeated).

  -h, --help

    Show this message and exit.
"""

# Standard library modules.
import getopt
import logging
import sys

# External dependencies.
import coloredlogs
from humanfriendly.terminal import output, usage, warning

# Modules included in our package.
from qpass import PasswordStore, QuickPass, is_clipboard_supported
from qpass.exceptions import PasswordStoreError

# Public identifiers that require documentation.
__all__ = (
    'edit_matching_entry',
    'list_matching_entries',
    'logger',
    'main',
    'show_matching_entry',
)

# Initialize a logger for this module.
logger = logging.getLogger(__name__)


def main():
    """Command line interface for the ``qpass`` program."""
    # Initialize logging to the terminal.
    coloredlogs.install()
    # Prepare for command line argument parsing.
    action = show_matching_entry
    program_opts = dict()
    show_opts = dict(use_clipboard=is_clipboard_supported(), show_pass=False)
    # Parse the command line arguments.
    try:
        options, arguments = getopt.gnu_getopt(sys.argv[1:], 'elnsp:vqh', [
            'edit', 'list', 'no-clipboard', 'show-pass', 'password-store=',
            'verbose', 'quiet', 'help',
        ])
        for option, value in options:
            if option in ('-e', '--edit'):
                action = edit_matching_entry
            elif option in ('-l', '--list'):
                action = list_matching_entries
            elif option in ('-n', '--no-clipboard'):
                show_opts['use_clipboard'] = False
            elif option in ('-s', '--show_pass'):
                show_opts['show_pass'] = True
            elif option in ('-p', '--password-store'):
                stores = program_opts.setdefault('stores', [])
                stores.append(PasswordStore(directory=value))
            elif option in ('-v', '--verbose'):
                coloredlogs.increase_verbosity()
            elif option in ('-q', '--quiet'):
                coloredlogs.decrease_verbosity()
            elif option in ('-h', '--help'):
                usage(__doc__)
                return
            else:
                raise Exception("Unhandled option! (programming error)")
        if not (arguments or action == list_matching_entries):
            usage(__doc__)
            return
    except Exception as e:
        warning("Error: %s", e)
        sys.exit(1)
    # Execute the requested action.
    try:
        action(QuickPass(**program_opts), arguments,
               **(show_opts if action == show_matching_entry else {}))
    except PasswordStoreError as e:
        # Known issues don't get a traceback.
        logger.error("%s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        # If the user interrupted an interactive prompt they most likely did so
        # intentionally, so there's no point in generating more output here.
        sys.exit(1)


def edit_matching_entry(program, arguments):
    """Edit the matching entry."""
    entry = program.select_entry(*arguments)
    entry.context.execute('pass', 'edit', entry.name)


def list_matching_entries(program, arguments):
    """List the entries matching the given keywords/patterns."""
    output('\n'.join(entry.name for entry in program.smart_search(*arguments)))


def show_matching_entry(program, arguments, use_clipboard=True, show_pass=False):
    """Show the matching entry on the terminal (and copy the password to the clipboard)."""
    entry = program.select_entry(*arguments)
    formatted_entry = entry.format_text(include_password=not use_clipboard)
    if formatted_entry and not formatted_entry.isspace() and show_pass:
        output(formatted_entry)
    if use_clipboard:
        entry.copy_password()

Changelog
=========

The purpose of this document is to list all of the notable changes to this
project. The format was inspired by `Keep a Changelog`_. This project adheres
to `semantic versioning`_.

.. contents::
   :local:

.. _Keep a Changelog: http://keepachangelog.com/
.. _semantic versioning: http://semver.org/

`Release 2.3`_ (2018-12-03)
---------------------------

Add support for exclude lists (``qpass -x`` or ``qpass --exclude=GLOB``).

Explaining how I got here requires a bit of context:

- For several years now I've been using `Google Authenticator`_ for two-factor
  authentication (2FA) to online services like GitHub and Trello. Unfortunately
  Google Authenticator is quite bare bones in that it doesn't allow to export
  the configured 2FA accounts, which implies that switching phones requires
  resetting the 2FA configuration of a dozen online services...

- As a workaround you can store the "account configuration token" (the text
  behind the QR code that you scan) that's available when an account is
  configured in a secure location (`explanation available here`_). This
  explains why I recently decided to reinitialize the 2FA configuration of all
  my online accounts (one last time 😛) so that I can store the tokens in my
  password store.

- My 2FA tokens are encrypted with a separate, dedicated GPG key pair (with a
  stronger password) to ensure that the password to each online service is
  unlocked with a different secret than the 2FA token (so as not to completely
  undermine the second factor).

- So now whenever I run something like ``qpass github`` I get offered two
  matches and I need to make a choice, even though that choice will always be
  the same (the 2FA tokens are stored only as backups).

- Thanks to this qpass release I'm now able to configure the alias ``qpass
  --exclude='*2fa*'`` in my ``~/.zshrc`` so that I never have to be bothered by
  the entries containing the 2FA tokens again 😇.

.. _Release 2.3: https://github.com/xolox/python-qpass/compare/2.2.1...2.3
.. _Google Authenticator: https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2
.. _explanation available here: https://android.stackexchange.com/a/183010/273993

`Release 2.2.1`_ (2018-06-21)
-----------------------------

Bumped ``proc`` requirement to version 0.15 to pull in an upstream bug fix
for hanging Travis CI builds caused by ``gpg-agent`` not detaching to the
background properly because the standard error stream was redirected.

Lots of improvements were made to the ``proc.gpg`` module in proc release 0.15
and I consider the GPG agent functionality to be *quite* relevant for
``qpass``, so this warrants a bug fix release.

.. _Release 2.2.1: https://github.com/xolox/python-qpass/compare/2.2...2.2.1

`Release 2.2`_ (2018-04-26)
---------------------------

- Added this changelog.
- Added ``license`` key to ``setup.py`` script.

.. _Release 2.2: https://github.com/xolox/python-qpass/compare/2.1...2.2

`Release 2.1`_ (2018-01-20)
---------------------------

The focus of this release was on hiding of sensitive details (fixes `#1`_):

- Made ``qpass --quiet`` hide password entry details (related to `#1`_).
- Made ``qpass -f ignore ...`` hide specific details (related to `#1`_).
- Shuffled text processing order in format_entry()
- Included documentation in source distributions.

.. _Release 2.1: https://github.com/xolox/python-qpass/compare/2.0.2...2.1
.. _#1: https://github.com/xolox/python-qpass/issues/1

`Release 2.0.2`_ (2017-11-20)
-----------------------------

Bug fix for default password store discovery in CLI.

.. _Release 2.0.2: https://github.com/xolox/python-qpass/compare/2.0.1...2.0.2

`Release 2.0.1`_ (2017-07-27)
-----------------------------

Minor bug fixes (update ``__all__``, fix heading in ``README.rst``).

.. _Release 2.0.1: https://github.com/xolox/python-qpass/compare/2.0...2.0.1

`Release 2.0`_ (2017-07-27)
---------------------------

Added support for multiple password stores.

.. _Release 2.0: https://github.com/xolox/python-qpass/compare/1.0.3...2.0

`Release 1.0.3`_ (2017-07-18)
-----------------------------

Bug fix for previous commit :-).

.. _Release 1.0.3: https://github.com/xolox/python-qpass/compare/1.0.2...1.0.3

`Release 1.0.2`_ (2017-07-18)
-----------------------------

Bug fix: Don't print superfluous whitespace for 'empty' entries.

.. _Release 1.0.2: https://github.com/xolox/python-qpass/compare/1.0.1...1.0.2

`Release 1.0.1`_ (2017-07-16)
-----------------------------

Bug fix: Ignore failing ``tty`` commands.

.. _Release 1.0.1: https://github.com/xolox/python-qpass/compare/1.0...1.0.1

`Release 1.0`_ (2017-07-16)
---------------------------

Initial commit and release.

.. _Release 1.0: https://github.com/xolox/python-qpass/tree/1.0

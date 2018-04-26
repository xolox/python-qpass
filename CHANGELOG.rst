Changelog
=========

The purpose of this document is to list all of the notable changes to this
project. The format was inspired by `Keep a Changelog`_. This project adheres
to `semantic versioning`_.

.. contents::
   :local:

.. _Keep a Changelog: http://keepachangelog.com/
.. _semantic versioning: http://semver.org/

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

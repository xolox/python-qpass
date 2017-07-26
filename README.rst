qpass: Frontend for pass (the standard unix password manager)
=============================================================

.. image:: https://travis-ci.org/xolox/python-qpass.svg?branch=master
   :target: https://travis-ci.org/xolox/python-qpass

.. image:: https://coveralls.io/repos/xolox/python-qpass/badge.svg?branch=master
   :target: https://coveralls.io/r/xolox/python-qpass?branch=master

The qpass program is a simple command line frontend for pass_, the standard
unix password manager. It makes it very easy to quickly find and copy specific
passwords in your ``~/.password-store`` to the clipboard. The package is
currently tested on cPython 2.6, 2.7, 3.4, 3.5, 3.6 and PyPy (2.7). It's
intended to work on Linux as well as macOS, although it has only been tested on
Linux.

.. contents::
   :local:

Installation
------------

The qpass package is available on PyPI_ which means installation should be as
simple as:

.. code-block:: sh

   $ pip install qpass

There's actually a multitude of ways to install Python packages (e.g. the `per
user site-packages directory`_, `virtual environments`_ or just installing
system wide) and I have no intention of getting into that discussion here, so
if this intimidates you then read up on your options before returning to these
instructions ;-).

Usage
-----

There are two ways to use the qpass package: As the command line program
``qpass`` and as a Python API. For details about the Python API please refer to
the API documentation available on `Read the Docs`_. The command line interface
is described below.

Command line
~~~~~~~~~~~~

.. A DRY solution to avoid duplication of the `qpass --help' text:
..
.. [[[cog
.. from humanfriendly.usage import inject_usage
.. inject_usage('qpass.cli')
.. ]]]

**Usage:** `qpass [OPTIONS] KEYWORD..`

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

**Supported options:**

.. csv-table::
   :header: Option, Description
   :widths: 30, 70


   "``-e``, ``--edit``",Edit the matching entry instead of copying it to the clipboard.
   "``-l``, ``--list``",List the matching entries on standard output.
   "``-n``, ``--no-clipboard``","Don't copy the password of the matching entry to the clipboard, instead
   show the password on the terminal (by default the password is copied to
   the clipboard but not shown on the terminal)."
   "``-p``, ``--password-store=DIRECTORY``","Search the password store in ``DIRECTORY``. If this option isn't given
   the password store is located using the ``$PASSWORD_STORE_DIR``
   environment variable. If that environment variable isn't
   set the directory ~/.password-store is used.
   
   You can use the ``-p``, ``--password-store`` option multiple times to search
   multiple password stores as if they were one."
   "``-v``, ``--verbose``",Increase logging verbosity (can be repeated).
   "``-q``, ``--quiet``",Decrease logging verbosity (can be repeated).
   "``-h``, ``--help``",Show this message and exit.

.. [[[end]]]

Why use pass?
-------------

In 2016 I was looking for a way to securely share passwords and other secrets
between my laptops and smartphones. I'm not going to bore you with the full
details of my quest to find the ultimate password manager but I can highlight a
few points about pass_ that are important to me:

.. contents::
   :local:

GPG encryption
~~~~~~~~~~~~~~

GPG_ is a cornerstone of computer security and it's open source. This means it
receives quite a lot of peer review, which makes it easier for me to trust
(versus do-it-yourself_ cryptography). Because pass_ uses GPG_ to implement its
encryption my trust extends directly to pass_. Of course it also helps that I
had years of experience with GPG_ before I started using pass_ :-).

Git version control
~~~~~~~~~~~~~~~~~~~

The git_ integration in pass_ makes it very easy to keep your passwords under
version control and synchronize the passwords between multiple systems. Git_ is
a great version control system and while I sometimes get annoyed by the fact
that ``git pull`` automatically merges, it's actually the perfect default
choice for a password store. As an added bonus you have a history of every
change you ever made to your passwords.

SSH secure transport
~~~~~~~~~~~~~~~~~~~~

I've been using SSH_ to access remote systems over secure connections for *a
very long time* now so I'm quite comfortable setting up and properly securing
SSH servers. In the case of pass_ I use SSH to synchronize my passwords between
my laptops and smartphones via a central server that hosts the private git
repository.

History
-------

Shortly after starting to use pass_ I realized that I needed a quick and easy
way to copy any given password to the clipboard, something smarter than the
pass_ program.

I tried out several GUI frontends but to be honest each of them felt clumsy, I
guess that through my work as a system administrator and programmer I've grown
to prefer command line interfaces over graphical user interfaces :-). For a few
weeks I tried upass_ (a somewhat fancy command line interface) but the lack of
simple things like case insensitive search made me stop using it.

Out of frustration I hacked together a simple Python script that would perform
case insensitive substring searches on my passwords, copying the password to
the clipboard when there was exactly one match. I called the Python script
qpass, thinking that it was similar in purpose to upass_ but much quicker
for me to use, so `q` (for quick) instead of `u`.

After using that Python script for a while I noticed that case insensitive
substring searching still forced me to specify long and detailed patterns in
order to get a unique match. Experimenting with other ways to match unique
passwords I came up with the idea of performing a "fuzzy match" against the
pathname of the password (including the directory components). The fuzzy
searching where a pattern like ``e/z`` matches ``Personal/Zabbix`` has since
become my primary way of interacting with my password stores.

About the name
~~~~~~~~~~~~~~

As explained above I initially wrote and named qpass with no intention of ever
publishing it. However since then my team at work has started using pass_ to
manage a shared pasword store and ever since we started doing that I've missed
the ability to query that password store using qpass :-).

Publishing qpass as an open source project with a proper Python package
available on PyPI_ provides a nice way to share qpass with my team and it also
forces me to maintain proper documentation and an automated test suite.

While considering whether to publish qpass I found that there's an existing
password manager out there called `QPass <http://qpass.sourceforge.net/>`_.
I decided not to rename my project for the following reasons:

- While both projects are password managers, they are intended for very
  different audiences (I'm expecting my end users to be power users that are
  most likely system administrators and/or programmers).

- I consider the name of the executable of a GUI program to be a lot less
  relevant than the name of the executable of a command line program. This is
  because the GUI will most likely be started via an application launcher,
  which means the executable doesn't even need to be on the ``$PATH``.

- Let's be honest, pass_ is already for power users only, so my qpass frontend
  is most likely not going to see a lot of users ;-).

Future improvements
-------------------

One great aspect of pass_ is the git_ integration that makes it easy to share a
password store between several devices [#]_ or people [#]_. This use case makes
it much more likely that you'll end up using multiple password stores, which is
something that pass_ doesn't specifically make easy. It would be nice if qpass
can be configured to query more than one password store in a single invocation.
As long as the passwords are "unique enough" I should be able to make it work
as if though the password stores are one.

.. [#] For example I synchronize my password store between my personal laptop
       and my work laptop and I also have access to my password store on my
       smartphones (thanks to the Android application `Password Store`_).

.. [#] My team at work also uses pass_ so because I was already using pass_ for
       personal use, I now find myself frequently searching through multiple
       password stores.

Contact
-------

The latest version of qpass is available on PyPI_ and GitHub_. The
documentation is hosted on `Read the Docs`_. For bug reports please create an
issue on GitHub_. If you have questions, suggestions, etc. feel free to send me
an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2017 Peter Odding.

.. External references:

.. _do-it-yourself: https://security.stackexchange.com/a/18198
.. _git: https://en.wikipedia.org/wiki/Git
.. _GitHub: https://github.com/xolox/python-qpass
.. _GPG: https://en.wikipedia.org/wiki/GNU_Privacy_Guard
.. _Linux: https://en.wikipedia.org/wiki/Linux
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _pass: https://www.passwordstore.org/
.. _Password Store: https://play.google.com/store/apps/details?id=com.zeapo.pwdstore
.. _per user site-packages directory: https://www.python.org/dev/peps/pep-0370/
.. _peter@peterodding.com: peter@peterodding.com
.. _PyPI: https://pypi.python.org/pypi/qpass
.. _Python Package Index: https://pypi.python.org/pypi/qpass
.. _Python: https://www.python.org/
.. _Read the Docs: https://qpass.readthedocs.org
.. _SSH: https://en.wikipedia.org/wiki/Secure_Shell
.. _upass: https://pypi.python.org/pypi/upass
.. _virtual environments: http://docs.python-guide.org/en/latest/dev/virtualenvs/

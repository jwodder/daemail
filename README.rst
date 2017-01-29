.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active - The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://img.shields.io/pypi/pyversions/daemail.svg
    :target: https://pypi.python.org/pypi/daemail

.. image:: https://img.shields.io/github/license/jwodder/daemail.svg?maxAge=2592000
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/daemail>`_
| `PyPI <https://pypi.python.org/pypi/daemail>`_
| `Issues <https://github.com/jwodder/daemail/issues>`_

``daemail`` (pronounced "DEE-mayl", like "e-mail" but with a D) is a Python
script for running a normally-foreground command in the background and
e-mailing its output (by default, the combined stdout and stderr) once it's
done.  It should work in both Python 2.7 and Python 3.2+, the only external
dependencies being the `python-daemon
<https://pypi.python.org/pypi/python-daemon>`_ package and the ubiquitous `six
<https://pypi.python.org/pypi/six>`_ package.


Installation
============

Just use `pip <https://pip.pypa.io/>`_ (You have pip, right?) to install
``daemail`` and its dependencies::

    pip install daemail


Usage
=====

::

    daemail [-C|--chdir <directory>]
            [-D|--dead-letter <mbox>]
            [-e|--encoding <encoding>]
            [-E|--stderr-encoding <encoding>]
            [-f|--from|--from-addr <address>]
            [-F|--failure-only]
            [-l|--logfile <logfile>]
            [-M|--mime-type|--mime <mime-type>]
            [-n|--nonempty]
            [--no-stdout]
            [--no-stderr]
            [-S|--split]
            [--stdout-filename <filename>]
            [-Z|--utc]
            -t|--to|--to-addr <address>  [-t|--to|--to-addr <address> ...]
            [<send options>]
            <command> [<arg> ...]

where ``<send options>`` is one of::

    -s|--sendmail <command>  # default

    --mbox <mbox>

    --smtp-host <host>
        [--smtp-port <port>]
        [--smtp-username <username>]
        [--smtp-password <password> | --smtp-password-file <file> | --netrc | --netrc-file <file>]
        [--smtp-ssl | --smtp-starttls]


Options
-------

- ``-C <directory>``, ``--chdir <directory>`` — Change to ``<directory>`` after
  daemonizing but before running ``<command>``; defaults to the current
  directory

- ``-D <mbox>``, ``--dead-letter <mbox>`` — If an error occurs when trying to
  send, append the e-mail (including a description of the error) to the file
  ``<mbox>``; defaults to ``dead.letter``.  If the file already exists, it must
  be a valid mbox file.

- ``-e <encoding>``, ``--encoding <encoding>`` — Expect the stdout (and stderr,
  if ``--split`` is not in effect) of ``<command>`` to be in the given
  encoding; defaults to the preferred encoding returned by Python's
  |getpreferredencoding|_.  If decoding fails, the output will be attached to
  the e-mail as an ``application/octet-stream`` file named "``stdout``".

  When ``--mime-type`` or ``--stdout-filename`` is also given, this option has
  no effect other than to set the default value for ``--stderr-encoding``.

- ``-E <encoding>``, ``--stderr-encoding <encoding>`` — Expect the stderr of
  ``<command>`` to be in the given encoding; defaults to the value specified
  via ``--encoding`` or its default.  If decoding fails, the stderr output will
  be attached to the e-mail as an ``application/octet-stream`` file named
  "``stderr``".

  This option only has an effect when ``--split`` is given, either implicitly
  or explicitly.

- ``-f <address>``, ``--from <address>``, ``--from-addr <address>`` — Set the
  ``From:`` address of the e-mail.  The address may be given in either the form
  "``address@example.com``" or "``Real Name <address@example.com>``."  If not
  specified, ``daemail`` will not set the ``From:`` header and will expect the
  mail command or SMTP server to do it instead.

- ``--from-name <name>`` — Deprecated; set the "real name" in the argument to
  ``--from-addr`` instead

- ``-F``, ``--failure-only`` — Only send an e-mail if the command failed to run
  or exited with a nonzero status

- ``-l <logfile>``, ``--logfile <logfile>`` — If an unexpected & unhandleable
  fatal error occurs after daemonization, append a report to ``<logfile>``;
  defaults to ``daemail.log``

  - Such an error is a deficiency in the program; please report it!

- ``-s <command>``, ``--sendmail <command>`` — Send e-mail by passing the
  message on stdin to ``<command>`` (executed via the shell, in the directory
  specified with ``--chdir`` or its default); default command: ``sendmail -i
  -t``.  This is the default if neither ``--mbox`` nor ``--smtp-host`` is
  specified.

- ``--mbox <mbox>`` — "Send" e-mail by appending it to the mbox file ``<mbox>``

- ``-M <mime-type>``, ``--mime-type <mime-type>``, ``--mime <mime-type>`` —
  Attach the standard output of ``<command>`` to the e-mail as an inline
  attachment with the given MIME type.  The MIME type may include parameters,
  e.g., ``--mime-type "text/html; charset=utf-16"``.  If ``--stdout-filename``
  is not also supplied, the attachment is named "``stdout``".  Implies
  ``--split``.

- ``-n``, ``--nonempty`` — Do not send an e-mail if the command exited
  successfully and both the command's stdout & stderr were empty or not
  captured

- ``--no-stdout`` — Don't capture the command's stdout; implies ``--split``

- ``--no-stderr`` — Don't capture the command's stderr; implies ``--split``

- ``--smtp-host <host>`` — Send e-mail via SMTP, connecting to the given host.
  ``--smtp-host`` may be accompanied by the following options:

  - ``--smtp-port <port>`` — Connect to ``<host>`` on the given port; defaults
    to 25, or to 465 if ``--smtp-ssl`` is specified

  - ``--smtp-username <username>`` — Authenticate to the SMTP server using the
    given username.  If a username is supplied (either on the command line or
    in a netrc file) but no password is, ``daemail`` will prompt the user for
    the SMTP password before daemonizing.

  - ``--smtp-password <password>`` — Authenticate to the SMTP server using the
    given password

  - ``--smtp-password-file <file>`` — Authenticate to the SMTP server using the
    contents of the given file (after removing the final line ending) as the
    password

  - ``--netrc`` — Fetch the SMTP username and/or password from ``~/.netrc``.
    If ``--smtp-username`` specifies a different username for the host than is
    given in the netrc file, the netrc file is ignored.

  - ``--netrc-file <file>`` — Like ``--netrc``, but use the given file instead
    of ``~/.netrc``

  - ``--smtp-ssl`` — Use the SMTPS protocol to communicate with the server

  - ``--smtp-starttls`` — Use the SMTP protocol with the STARTTLS extension to
    communicate with the server

- ``-S``, ``--split`` — Capture the command's stdout and stderr separately
  rather than as a single stream

- ``--stdout-filename <filename>`` — Attach the standard output of
  ``<command>`` to the e-mail as an inline attachment with the given filename.
  If ``--mime-type`` is not also supplied, the MIME type of the attachment is
  deduced from the file extension, falling back to ``application/octet-stream``
  for unknown extensions.  Implies ``--split``.

- ``-t <address>``, ``--to <address>``, ``--to-addr <address>`` — Set the
  recipient of the e-mail.  The address may be given in either the form
  "``address@example.com``" or "``Real Name <address@example.com>``."

  - This option is required.  It may be given multiple times in order to
    specify multiple recipients.

- ``--to-name <name>`` — Deprecated; set the "real name" in the argument to
  ``--to-addr`` instead

- ``-Z``, ``--utc`` — Show start & end times in UTC instead of local time


Caveats
=======
- Input cannot be piped to the command, as standard input is closed when
  daemonizing.  If you really need to pass data on standard input, run a shell,
  e.g.::

    daemail bash -c 'command < file'

  or::

    daemail bash -c 'command | other-command'


.. |getpreferredencoding| replace:: ``locale.getpreferredencoding``
.. _getpreferredencoding: https://docs.python.org/3/library/locale.html#locale.getpreferredencoding

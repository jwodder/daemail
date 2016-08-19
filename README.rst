.. |repostatus| image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active - The project has reached a stable, usable
          state and is being actively developed.

.. |license| image:: https://img.shields.io/github/license/jwodder/daemail.svg?maxAge=2592000
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

|repostatus| |license|

``daemail`` (pronounced "DEE-mayl", like "e-mail" but with a D) is a Python
script for running a command in the background and sending an e-mail with its
output (by default, the combined stdout and stderr) once it's done.  It should
work in both Python 2.7 and Python 3.2+, the only external dependencies being
`the python-daemon package <https://pypi.python.org/pypi/python-daemon>`_ and
the ubiquitous `six package <https://pypi.python.org/pypi/six>`_.


Usage
=====

::

    daemail [--chdir <directory>]
            [-D|--dead-letter <file>]
            [-e|--encoding <encoding>]
            [-E|--err-encoding <encoding>]
            [-f|--from|--from-addr|--sender <address>]
            [-F|--failure-only]
            [-l|--logfile <logfile>]
            [-m|--mail-cmd <command>]
            [-M|--mime-type|--mime <mime-type>]
            [-n|--nonempty]
            [--no-stdout]
            [--no-stderr]
            [--smtp-host <host>]
            [--smtp-port <port>]
            [--smtp-username <username>]
            [--smtp-password <password>]
            [--smtp-ssl | --smtp-starttls]
            [--split]
            [-t|--to|--to-addr|--recipient|--rcpt <address>]
            [-Z|--utc]
            <command> [<arg> ...]

Options
-------

- ``--chdir <directory>`` — Change to ``<directory>`` before running
  ``<command>``

- ``-D <file>``, ``--dead-letter <file>`` — If an error occurs when trying to
  send, append the e-mail (including a description of the error) to ``<file>``;
  defaults to ``dead.letter`` in the current directory or the directory
  specified with ``--chdir``

- ``-e <encoding>``, ``--encoding <encoding>`` — Expect the stdout (and stderr,
  if ``--split`` is not in effect) of ``<command>`` to be in the given
  encoding; defaults to the preferred encoding returned by Python's
  |getpreferredencoding|_.  If decoding fails, the output will be attached to
  the e-mail as an ``application/octet-stream`` file.

  When ``--mime-type`` is also given, this option has no effect other than to
  set the default value for ``--err-encoding``.

- ``-E <encoding>``, ``--err-encoding <encoding>`` — Expect the stderr of
  ``<command>`` to be in the given encoding; defaults to the value specified
  via ``--encoding`` or its default.  If decoding fails, the stderr output will
  be attached to the e-mail as an ``application/octet-stream`` file.

  This option only has an effect when ``--split`` is given, either implicitly
  or explicitly.

- ``-f <address>``, ``--from <address>``, ``--from-addr <address>``, ``--sender
  <address>`` — Set the ``From:`` address of the e-mail.  If not specified,
  ``daemail`` will not set the ``From:`` header and will expect the mail
  command to do it instead.

- ``-F``, ``--failure-only`` — Only send an e-mail if the command exited with a
  nonzero status

- ``-l <logfile>``, ``--logfile <logfile>`` — If an unexpected & unhandleable
  fatal error occurs after daemonization, append a report to ``<logfile>``;
  defaults to ``daemail.log`` in the current directory or the directory
  specified with ``--chdir``

  - Such an error is a deficiency in the program; please report it!

- ``-m <command>``, ``--mail-cmd <command>`` — Send e-mail by passing the
  message on stdin to ``<command>`` (executed via the shell); default command:
  ``sendmail -t``

  ``--mail-cmd`` and ``--smtp-host`` are mutually exclusive.

- ``-M <mime-type>``, ``--mime-type <mime-type>``, ``--mime <mime-type>`` —
  Attach the standard output of ``<command>`` to the e-mail as an inline
  attachment with the given MIME type.  The MIME type may include parameters,
  e.g., ``--mime-type "application/json; charset=utf-16"``.  Implies
  ``--split``.

- ``-n``, ``--nonempty`` — Do not send an e-mail if the command exited
  successfully with no output

- ``--no-stdout`` — Don't capture the command's stdout; implies ``--split``

- ``--no-stderr`` — Don't capture the command's stderr; implies ``--split``

- ``--smtp-host <host>`` — Send e-mail via SMTP, connecting to the given host.
  When this option is not given, e-mail is instead sent using the command
  specified via ``--mail-cmd`` or its default.

  ``--smtp-host`` and ``--mail-cmd`` are mutually exclusive.

  ``--smtp-host`` may be accompanied by the following options:

  - ``--smtp-port <port>`` — Connect to ``<host>`` on the given port; defaults
    to 25, or to 465 if ``--smtp-ssl`` is specified

  - ``--smtp-username <username>`` — Authenticate to the SMTP server using the
    given username; must be accompanied by ``--smtp-password``

  - ``--smtp-password <username>`` — Authenticate to the SMTP server using the
    given password

  - ``--smtp-ssl`` — Use the SMTPS protocol to communicate with the server

  - ``--smtp-starttls`` — Use the SMTP protocol with the STARTTLS extension to
    communicate with the server

- ``--split`` — Capture the command's stdout and stderr separately rather than
  as a single stream

- ``-t <address>``, ``--to <address>``, ``--to-addr <address>``, ``--recipient
  <address>``, ``--rcpt <address>`` — Set the recipient of the e-mail; defaults
  to the current user (no host)

- ``-Z``, ``--utc`` — Show start & end times in UTC instead of local time


.. |getpreferredencoding| replace:: ``locale.getpreferredencoding``
.. _getpreferredencoding: https://docs.python.org/3/library/locale.html#locale.getpreferredencoding

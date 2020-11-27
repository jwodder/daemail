.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active - The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://github.com/jwodder/daemail/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/daemail/actions?workflow=Test
    :alt: CI Status

.. image:: https://codecov.io/gh/jwodder/daemail/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/daemail

.. image:: https://img.shields.io/pypi/pyversions/daemail.svg
    :target: https://pypi.org/project/daemail

.. image:: https://img.shields.io/github/license/jwodder/daemail.svg?maxAge=2592000
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/daemail>`_
| `PyPI <https://pypi.org/project/daemail>`_
| `Issues <https://github.com/jwodder/daemail/issues>`_
| `Changelog <https://github.com/jwodder/daemail/blob/master/CHANGELOG.md>`_

``daemail`` (pronounced "DEE-mayl", like "e-mail" but with a D) is a Python
script built on top of `python-daemon
<https://pypi.org/project/python-daemon>`_ for running a normally-foreground
command in the background and e-mailing its output (by default, the combined
stdout and stderr) once it's done.


Installation
============

``daemail`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install
``daemail`` and its dependencies::

    python3 -m pip install daemail


Usage
=====

::

    daemail [-C|--chdir <directory>]
            [-D|--dead-letter <mbox>]
            [-e|--encoding <encoding>]
            [-E|--stderr-encoding <encoding>]
            [--foreground|--fg]
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

-C DIR, --chdir DIR     Change to ``DIR`` after daemonizing but before running
                        the command; defaults to the current directory

-D MBOX, --dead-letter MBOX
                        If an error occurs when trying to send, append the
                        e-mail (including a description of the error) to the
                        file ``MBOX``; defaults to ``dead.letter``.  If the
                        file already exists, it must be a valid mbox file.

-e ENCODING, --encoding ENCODING
                        Expect the stdout (and stderr, if ``--split`` is not in
                        effect) of the command to be in the given encoding;
                        defaults to the preferred encoding returned by Python's
                        |getpreferredencoding|_.  If decoding fails, the output
                        will be attached to the e-mail as an
                        ``application/octet-stream`` file named "``stdout``".

                        When ``--mime-type`` or ``--stdout-filename`` is also
                        given, this option has no effect other than to set the
                        default value for ``--stderr-encoding``.

-E ENCODING, --stderr-encoding ENCODING
                        Expect the stderr of the command to be in the given
                        encoding; defaults to the value specified via
                        ``--encoding`` or its default.  If decoding fails, the
                        stderr output will be attached to the e-mail as an
                        ``application/octet-stream`` file named "``stderr``".

                        This option only has an effect when ``--split`` is
                        given, either implicitly or explicitly.

--foreground, --fg      Run everything in the foreground instead of
                        daemonizing.  Note that command output will still be
                        captured rather than displayed.

-f ADDRESS, --from ADDRESS, --from-addr ADDRESS
                        Set the ``From:`` address of the e-mail.  The address
                        may be given in either the form
                        "``address@example.com``" or "``Real Name
                        <address@example.com>``."  If not specified,
                        ``daemail`` will not set the ``From:`` header and will
                        expect the mail command or SMTP server to do it
                        instead.

-F, --failure-only      Only send an e-mail if the command failed to run or
                        exited with a nonzero status

-l LOGFILE, --logfile LOGFILE
                        If an unexpected & unhandleable fatal error occurs
                        after daemonization, append a report to LOGFILE;
                        defaults to ``daemail.log``

                        Such an error is a deficiency in the program; please
                        report it!

-s COMMAND, --sendmail COMMAND
                        Send e-mail by passing the message on stdin to
                        ``COMMAND`` (executed via the shell, in the directory
                        specified with ``--chdir`` or its default); default
                        command: ``sendmail -i -t``.  This is the default if
                        neither ``--mbox`` nor ``--smtp-host`` is specified.

--mbox MBOX             "Send" e-mail by appending it to the mbox file ``MBOX``

-M MIME-TYPE, --mime-type MIME-TYPE, --mime MIME-TYPE
                        Attach the standard output of the command to the
                        e-mail as an inline attachment with the given MIME
                        type.  The MIME type may include parameters, e.g.,
                        ``--mime-type "text/html; charset=utf-16"``.  If
                        ``--stdout-filename`` is not also supplied, the
                        attachment is named "``stdout``".  Implies ``--split``.

-n, --nonempty          Do not send an e-mail if the command exited
                        successfully and both the command's stdout & stderr
                        were empty or not captured

--no-stdout             Don't capture the command's stdout; implies ``--split``

--no-stderr             Don't capture the command's stderr; implies ``--split``

--smtp-host HOST        Send e-mail via SMTP, connecting to the given host.
                        See "`SMTP Options`_" for options for further
                        configuring the SMTP connection.

-S, --split             Capture the command's stdout and stderr separately
                        rather than as a single stream

--stdout-filename FILENAME
                        Attach the standard output of the command to the e-mail
                        as an inline attachment with the given filename.  If
                        ``--mime-type`` is not also supplied, the MIME type of
                        the attachment is deduced from the file extension,
                        falling back to ``application/octet-stream`` for
                        unknown extensions.  Implies ``--split``.

-t ADDRESS, --to ADDRESS, --to-addr ADDRESS
                        Set the recipient of the e-mail.  The address may be
                        given in either the form "``address@example.com``" or
                        "``Real Name <address@example.com>``."

                        This option is required.  It may be given multiple
                        times in order to specify multiple recipients.

-Z, --utc               Show start & end times in UTC instead of local time


SMTP Options
^^^^^^^^^^^^

When ``--smtp-host`` is specified on the command line, these options may be
specified as well in order to further configure the SMTP connection:

--netrc                 Fetch the SMTP username and/or password from
                        ``~/.netrc``.  If ``--smtp-username`` specifies a
                        different username for the host than is given in the
                        netrc file, the netrc file is ignored.

--netrc-file FILE       Like ``--netrc``, but use the given file instead of
                        ``~/.netrc``

--smtp-password PASSWORD
                        Authenticate to the SMTP server using the given
                        password

--smtp-password-file FILE
                        Authenticate to the SMTP server using the contents of
                        the given file (after removing the final line ending)
                        as the password

--smtp-port PORT        Connect to the SMTP host on the given port; defaults
                        to 25, or to 465 if ``--smtp-ssl`` is specified

--smtp-ssl              Use the SMTPS protocol to communicate with the server

--smtp-starttls         Use the SMTP protocol with the STARTTLS extension to
                        communicate with the server

--smtp-username USERNAME
                        Authenticate to the SMTP host using the given username.
                        If a username is supplied (either on the command line
                        or in a netrc file) but no password is, ``daemail``
                        will prompt the user for the SMTP password before
                        daemonizing.


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

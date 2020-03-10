from   datetime             import datetime, timedelta, timezone
from   email.headerregistry import Address
from   email.message        import EmailMessage
import signal
import pytest
from   daemail              import util
from   daemail.message      import DraftMessage, USER_AGENT
from   daemail.reporter     import CommandReporter
from   daemail.runner       import CommandError, CommandResult

w4 = timezone(timedelta(hours=-4))

@pytest.mark.parametrize('result,subject,body', [
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'',
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
        '> This is the output.\n',
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'',
            stderr = b'',
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output: none\n'
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'This is the stderr.\n',
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
        '> This is the output.\n'
        '\n'
        'Error Output:\n'
        '> This is the stderr.\n'
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'',
            stderr = b'This is the stderr.\n',
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output: none\n'
        '\n'
        'Error Output:\n'
        '> This is the stderr.\n'
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = None,
            stderr = b'This is the stderr.\n',
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Error Output:\n'
        '> This is the stderr.\n'
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = None,
            stderr = None,
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 42,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'',
        ),
        '[FAILED] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 42\n'
        '\n'
        'Output:\n'
        '> This is the output.\n',
    ),
    pytest.param(
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = -2,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'',
        ),
        '[FAILED] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: -2 (SIGINT)\n'
        '\n'
        'Output:\n'
        '> This is the output.\n',
        marks=pytest.mark.skipif(
            getattr(signal, 'SIGINT', None) != 2,
            reason='SIGINT is not 2 on this platform',
        ),
    ),
    pytest.param(
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = -65,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'',
        ),
        '[FAILED] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: -65\n'
        '\n'
        'Output:\n'
        '> This is the output.\n',
        marks=pytest.mark.skipif(
            any(s.value == 65 for s in signal.Signals),
            reason='This platform has a signal #65',
        ),
    ),
])
def test_report_plain_message(mocker, result, subject, body):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = False,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = False,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = False,
    )
    show_argv_spy = mocker.spy(util, 'show_argv')
    msg = reporter.report(result)
    assert isinstance(msg, DraftMessage)
    assert msg.headers == {
        "To": to_addrs,
        "Subject": subject,
        "User-Agent": USER_AGENT,
        "From": from_addr,
    }
    assert msg.parts == [body]
    show_argv_spy.assert_called_once_with(*result.argv)

@pytest.mark.parametrize('failure_only', [False, True])
@pytest.mark.parametrize('nonempty', [False, True])
def test_report_command_error(mocker, monkeypatch, failure_only, nonempty):
    monkeypatch.setattr(
        CommandError,
        'format_traceback',
        lambda _: 'Traceback (most recent call last):\n'
                  '    ...\n'
                  "FakeError: Let's pretend this really happened\n"
    )
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    result = CommandError(
        argv     = ['foo', '-x', 'bar.txt'],
        start    = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
        end      = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
        exc_info = None,
    )
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = failure_only,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = nonempty,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = False,
    )
    show_argv_spy = mocker.spy(util, 'show_argv')
    msg = reporter.report(result)
    assert isinstance(msg, DraftMessage)
    assert msg.headers == {
        "To": to_addrs,
        "Subject": '[ERROR] foo -x bar.txt',
        "User-Agent": USER_AGENT,
        "From": from_addr,
    }
    assert msg.parts == [
        'An error occurred while attempting to run the command:\n'
        '> Traceback (most recent call last):\n'
        '>     ...\n'
        "> FakeError: Let's pretend this really happened\n"
    ]
    show_argv_spy.assert_called_once_with(*result.argv)

def test_report_stdout_mime(mocker):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    result = CommandResult(
        argv = ['foo', '-x', 'bar.txt'],
        rc = 0,
        start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
        end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
        stdout = b'{"This": "is the output."}\n',
        stderr = b'',
    )
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = False,
        from_addr       = from_addr,
        mime_type       = 'application/json',
        nonempty        = False,
        stderr_encoding = 'utf-8',
        stdout_filename = 'stdout.html',
        to_addrs        = to_addrs,
        utc             = False,
    )
    show_argv_spy = mocker.spy(util, 'show_argv')
    msg = reporter.report(result)
    assert isinstance(msg, DraftMessage)
    assert msg.headers == {
        "To": to_addrs,
        "Subject": '[DONE] foo -x bar.txt',
        "User-Agent": USER_AGENT,
        "From": from_addr,
    }
    assert len(msg.parts) == 2
    assert msg.parts[0] == (
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
    )
    assert isinstance(msg.parts[1], EmailMessage)
    assert msg.parts[1].get_content() == b'{"This": "is the output."}\n'
    assert msg.parts[1].get_content_disposition() == 'inline'
    assert msg.parts[1].get_content_type() == 'application/json'
    assert msg.parts[1].get_filename() == 'stdout.html'
    ### TODO: Somehow fetch the Content-Type params and assert they are {}
    show_argv_spy.assert_called_once_with(*result.argv)

@pytest.mark.parametrize('result,subject,body', [
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'',
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
        '> This is the output.\n',
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'',
            stderr = b'',
        ),
        None,
        None,
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'This is the stderr.\n',
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
        '> This is the output.\n'
        '\n'
        'Error Output:\n'
        '> This is the stderr.\n'
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'',
            stderr = b'This is the stderr.\n',
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output: none\n'
        '\n'
        'Error Output:\n'
        '> This is the stderr.\n'
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = None,
            stderr = b'This is the stderr.\n',
        ),
        '[DONE] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Error Output:\n'
        '> This is the stderr.\n'
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = None,
            stderr = None,
        ),
        None,
        None,
    ),
])
def test_report_nonempty(result, subject, body):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = False,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = True,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = False,
    )
    msg = reporter.report(result)
    if body is None:
        assert msg is None
    else:
        assert isinstance(msg, DraftMessage)
        assert msg.headers == {
            "To": to_addrs,
            "Subject": subject,
            "User-Agent": USER_AGENT,
            "From": from_addr,
        }
        assert msg.parts == [body]

@pytest.mark.parametrize('result,subject,body', [
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 0,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'',
        ),
        None,
        None,
    ),
    (
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = 42,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'',
        ),
        '[FAILED] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 42\n'
        '\n'
        'Output:\n'
        '> This is the output.\n',
    ),
    pytest.param(
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = -2,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'',
        ),
        '[FAILED] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: -2 (SIGINT)\n'
        '\n'
        'Output:\n'
        '> This is the output.\n',
        marks=pytest.mark.skipif(
            getattr(signal, 'SIGINT', None) != 2,
            reason='SIGINT is not 2 on this platform',
        ),
    ),
    pytest.param(
        CommandResult(
            argv = ['foo', '-x', 'bar.txt'],
            rc = -65,
            start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
            end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
            stdout = b'This is the output.\n',
            stderr = b'',
        ),
        '[FAILED] foo -x bar.txt',
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: -65\n'
        '\n'
        'Output:\n'
        '> This is the output.\n',
        marks=pytest.mark.skipif(
            any(s.value == 65 for s in signal.Signals),
            reason='This platform has a signal #65',
        ),
    ),
])
def test_report_failure_only(result, subject, body):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = True,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = False,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = False,
    )
    msg = reporter.report(result)
    if body is None:
        assert msg is None
    else:
        assert isinstance(msg, DraftMessage)
        assert msg.headers == {
            "To": to_addrs,
            "Subject": subject,
            "User-Agent": USER_AGENT,
            "From": from_addr,
        }
        assert msg.parts == [body]

def test_report_utc(mocker):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    result = CommandResult(
        argv = ['foo', '-x', 'bar.txt'],
        rc = 0,
        start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
        end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
        stdout = b'This is the output.\n',
        stderr = b'',
    )
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = False,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = False,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = True,
    )
    show_argv_spy = mocker.spy(util, 'show_argv')
    msg = reporter.report(result)
    assert isinstance(msg, DraftMessage)
    assert msg.headers == {
        "To": to_addrs,
        "Subject": '[DONE] foo -x bar.txt',
        "User-Agent": USER_AGENT,
        "From": from_addr,
    }
    assert msg.parts == [
        'Start Time:  2020-03-10 19:00:28.123456Z\n'
        'End Time:    2020-03-10 19:01:27.654321Z\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
        '> This is the output.\n',
    ]
    show_argv_spy.assert_called_once_with(*result.argv)

@pytest.mark.parametrize('stderr', [b'', None])
def test_report_undecodable_stdout_empty_stderr(mocker, stderr):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    result = CommandResult(
        argv = ['foo', '-x', 'bar.txt'],
        rc = 0,
        start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
        end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
        stdout = b'\xD0is is i\xF1 L\xE1tin\xB9.\n',
        stderr = stderr,
    )
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = False,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = False,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = False,
    )
    show_argv_spy = mocker.spy(util, 'show_argv')
    msg = reporter.report(result)
    assert isinstance(msg, DraftMessage)
    assert msg.headers == {
        "To": to_addrs,
        "Subject": '[DONE] foo -x bar.txt',
        "User-Agent": USER_AGENT,
        "From": from_addr,
    }
    assert len(msg.parts) == 2
    assert msg.parts[0] == (
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
    )
    assert isinstance(msg.parts[1], EmailMessage)
    assert msg.parts[1].get_content() == b'\xD0is is i\xF1 L\xE1tin\xB9.\n'
    assert msg.parts[1].get_content_disposition() == 'inline'
    assert msg.parts[1].get_content_type() == 'application/octet-stream'
    assert msg.parts[1].get_filename() == 'stdout'
    ### TODO: Somehow fetch the Content-Type params and assert they are {}
    show_argv_spy.assert_called_once_with(*result.argv)

def test_report_undecodable_stdout_good_stderr(mocker):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    result = CommandResult(
        argv = ['foo', '-x', 'bar.txt'],
        rc = 0,
        start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
        end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
        stdout = b'\xD0is is i\xF1 L\xE1tin\xB9.\n',
        stderr = b'This is in ASCII.\n',
    )
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = False,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = False,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = False,
    )
    show_argv_spy = mocker.spy(util, 'show_argv')
    msg = reporter.report(result)
    assert isinstance(msg, DraftMessage)
    assert msg.headers == {
        "To": to_addrs,
        "Subject": '[DONE] foo -x bar.txt',
        "User-Agent": USER_AGENT,
        "From": from_addr,
    }
    assert len(msg.parts) == 3
    assert msg.parts[0] == (
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
    )
    assert isinstance(msg.parts[1], EmailMessage)
    assert msg.parts[1].get_content() == b'\xD0is is i\xF1 L\xE1tin\xB9.\n'
    assert msg.parts[1].get_content_disposition() == 'inline'
    assert msg.parts[1].get_content_type() == 'application/octet-stream'
    assert msg.parts[1].get_filename() == 'stdout'
    ### TODO: Somehow fetch the Content-Type params and assert they are {}
    assert msg.parts[2] == (
        '\n'
        'Error Output:\n'
        '> This is in ASCII.\n'
    )
    show_argv_spy.assert_called_once_with(*result.argv)

def test_report_empty_stdout_undecodable_stderr(mocker):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    result = CommandResult(
        argv = ['foo', '-x', 'bar.txt'],
        rc = 0,
        start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
        end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
        stdout = b'',
        stderr = b'\xD0is is i\xF1 L\xE1tin\xB9.\n',
    )
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = False,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = False,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = False,
    )
    show_argv_spy = mocker.spy(util, 'show_argv')
    msg = reporter.report(result)
    assert isinstance(msg, DraftMessage)
    assert msg.headers == {
        "To": to_addrs,
        "Subject": '[DONE] foo -x bar.txt',
        "User-Agent": USER_AGENT,
        "From": from_addr,
    }
    assert len(msg.parts) == 2
    assert msg.parts[0] == (
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output: none\n'
        '\n'
        'Error Output:\n'
    )
    assert isinstance(msg.parts[1], EmailMessage)
    assert msg.parts[1].get_content() == b'\xD0is is i\xF1 L\xE1tin\xB9.\n'
    assert msg.parts[1].get_content_disposition() == 'inline'
    assert msg.parts[1].get_content_type() == 'application/octet-stream'
    assert msg.parts[1].get_filename() == 'stderr'
    ### TODO: Somehow fetch the Content-Type params and assert they are {}
    show_argv_spy.assert_called_once_with(*result.argv)

def test_report_good_stdout_undecodable_stderr(mocker):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    result = CommandResult(
        argv = ['foo', '-x', 'bar.txt'],
        rc = 0,
        start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
        end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
        stdout = b'This is in ASCII.\n',
        stderr = b'\xD0is is i\xF1 L\xE1tin\xB9.\n',
    )
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = False,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = False,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = False,
    )
    show_argv_spy = mocker.spy(util, 'show_argv')
    msg = reporter.report(result)
    assert isinstance(msg, DraftMessage)
    assert msg.headers == {
        "To": to_addrs,
        "Subject": '[DONE] foo -x bar.txt',
        "User-Agent": USER_AGENT,
        "From": from_addr,
    }
    assert len(msg.parts) == 2
    assert msg.parts[0] == (
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
        '> This is in ASCII.\n'
        '\n'
        'Error Output:\n'
    )
    assert isinstance(msg.parts[1], EmailMessage)
    assert msg.parts[1].get_content() == b'\xD0is is i\xF1 L\xE1tin\xB9.\n'
    assert msg.parts[1].get_content_disposition() == 'inline'
    assert msg.parts[1].get_content_type() == 'application/octet-stream'
    assert msg.parts[1].get_filename() == 'stderr'
    ### TODO: Somehow fetch the Content-Type params and assert they are {}
    show_argv_spy.assert_called_once_with(*result.argv)

def test_report_undecodable_stdout_and_stderr(mocker):
    from_addr = Address('Command Reporter', addr_spec='reporter@example.com')
    to_addrs = [Address('Re Cipient', addr_spec='person@example.com')]
    result = CommandResult(
        argv = ['foo', '-x', 'bar.txt'],
        rc = 0,
        start = datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
        end = datetime(2020, 3, 10, 15, 1, 27, 654321, w4),
        stdout = b'\xD0is is i\xF1 L\xE1tin\xB9.\n',
        stderr = b'\xE3\x88\x89\xA2@\x89\xA2@\x89\x95@\xC5\xC2\xC3\xC4\xC9\xC3K%',
    )
    reporter = CommandReporter(
        encoding        = 'utf-8',
        failure_only    = False,
        from_addr       = from_addr,
        mime_type       = None,
        nonempty        = False,
        stderr_encoding = 'utf-8',
        stdout_filename = None,
        to_addrs        = to_addrs,
        utc             = False,
    )
    show_argv_spy = mocker.spy(util, 'show_argv')
    msg = reporter.report(result)
    assert isinstance(msg, DraftMessage)
    assert msg.headers == {
        "To": to_addrs,
        "Subject": '[DONE] foo -x bar.txt',
        "User-Agent": USER_AGENT,
        "From": from_addr,
    }
    assert len(msg.parts) == 4
    assert msg.parts[0] == (
        'Start Time:  2020-03-10 15:00:28.123456-04:00\n'
        'End Time:    2020-03-10 15:01:27.654321-04:00\n'
        'Exit Status: 0\n'
        '\n'
        'Output:\n'
    )
    assert isinstance(msg.parts[1], EmailMessage)
    assert msg.parts[1].get_content() == b'\xD0is is i\xF1 L\xE1tin\xB9.\n'
    assert msg.parts[1].get_content_disposition() == 'inline'
    assert msg.parts[1].get_content_type() == 'application/octet-stream'
    assert msg.parts[1].get_filename() == 'stdout'
    ### TODO: Somehow fetch the Content-Type params and assert they are {}
    assert msg.parts[2] == (
        '\n'
        'Error Output:\n'
    )
    assert isinstance(msg.parts[3], EmailMessage)
    assert msg.parts[3].get_content() \
        == b'\xE3\x88\x89\xA2@\x89\xA2@\x89\x95@\xC5\xC2\xC3\xC4\xC9\xC3K%'
    assert msg.parts[3].get_content_disposition() == 'inline'
    assert msg.parts[3].get_content_type() == 'application/octet-stream'
    assert msg.parts[3].get_filename() == 'stderr'
    ### TODO: Somehow fetch the Content-Type params and assert they are {}
    show_argv_spy.assert_called_once_with(*result.argv)

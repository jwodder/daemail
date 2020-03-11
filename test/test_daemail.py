from   datetime              import datetime, timedelta, timezone
from   email                 import message_from_binary_file, policy
from   email.headerregistry  import Address
import mailbox
import os
import subprocess
from   types                 import SimpleNamespace
from   click.testing         import CliRunner
import pytest
from   daemail.__main__      import main
from   daemail.message       import USER_AGENT
from   test_lib_emailmatcher import TextMessage

w4 = timezone(timedelta(hours=-4))

MOCK_START = datetime(2020, 3, 11, 16, 22, 32,  10203, w4)
MOCK_END   = datetime(2020, 3, 11, 16, 24, 19, 102030, w4)

def msg_factory(fp):
    return message_from_binary_file(fp, policy=policy.default)

@pytest.mark.parametrize('opts,argv,run_kwargs,cmdresult,mailspec', [

    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        SimpleNamespace(
            returncode = 0,
            stdout     = b'This is the output.\n',
            stderr     = None,
        ),
        TextMessage(
            {
                "From": (Address('Me', addr_spec='sender@example.nil'),),
                "To": (Address(addr_spec='null@test.test'),),
                "Subject": '[DONE] not-a-real-command -x foo.txt',
                "User-Agent": USER_AGENT,
            },
            'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
            'End Time:    2020-03-11 16:24:19.102030-04:00\n'
            'Exit Status: 0\n'
            '\n'
            'Output:\n'
            '> This is the output.\n'
        ),
    ),

    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '-t', 'Interested Party <them@org.test>',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        SimpleNamespace(
            returncode = 0,
            stdout     = b'This is the output.\n',
            stderr     = None,
        ),
        TextMessage(
            {
                "From": (Address('Me', addr_spec='sender@example.nil'),),
                "To": (
                    Address(addr_spec='null@test.test'),
                    Address('Interested Party', addr_spec='them@org.test'),
                ),
                "Subject": '[DONE] not-a-real-command -x foo.txt',
                "User-Agent": USER_AGENT,
            },
            'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
            'End Time:    2020-03-11 16:24:19.102030-04:00\n'
            'Exit Status: 0\n'
            '\n'
            'Output:\n'
            '> This is the output.\n'
        ),
    ),

    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
        ],
        ['space command', 'space file'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        SimpleNamespace(
            returncode = 0,
            stdout     = b'This is the output.\n',
            stderr     = None,
        ),
        TextMessage(
            {
                "From": (Address('Me', addr_spec='sender@example.nil'),),
                "To": (Address(addr_spec='null@test.test'),),
                "Subject": "[DONE] 'space command' 'space file'",
                "User-Agent": USER_AGENT,
            },
            'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
            'End Time:    2020-03-11 16:24:19.102030-04:00\n'
            'Exit Status: 0\n'
            '\n'
            'Output:\n'
            '> This is the output.\n'
        ),
    ),

])
def test_daemail(mocker, opts, argv, run_kwargs, cmdresult, mailspec):
    daemon_mock = mocker.patch('daemon.DaemonContext', autospec=True)
    run_mock = mocker.patch('subprocess.run', return_value=cmdresult)
    tsiter = iter([MOCK_START, MOCK_END])
    dtnow_mock = mocker.patch(
        'daemail.util.dtnow',
        side_effect=lambda: next(tsiter),
    )
    runner = CliRunner()
    with runner.isolated_filesystem():
        r = runner.invoke(main, [*opts, '--mbox', 'daemail.mbox', *argv])
        assert r.exit_code == 0, r.output
        assert daemon_mock.call_count == 1
        assert daemon_mock.return_value.__enter__.call_count == 1
        run_mock.assert_called_once_with(argv, **run_kwargs)
        assert dtnow_mock.call_count == 2
        assert os.listdir() == ['daemail.mbox']
        mbox = mailbox.mbox('daemail.mbox', factory=msg_factory)
        mbox.lock()
        msgs = list(mbox)
        mbox.close()
    assert len(msgs) == 1
    mailspec.assert_match(msgs[0])

# no message due to --nonempty
# no message due to --failure-only
# message delivery failure leading to dead.letter file

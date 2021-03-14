from   datetime         import datetime, timedelta, timezone
import email
from   email            import policy
import mailbox
import os
import subprocess
from   traceback        import format_exception
from   types            import SimpleNamespace
from   click.testing    import CliRunner
from   mailbits         import email2dict
import pytest
from   daemail.__main__ import DEFAULT_SENDMAIL, main
from   daemail.message  import USER_AGENT

w4 = timezone(timedelta(hours=-4))

MOCK_START = datetime(2020, 3, 11, 16, 22, 32,  10203, w4)
MOCK_END   = datetime(2020, 3, 11, 16, 24, 19, 102030, w4)

def msg_factory(fp):
    return email.message_from_binary_file(fp, policy=policy.default)

def show_result(r):
    if r.exception is not None:
        return ''.join(format_exception(*r.exc_info))
    else:
        return r.stdout, r.stderr

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
        {
            "unixfrom": None,
            "headers": {
                "from": [
                    {"display_name": "Me", "address": "sender@example.nil"}
                ],
                "to": [
                    {"display_name": "", "address": "null@test.test"},
                ],
                "subject": '[DONE] not-a-real-command -x foo.txt',
                "user-agent": [USER_AGENT],
                "content-type": {
                    "content_type": "text/plain",
                    "params": {},
                },
            },
            "preamble": None,
            "content": (
                'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
                'End Time:    2020-03-11 16:24:19.102030-04:00\n'
                'Exit Status: 0\n'
                '\n'
                'Output:\n'
                '> This is the output.\n'
            ),
            "epilogue": None,
        },
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
        {
            "unixfrom": None,
            "headers": {
                "from": [
                    {"display_name": "Me", "address": "sender@example.nil"}
                ],
                "to": [
                    {"display_name": "", "address": "null@test.test"},
                    {
                        "display_name": "Interested Party",
                        "address": "them@org.test",
                    },
                ],
                "subject": '[DONE] not-a-real-command -x foo.txt',
                "user-agent": [USER_AGENT],
                "content-type": {
                    "content_type": "text/plain",
                    "params": {},
                },
            },
            "preamble": None,
            "content": (
                'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
                'End Time:    2020-03-11 16:24:19.102030-04:00\n'
                'Exit Status: 0\n'
                '\n'
                'Output:\n'
                '> This is the output.\n'
            ),
            "epilogue": None,
        },
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
        {
            "unixfrom": None,
            "headers": {
                "from": [
                    {"display_name": "Me", "address": "sender@example.nil"}
                ],
                "to": [{"display_name": "", "address": "null@test.test"}],
                "subject": "[DONE] 'space command' 'space file'",
                "user-agent": [USER_AGENT],
                "content-type": {
                    "content_type": "text/plain",
                    "params": {},
                },
            },
            "preamble": None,
            "content": (
                'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
                'End Time:    2020-03-11 16:24:19.102030-04:00\n'
                'Exit Status: 0\n'
                '\n'
                'Output:\n'
                '> This is the output.\n'
            ),
            "epilogue": None,
        },
    ),

    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '--nonempty',
            '--no-stdout',
            '--no-stderr',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": None, "stderr": None},
        SimpleNamespace(
            returncode = 1,
            stdout     = None,
            stderr     = None,
        ),
        {
            "unixfrom": None,
            "headers": {
                "from": [
                    {"display_name": "Me", "address": "sender@example.nil"}
                ],
                "to": [{"display_name": "", "address": "null@test.test"}],
                "subject": "[FAILED] not-a-real-command -x foo.txt",
                "user-agent": [USER_AGENT],
                "content-type": {
                    "content_type": "text/plain",
                    "params": {},
                },
            },
            "preamble": None,
            "content": (
                'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
                'End Time:    2020-03-11 16:24:19.102030-04:00\n'
                'Exit Status: 1\n'
            ),
            "epilogue": None,
        },
    ),

    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '--failure-only',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        SimpleNamespace(
            returncode = 1,
            stdout     = b'Something went wrong.\n',
            stderr     = None,
        ),
        {
            "unixfrom": None,
            "headers": {
                "from": [
                    {"display_name": "Me", "address": "sender@example.nil"}
                ],
                "to": [{"display_name": "", "address": "null@test.test"}],
                "subject": "[FAILED] not-a-real-command -x foo.txt",
                "user-agent": [USER_AGENT],
                "content-type": {
                    "content_type": "text/plain",
                    "params": {},
                },
            },
            "preamble": None,
            "content": (
                'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
                'End Time:    2020-03-11 16:24:19.102030-04:00\n'
                'Exit Status: 1\n'
                '\n'
                'Output:\n'
                '> Something went wrong.\n'
            ),
            "epilogue": None,
        },
    ),

    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '--nonempty',
            '--split',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE},
        SimpleNamespace(
            returncode = 0,
            stdout     = b'This is the stdout.\n',
            stderr     = b'',
        ),
        {
            "unixfrom": None,
            "headers": {
                "from": [
                    {"display_name": "Me", "address": "sender@example.nil"}
                ],
                "to": [{"display_name": "", "address": "null@test.test"}],
                "subject": "[DONE] not-a-real-command -x foo.txt",
                "user-agent": [USER_AGENT],
                "content-type": {
                    "content_type": "text/plain",
                    "params": {},
                },
            },
            "preamble": None,
            "content": (
                'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
                'End Time:    2020-03-11 16:24:19.102030-04:00\n'
                'Exit Status: 0\n'
                '\n'
                'Output:\n'
                '> This is the stdout.\n'
            ),
            "epilogue": None,
        },
    ),

    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '--nonempty',
            '--split',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE},
        SimpleNamespace(
            returncode = 0,
            stdout     = b'',
            stderr     = b'This is the stderr.\n',
        ),
        {
            "unixfrom": None,
            "headers": {
                "from": [
                    {"display_name": "Me", "address": "sender@example.nil"}
                ],
                "to": [{"display_name": "", "address": "null@test.test"}],
                "subject": "[DONE] not-a-real-command -x foo.txt",
                "user-agent": [USER_AGENT],
                "content-type": {
                    "content_type": "text/plain",
                    "params": {},
                },
            },
            "preamble": None,
            "content": (
                'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
                'End Time:    2020-03-11 16:24:19.102030-04:00\n'
                'Exit Status: 0\n'
                '\n'
                'Output: none\n'
                '\n'
                'Error Output:\n'
                '> This is the stderr.\n'
            ),
            "epilogue": None,
        },
    ),

    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '--foreground',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        SimpleNamespace(
            returncode = 0,
            stdout     = b'This is the output.\n',
            stderr     = None,
        ),
        {
            "unixfrom": None,
            "headers": {
                "from": [
                    {"display_name": "Me", "address": "sender@example.nil"}
                ],
                "to": [{"display_name": "", "address": "null@test.test"}],
                "subject": '[DONE] not-a-real-command -x foo.txt',
                "user-agent": [USER_AGENT],
                "content-type": {
                    "content_type": "text/plain",
                    "params": {},
                },
            },
            "preamble": None,
            "content": (
                'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
                'End Time:    2020-03-11 16:24:19.102030-04:00\n'
                'Exit Status: 0\n'
                '\n'
                'Output:\n'
                '> This is the output.\n'
            ),
            "epilogue": None,
        },
    ),

])
def test_daemail(mocker, opts, argv, run_kwargs, cmdresult, mailspec):
    daemon_mock = mocker.patch('daemon.DaemonContext', autospec=True)
    run_mock = mocker.patch('subprocess.run', return_value=cmdresult)
    dtnow_mock = mocker.patch(
        'daemail.util.dtnow',
        side_effect=[MOCK_START, MOCK_END],
    )
    runner = CliRunner()
    with runner.isolated_filesystem():
        r = runner.invoke(main, [*opts, '--mbox', 'daemail.mbox', *argv])
        assert r.exit_code == 0, show_result(r)
        if '--foreground' in opts:
            assert not daemon_mock.called
        else:
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
    assert email2dict(msgs[0]) == mailspec

@pytest.mark.parametrize('opts,argv,run_kwargs,cmdresult', [
    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '--failure-only',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        SimpleNamespace(
            returncode = 0,
            stdout     = b'This is the output.\n',
            stderr     = None,
        ),
    ),
    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '--nonempty',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        SimpleNamespace(
            returncode = 0,
            stdout     = b'',
            stderr     = None,
        ),
    ),
    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '--nonempty',
            '--split',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE},
        SimpleNamespace(
            returncode = 0,
            stdout     = b'',
            stderr     = b'',
        ),
    ),
    (
        [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            '--nonempty',
            '--no-stdout',
            '--no-stderr',
        ],
        ['not-a-real-command', '-x', 'foo.txt'],
        {"stdout": None, "stderr": None},
        SimpleNamespace(
            returncode = 0,
            stdout     = None,
            stderr     = None,
        ),
    ),
])
def test_no_message(mocker, opts, argv, run_kwargs, cmdresult):
    daemon_mock = mocker.patch('daemon.DaemonContext', autospec=True)
    run_mock = mocker.patch('subprocess.run', return_value=cmdresult)
    dtnow_mock = mocker.patch(
        'daemail.util.dtnow',
        side_effect=[MOCK_START, MOCK_END],
    )
    runner = CliRunner()
    with runner.isolated_filesystem():
        r = runner.invoke(main, [*opts, '--mbox', 'daemail.mbox', *argv])
        assert r.exit_code == 0, show_result(r)
        assert daemon_mock.call_count == 1
        assert daemon_mock.return_value.__enter__.call_count == 1
        run_mock.assert_called_once_with(argv, **run_kwargs)
        assert dtnow_mock.call_count == 2
        assert os.listdir() == []

def test_sendmail_failure(mocker):
    daemon_mock = mocker.patch('daemon.DaemonContext', autospec=True)
    run_mock = mocker.patch(
        'subprocess.run',
        side_effect=[
            SimpleNamespace(
                returncode = 0,
                stdout     = b'This is the output.\n',
                stderr     = None,
            ),
            SimpleNamespace(
                returncode = 1,
                stdout     = b'All the foos are bar when they should be baz.\n',
            ),
        ],
    )
    dtnow_mock = mocker.patch(
        'daemail.util.dtnow',
        side_effect=[MOCK_START, MOCK_END],
    )
    runner = CliRunner()
    argv = ['not-a-real-command', '-x', 'foo.txt']
    with runner.isolated_filesystem():
        r = runner.invoke(main, [
            '-t', 'null@test.test',
            '-f', 'Me <sender@example.nil>',
            *argv,
        ])
        assert r.exit_code == 0, show_result(r)
        assert daemon_mock.call_count == 1
        assert daemon_mock.return_value.__enter__.call_count == 1
        assert run_mock.call_args_list == [
            mocker.call(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT),
            mocker.call(
                DEFAULT_SENDMAIL,
                shell  = True,
                input  = mocker.ANY,
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
            ),
        ]
        sent_msg = email.message_from_bytes(
            run_mock.call_args_list[1][1]["input"],
            policy=policy.default,
        )
        assert email2dict(sent_msg) == {
            "unixfrom": None,
            "headers": {
                "from": [
                    {"display_name": "Me", "address": "sender@example.nil"}
                ],
                "to": [{"display_name": "", "address": "null@test.test"}],
                "subject": '[DONE] not-a-real-command -x foo.txt',
                "user-agent": [USER_AGENT],
                "content-type": {
                    "content_type": "text/plain",
                    "params": {},
                },
            },
            "preamble": None,
            "content": (
                'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
                'End Time:    2020-03-11 16:24:19.102030-04:00\n'
                'Exit Status: 0\n'
                '\n'
                'Output:\n'
                '> This is the output.\n'
            ),
            "epilogue": None,
        }
        assert dtnow_mock.call_count == 2
        assert os.listdir() == ['dead.letter']
        mbox = mailbox.mbox('dead.letter', factory=msg_factory)
        mbox.lock()
        dead_msgs = list(mbox)
        mbox.close()
    assert len(dead_msgs) == 1
    assert email2dict(dead_msgs[0]) == {
        "unixfrom": None,
        "headers": {
            "from": [
                {"display_name": "Me", "address": "sender@example.nil"}
            ],
            "to": [{"display_name": "", "address": "null@test.test"}],
            "subject": '[DONE] not-a-real-command -x foo.txt',
            "user-agent": [USER_AGENT],
            "content-type": {
                "content_type": "text/plain",
                "params": {},
            },
        },
        "preamble": None,
        "content": (
            'Start Time:  2020-03-11 16:22:32.010203-04:00\n'
            'End Time:    2020-03-11 16:24:19.102030-04:00\n'
            'Exit Status: 0\n'
            '\n'
            'Output:\n'
            '> This is the output.\n'
            '\n'
            'Additionally, an error occurred while trying to send this e-mail:\n'
            '\n'
            'Method: command\n'
            f'Command: {DEFAULT_SENDMAIL}\n'
            'Exit Status: 1\n'
            '\n'
            'Output:\n'
            '> All the foos are bar when they should be baz.\n'
        ),
        "epilogue": None,
    }

# daemail printf '%s\n' $'foo\nbar'
# daemail printf '%s\n' $'foo\xe2bar'
# daemail printf '%s\n' $'go\xf0\x9f\x90\x90at'
# daemail printf '%s\n' $'baaaad \xed\xa0\xbd\xed\xb0\x90 goat'

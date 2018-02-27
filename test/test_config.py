import os.path
from   click.testing    import CliRunner
import pytest
from   daemail          import senders
from   daemail.__main__ import main

@pytest.fixture
def capture_cfg(mocker):
    return mocker.patch('daemail.mailer.CommandMailer', autospec=True)

def test_default_sendmail(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert isinstance(kwargs["sender"], senders.CommandSender)
    assert kwargs["sender"].sendmail == 'sendmail -i -t'

def test_custom_sendmail(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '-s', 'mail-send -q -rs',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert isinstance(kwargs["sender"], senders.CommandSender)
    assert kwargs["sender"].sendmail == 'mail-send -q -rs'

def test_smtp_host(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-host', 'smtp.test',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username is None
    assert kwargs["sender"].password is None

def test_smtp_host_port(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-host', 'smtp.test',
        '--smtp-port', '42',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port == 42
    assert kwargs["sender"].username is None
    assert kwargs["sender"].password is None

def test_smtp_port_host(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-port', '42',
        '--smtp-host', 'smtp.test',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port == 42
    assert kwargs["sender"].username is None
    assert kwargs["sender"].password is None

def test_bad_smtp_port_no_host(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-port', '42',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code != 0
    assert '--smtp-host is required for SMTP' in r.output
    assert not capture_cfg.called

def test_smtp_port_mbox(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-port', '42',
        '--mbox', 'mail.mbox',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert isinstance(kwargs["sender"], senders.MboxSender)
    assert kwargs["sender"].filename == os.path.realpath('mail.mbox')

def test_bad_mbox_smtp_port_no_host(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--mbox', 'mail.mbox',
        '--smtp-port', '42',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code != 0
    assert '--smtp-host is required for SMTP' in r.output
    assert not capture_cfg.called

def test_starttls_smtp_host(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-starttls',
        '--smtp-host', 'smtp.test',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.StartTLSSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username is None
    assert kwargs["sender"].password is None

def test_smtp_host_starttls(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-host', 'smtp.test',
        '-t', 'null@test.test',
        '--smtp-starttls',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.StartTLSSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username is None
    assert kwargs["sender"].password is None

def test_ssl_smtp_host(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-ssl',
        '--smtp-host', 'smtp.test',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTP_SSLSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username is None
    assert kwargs["sender"].password is None

def test_smtp_host_ssl(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-host', 'smtp.test',
        '-t', 'null@test.test',
        '--smtp-ssl',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTP_SSLSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username is None
    assert kwargs["sender"].password is None

def test_smtp_host_username_input_pass(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-host', 'smtp.test',
        '--smtp-username', 'me@invalid.test',
        '-t', 'null@test.test',
        'true',
    ], input='hunter2\n')
    assert r.exit_code == 0, r.output
    assert r.output == 'SMTP password: \n'
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'hunter2'

def test_smtp_host_username_cli_pass(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-host', 'smtp.test',
        '--smtp-username', 'me@invalid.test',
        '--smtp-password', 'from-the-command-line',
        '-t', 'null@test.test',
        'true',
    ], input='hunter2\n')
    assert r.exit_code == 0, r.output
    assert r.output == ''
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'from-the-command-line'

def test_smtp_host_username_file_pass(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('smtp_password.txt', 'w') as fp:
            print('from_a_file', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--smtp-username', 'me@invalid.test',
            '--smtp-password-file', 'smtp_password.txt',
            '-t', 'null@test.test',
            'true',
        ])
    assert r.exit_code == 0, r.output
    assert r.output == ''
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'from_a_file'

def test_smtp_host_username_file_pass_extra_newline(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('smtp_password.txt', 'w') as fp:
            print('from_a_file\n', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--smtp-username', 'me@invalid.test',
            '--smtp-password-file', 'smtp_password.txt',
            '-t', 'null@test.test',
            'true',
        ])
    assert r.exit_code == 0, r.output
    assert r.output == ''
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'from_a_file\n'

def test_smtp_host_username_cli_file_pass(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('smtp_password.txt', 'w') as fp:
            print('from_a_file', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--smtp-username', 'me@invalid.test',
            '--smtp-password', 'from-the-command-line',
            '--smtp-password-file', 'smtp_password.txt',
            '-t', 'null@test.test',
            'true',
        ])
    assert r.exit_code == 0, r.output
    assert r.output == ''
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'from_a_file'

def test_smtp_host_username_netrc_file_pass(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('netrc.txt', 'w') as fp:
            print('machine smtp.test', file=fp)
            print('login me@invalid.test', file=fp)
            print('password from-custom-netrc', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--smtp-username', 'me@invalid.test',
            '--netrc-file', 'netrc.txt',
            '-t', 'null@test.test',
            'true',
        ])
    assert r.exit_code == 0, r.output
    assert r.output == ''
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'from-custom-netrc'

def test_smtp_host_username_netrc_mismatch(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('netrc.txt', 'w') as fp:
            print('machine smtp.test', file=fp)
            print('login you@test.invalid', file=fp)
            print('password from-custom-netrc', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--smtp-username', 'me@invalid.test',
            '--netrc-file', 'netrc.txt',
            '-t', 'null@test.test',
            'true',
        ], input='hunter2\n')
    assert r.exit_code == 0, r.output
    assert r.output == 'SMTP password: \n'
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'hunter2'

def test_smtp_host_username_netrc_host_mismatch(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('netrc.txt', 'w') as fp:
            print('machine smtp.invalid', file=fp)
            print('login me@invalid.test', file=fp)
            print('password from-custom-netrc', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--smtp-username', 'me@invalid.test',
            '--netrc-file', 'netrc.txt',
            '-t', 'null@test.test',
            'true',
        ], input='hunter2\n')
    assert r.exit_code == 0, r.output
    assert r.output == 'SMTP password: \n'
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'hunter2'

def test_smtp_host_no_username_netrc_file(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('netrc.txt', 'w') as fp:
            print('machine smtp.test', file=fp)
            print('login me@invalid.test', file=fp)
            print('password from-custom-netrc', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--netrc-file', 'netrc.txt',
            '-t', 'null@test.test',
            'true',
        ])
    assert r.exit_code == 0, r.output
    assert r.output == ''
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'from-custom-netrc'

def test_smtp_host_username_netrc_no_user(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('netrc.txt', 'w') as fp:
            print('machine smtp.test', file=fp)
            print('password from-custom-netrc', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--smtp-username', 'me@invalid.test',
            '--netrc-file', 'netrc.txt',
            '-t', 'null@test.test',
            'true',
        ])
    assert r.exit_code == 0, r.output
    assert r.output == ''
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'from-custom-netrc'

def test_smtp_host_no_username_netrc_no_user(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('netrc.txt', 'w') as fp:
            print('machine smtp.test', file=fp)
            print('password from-custom-netrc', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--netrc-file', 'netrc.txt',
            '-t', 'null@test.test',
            'true',
        ])
    assert r.exit_code == 0, r.output
    assert r.output == ''
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username is None
    assert kwargs["sender"].password is None

@pytest.mark.skip(reason="Python doesn't support .netrc entries without `password`?")
def test_smtp_host_no_username_netrc_no_pass(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('netrc.txt', 'w') as fp:
            print('machine smtp.test', file=fp)
            print('login me@invalid.test', file=fp)
        r = runner.invoke(main, [
            '--foreground',
            '--smtp-host', 'smtp.test',
            '--netrc-file', 'netrc.txt',
            '-t', 'null@test.test',
            'true',
        ], input='hunter2\n')
    assert r.exit_code == 0, r.output
    assert r.output == 'SMTP password: \n'
    assert capture_cfg.call_count == 1
    _, kwargs = capture_cfg.call_args
    assert "sender" in kwargs
    assert type(kwargs["sender"]) is senders.SMTPSender
    assert kwargs["sender"].host == 'smtp.test'
    assert kwargs["sender"].port is None
    assert kwargs["sender"].username == 'me@invalid.test'
    assert kwargs["sender"].password == 'hunter2'

def test_command_options(mocker):
    run = mocker.patch('daemail.mailer.CommandMailer.run', autospec=True)
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        'true',
        '-l', 'true.log',
        'false',
    ])
    assert r.exit_code == 0, r.output
    run.assert_called_once_with(mocker.ANY, 'true', '-l', 'true.log', 'false')

def test_command_double_dash(mocker):
    run = mocker.patch('daemail.mailer.CommandMailer.run', autospec=True)
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        'true',
        '--',
        '-l', 'true.log',
        'false',
    ])
    assert r.exit_code == 0, r.output
    run.assert_called_once_with(
        mocker.ANY, 'true', '--', '-l', 'true.log', 'false',
    )

def test_double_dash_command(mocker):
    run = mocker.patch('daemail.mailer.CommandMailer.run', autospec=True)
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--',
        '-l', 'true.log',
        'false',
    ])
    assert r.exit_code == 0, r.output
    run.assert_called_once_with(mocker.ANY, '-l', 'true.log', 'false')

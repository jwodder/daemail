import locale
import os.path
from   click.testing    import CliRunner
import pytest
from   daemail          import senders
from   daemail.__main__ import main

@pytest.fixture
def capture_cfg(mocker):
    return mocker.patch('daemail.__main__.Daemail', autospec=True)

def test_default_sendmail(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    mailer = capture_cfg.call_args[1]["mailer"]
    assert isinstance(mailer.sender, senders.CommandSender)
    assert mailer.sender.sendmail == 'sendmail -i -t'
    assert mailer.dead_letter_path == os.path.realpath('dead.letter')

def test_custom_sendmail(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '-s', 'mail-send -q -rs',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert isinstance(sender, senders.CommandSender)
    assert sender.sendmail == 'mail-send -q -rs'

def test_smtp_host(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--smtp-host', 'smtp.test',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username is None
    assert sender.password is None

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port == 42
    assert sender.username is None
    assert sender.password is None

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port == 42
    assert sender.username is None
    assert sender.password is None

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert isinstance(sender, senders.MboxSender)
    assert sender.filename == os.path.realpath('mail.mbox')

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.StartTLSSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username is None
    assert sender.password is None

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.StartTLSSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username is None
    assert sender.password is None

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTP_SSLSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username is None
    assert sender.password is None

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTP_SSLSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username is None
    assert sender.password is None

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'hunter2'

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'from-the-command-line'

@pytest.mark.parametrize('file_pwd', [
    'from_a_file',
    'from_a_file\n',
    'from_a_file\r\n',
    'from_a_file\r',
])
def test_smtp_host_username_file_pass(capture_cfg, file_pwd):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('smtp_password.txt', 'w') as fp:
            print(file_pwd, end='', file=fp)
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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'from_a_file'

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'from_a_file\n'

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'from_a_file'

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'from-custom-netrc'

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'hunter2'

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'hunter2'

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'from-custom-netrc'

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'from-custom-netrc'

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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username is None
    assert sender.password is None

@pytest.mark.skip(
    reason="Python doesn't support .netrc entries without `password`"
)
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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'hunter2'

def test_smtp_host_username_netrc_defaults(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('netrc.txt', 'w') as fp:
            print('default', file=fp)
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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'from-custom-netrc'

def test_smtp_host_username_netrc_skip_defaults(capture_cfg):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('netrc.txt', 'w') as fp:
            print('default', file=fp)
            print('login me@invalid.test', file=fp)
            print('password from-custom-netrc', file=fp)
            print('machine smtp.test', file=fp)
            print('login me@invalid.test', file=fp)
            print('password the-real-password', file=fp)
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
    sender = capture_cfg.call_args[1]["mailer"].sender
    assert type(sender) is senders.SMTPSender
    assert sender.host == 'smtp.test'
    assert sender.port is None
    assert sender.username == 'me@invalid.test'
    assert sender.password == 'the-real-password'

def test_command_options(mocker):
    run = mocker.patch('daemail.__main__.Daemail.run', autospec=True)
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
    run = mocker.patch('daemail.__main__.Daemail.run', autospec=True)
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
    run = mocker.patch('daemail.__main__.Daemail.run', autospec=True)
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--',
        '-l', 'true.log',
        'false',
    ])
    assert r.exit_code == 0, r.output
    run.assert_called_once_with(mocker.ANY, '-l', 'true.log', 'false')

def test_bad_encoding(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--encoding', 'foobar',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code != 0
    assert 'foobar: unknown encoding' in r.output
    assert not capture_cfg.called

def test_bad_stderr_encoding(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '--stderr-encoding', 'foobar',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code != 0
    assert 'foobar: unknown encoding' in r.output
    assert not capture_cfg.called

def test_default_encodings(capture_cfg):
    def_encoding = locale.getpreferredencoding(True)
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    reporter = capture_cfg.call_args[1]["reporter"]
    assert reporter.encoding == def_encoding
    assert reporter.stderr_encoding == def_encoding

def test_encoding_set(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--encoding=cp500',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    reporter = capture_cfg.call_args[1]["reporter"]
    assert reporter.encoding == 'cp500'
    assert reporter.stderr_encoding == 'cp500'

def test_stderr_encoding_set(capture_cfg):
    def_encoding = locale.getpreferredencoding(True)
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--stderr-encoding', 'cp500',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    reporter = capture_cfg.call_args[1]["reporter"]
    assert reporter.encoding == def_encoding
    assert reporter.stderr_encoding == 'cp500'

def test_all_encodings_set(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--encoding=cp500',
        '--stderr-encoding', 'utf-16be',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    reporter = capture_cfg.call_args[1]["reporter"]
    assert reporter.encoding == 'cp500'
    assert reporter.stderr_encoding == 'utf-16be'

def test_stdout_file_defaults(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    runner = capture_cfg.call_args[1]["runner"]
    reporter = capture_cfg.call_args[1]["reporter"]
    assert not runner.split
    assert reporter.stdout_filename is None
    assert reporter.mime_type is None

def test_stdout_filename_set(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--stdout-filename=foo.png',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    runner = capture_cfg.call_args[1]["runner"]
    reporter = capture_cfg.call_args[1]["reporter"]
    assert runner.split
    assert reporter.stdout_filename == 'foo.png'
    assert reporter.mime_type == 'image/png'

def test_mime_type_set(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--mime-type', 'application/json',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    runner = capture_cfg.call_args[1]["runner"]
    reporter = capture_cfg.call_args[1]["reporter"]
    assert runner.split
    assert reporter.stdout_filename == 'stdout'
    assert reporter.mime_type == 'application/json'

def test_mime_type_and_stdout_filename_set(capture_cfg):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--stdout-filename', 'foo.png',
        '--mime-type=application/json',
        'true',
    ])
    assert r.exit_code == 0, r.output
    assert capture_cfg.call_count == 1
    runner = capture_cfg.call_args[1]["runner"]
    reporter = capture_cfg.call_args[1]["reporter"]
    assert runner.split
    assert reporter.stdout_filename == 'foo.png'
    assert reporter.mime_type == 'application/json'

@pytest.mark.parametrize('mt', [
    'text',
    'text/',
    '/plain',
    'text/plain, charset=utf-8',
])
def test_bad_mime_type(capture_cfg, mt):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--mime-type', mt,
        'true',
    ])
    assert r.exit_code != 0
    assert '{}: invalid MIME type'.format(mt) in r.output
    assert not capture_cfg.called

@pytest.mark.parametrize('to_addr', ['Me', 'person@example.com, foo@bar.org'])
def test_bad_to_addr(capture_cfg, to_addr):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', to_addr,
        'true',
    ])
    assert r.exit_code != 0
    assert '{!r}: invalid address'.format(to_addr) in r.output
    assert not capture_cfg.called

@pytest.mark.parametrize('from_addr', ['Me', 'person@example.com, foo@bar.org'])
def test_bad_from_addr(capture_cfg, from_addr):
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--from', from_addr,
        'true',
    ])
    assert r.exit_code != 0
    assert '{!r}: invalid address'.format(from_addr) in r.output
    assert not capture_cfg.called

# Don't use ~/.netrc if --netrc not specified

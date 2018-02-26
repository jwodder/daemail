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

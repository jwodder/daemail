from   click.testing    import CliRunner
import pytest
from   daemail.__main__ import main
from   daemail.senders  import CommandSender

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
    assert isinstance(kwargs["sender"], CommandSender)
    assert kwargs["sender"].sendmail == 'sendmail -i -t'

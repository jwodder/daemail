import locale
from   pathlib          import Path
from   unittest.mock    import MagicMock
from   click.testing    import CliRunner
from   outgoing         import get_default_configpath
import pytest
from   pytest_mock      import MockerFixture
from   daemail.__main__ import main

@pytest.fixture
def capture_cfg(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('daemail.__main__.Daemail', autospec=True)

@pytest.fixture(autouse=True)
def default_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    p = get_default_configpath()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('[outgoing]\nmethod = "command"\n')

def test_command_options(mocker: MockerFixture) -> None:
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

def test_command_double_dash(mocker: MockerFixture) -> None:
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

def test_double_dash_command(mocker: MockerFixture) -> None:
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

def test_bad_encoding(capture_cfg: MagicMock) -> None:
    r = CliRunner().invoke(main, [
        '--foreground',
        '--encoding', 'foobar',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code != 0
    assert 'foobar: unknown encoding' in r.output
    assert not capture_cfg.called

def test_bad_stderr_encoding(capture_cfg: MagicMock) -> None:
    r = CliRunner().invoke(main, [
        '--foreground',
        '--stderr-encoding', 'foobar',
        '-t', 'null@test.test',
        'true',
    ])
    assert r.exit_code != 0
    assert 'foobar: unknown encoding' in r.output
    assert not capture_cfg.called

def test_default_encodings(capture_cfg: MagicMock) -> None:
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

def test_encoding_set(capture_cfg: MagicMock) -> None:
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

def test_stderr_encoding_set(capture_cfg: MagicMock) -> None:
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

def test_all_encodings_set(capture_cfg: MagicMock) -> None:
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

def test_stdout_file_defaults(capture_cfg: MagicMock) -> None:
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

def test_stdout_filename_set(capture_cfg: MagicMock) -> None:
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

def test_mime_type_set(capture_cfg: MagicMock) -> None:
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

def test_mime_type_and_stdout_filename_set(capture_cfg: MagicMock) -> None:
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
def test_bad_mime_type(capture_cfg: MagicMock, mt: str) -> None:
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--mime-type', mt,
        'true',
    ])
    assert r.exit_code != 0
    assert f'{mt}: invalid MIME type' in r.output
    assert not capture_cfg.called

@pytest.mark.parametrize('to_addr', ['Me', 'person@example.com, foo@bar.org'])
def test_bad_to_addr(capture_cfg: MagicMock, to_addr: str) -> None:
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', to_addr,
        'true',
    ])
    assert r.exit_code != 0
    assert f'{to_addr!r}: invalid address' in r.output
    assert not capture_cfg.called

@pytest.mark.parametrize('from_addr', ['Me', 'person@example.com, foo@bar.org'])
def test_bad_from_addr(capture_cfg: MagicMock, from_addr: str) -> None:
    r = CliRunner().invoke(main, [
        '--foreground',
        '-t', 'null@test.test',
        '--from', from_addr,
        'true',
    ])
    assert r.exit_code != 0
    assert f'{from_addr!r}: invalid address' in r.output
    assert not capture_cfg.called

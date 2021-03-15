from   datetime       import datetime, timedelta, timezone
import subprocess
from   types          import SimpleNamespace
from   typing         import Any, Dict, Union
from   unittest.mock  import ANY, sentinel
import pytest
from   pytest_mock    import MockerFixture
from   daemail.runner import CommandError, CommandResult, CommandRunner

w4 = timezone(timedelta(hours=-4))

MOCK_START = datetime(2020, 3, 11, 16, 22, 32,  10203, w4)
MOCK_END   = datetime(2020, 3, 11, 16, 24, 19, 102030, w4)

ARGV = ['not-a-real-command', '-x', 'foo.txt']

ERROR = OSError('The kernel died.')

@pytest.mark.parametrize('no_stderr,no_stdout,split,run_kwargs,runresult,cmdresult', [
    (
        False,
        False,
        False,
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        SimpleNamespace(
            returncode = sentinel.rc,
            stdout     = sentinel.stdout,
            stderr     = sentinel.stderr,
        ),
        CommandResult(
            argv   = ARGV,
            rc     = sentinel.rc,
            start  = MOCK_START,
            end    = MOCK_END,
            stdout = sentinel.stdout,
            stderr = sentinel.stderr,
        ),
    ),
    (
        False,
        False,
        False,
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        ERROR,
        CommandError(
            argv  = ARGV,
            start = MOCK_START,
            end   = MOCK_END,
            tb    = ANY,
        ),
    ),
    (
        False,
        False,
        True,
        {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE},
        SimpleNamespace(
            returncode = sentinel.rc,
            stdout     = sentinel.stdout,
            stderr     = sentinel.stderr,
        ),
        CommandResult(
            argv   = ARGV,
            rc     = sentinel.rc,
            start  = MOCK_START,
            end    = MOCK_END,
            stdout = sentinel.stdout,
            stderr = sentinel.stderr,
        ),
    ),
    (
        True,
        False,
        False,
        {"stdout": subprocess.PIPE, "stderr": None},
        SimpleNamespace(
            returncode = sentinel.rc,
            stdout     = sentinel.stdout,
            stderr     = sentinel.stderr,
        ),
        CommandResult(
            argv   = ARGV,
            rc     = sentinel.rc,
            start  = MOCK_START,
            end    = MOCK_END,
            stdout = sentinel.stdout,
            stderr = sentinel.stderr,
        ),
    ),
    (
        False,
        True,
        False,
        {"stdout": None, "stderr": subprocess.PIPE},
        SimpleNamespace(
            returncode = sentinel.rc,
            stdout     = sentinel.stdout,
            stderr     = sentinel.stderr,
        ),
        CommandResult(
            argv   = ARGV,
            rc     = sentinel.rc,
            start  = MOCK_START,
            end    = MOCK_END,
            stdout = sentinel.stdout,
            stderr = sentinel.stderr,
        ),
    ),
])
def test_runner(
    mocker: MockerFixture,
    no_stderr: bool,
    no_stdout: bool,
    split: bool,
    run_kwargs: Dict[str, Any],
    runresult: Any,
    cmdresult: Union[CommandResult, CommandError],
) -> None:
    def subprocess_run(*args: Any, **kwargs: Any) -> Any:
        if isinstance(runresult, Exception):
            raise runresult
        else:
            return runresult
    run_mock = mocker.patch('subprocess.run', side_effect=subprocess_run)
    dtnow_mock = mocker.patch(
        'daemail.util.dtnow',
        side_effect=[MOCK_START, MOCK_END],
    )
    runner = CommandRunner(
        no_stderr = no_stderr,
        no_stdout = no_stdout,
        split     = split,
    )
    r = runner.run(*ARGV)
    run_mock.assert_called_once_with(ARGV, **run_kwargs)
    assert dtnow_mock.call_count == 2
    assert r == cmdresult

from   datetime       import datetime, timedelta, timezone
import subprocess
from   types          import SimpleNamespace
from   unittest.mock  import ANY, sentinel
import pytest
from   daemail.runner import CommandError, CommandResult, CommandRunner

w4 = timezone(timedelta(hours=-4))

MOCK_START = datetime(2020, 3, 11, 16, 22, 32,  10203, w4)
MOCK_END   = datetime(2020, 3, 11, 16, 24, 19, 102030, w4)

ARGV = ['not-a-real-command', '-x', 'foo.txt']

ERROR = OSError('The kernel died.')

@pytest.mark.parametrize('no_stderr,no_stdout,split,run_kwargs,runresult,'
                         'cmdresult,errored', [
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
        False,
    ),
    (
        False,
        False,
        False,
        {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT},
        ERROR,
        CommandError(
            argv     = ARGV,
            start    = MOCK_START,
            end      = MOCK_END,
            exc_info = (type(ERROR), ERROR, ANY),
        ),
        True,
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
        False,
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
        False,
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
        False,
    ),
])
def test_runner(mocker, no_stderr, no_stdout, split, run_kwargs, runresult,
                cmdresult, errored):
    def subprocess_run(*args, **kwargs):
        if isinstance(runresult, Exception):
            raise runresult
        else:
            return runresult
    run_mock = mocker.patch('subprocess.run', side_effect=subprocess_run)
    tsiter = iter([MOCK_START, MOCK_END])
    dtnow_mock = mocker.patch(
        'daemail.util.dtnow',
        side_effect=lambda: next(tsiter),
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
    assert r.errored is errored

from   collections import namedtuple
import subprocess
import sys
import traceback
from   .util       import dtnow

class CommandRunner(namedtuple('CommandRunner', 'no_stderr no_stdout split')):
    def run(self, command, *args):
        params = {}
        if self.split or self.no_stdout or self.no_stderr:
            params = {
                "stdout": None if self.no_stdout else subprocess.PIPE,
                "stderr": None if self.no_stderr else subprocess.PIPE,
            }
        else:
            params = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
        start = dtnow()
        try:
            r = subprocess.run([command, *args], **params)
        except Exception:
            return CommandError(
                argv     = [command, *args],
                start    = start,
                end      = dtnow(),
                exc_info = sys.exc_info(),
            )
        end = dtnow()
        return CommandResult(
            argv   = [command, *args],
            rc     = r.returncode,
            start  = start,
            end    = end,
            stdout = r.stdout,
            stderr = r.stderr,
        )


class CommandResult(namedtuple(
    'CommandResult', 'argv rc start end stdout stderr',
)):
    @property
    def errored(self):
        return False


class CommandError(namedtuple('CommandError', 'argv start end exc_info')):
    @property
    def errored(self):
        return True

    def format_traceback(self):
        return traceback.format_exception(*self.exc_info)

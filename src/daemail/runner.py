from   datetime import datetime
import subprocess
import traceback
from   typing   import List, Optional, Union
import attr
from   .        import util  # Access dtnow through util for mocking purposes

@attr.s(auto_attribs=True)
class CommandRunner:
    no_stderr: bool
    no_stdout: bool
    split: bool

    def run(self, command: str, *args: str) -> Union["CommandResult", "CommandError"]:
        stdout: Optional[int]
        stderr: Optional[int]
        if self.split or self.no_stdout or self.no_stderr:
            stdout = None if self.no_stdout else subprocess.PIPE
            stderr = None if self.no_stderr else subprocess.PIPE
        else:
            stdout = subprocess.PIPE
            stderr = subprocess.STDOUT
        start = util.dtnow()
        try:
            r = subprocess.run([command, *args], stdout=stdout, stderr=stderr)
        except Exception:
            return CommandError(
                argv  = [command, *args],
                start = start,
                end   = util.dtnow(),
                tb    = traceback.format_exc(),
            )
        end = util.dtnow()
        return CommandResult(
            argv   = [command, *args],
            rc     = r.returncode,
            start  = start,
            end    = end,
            stdout = r.stdout,
            stderr = r.stderr,
        )


@attr.s(auto_attribs=True)
class CommandResult:
    argv: List[str]
    rc: int
    start: datetime  # aware
    end: datetime  # aware
    stdout: Optional[bytes]
    stderr: Optional[bytes]


@attr.s(auto_attribs=True)
class CommandError:
    argv: List[str]
    start: datetime  # aware
    end: datetime  # aware
    tb: str

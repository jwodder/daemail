- Check the validity of format strings (by populating them with dummy values?)
  before daemonizing

- Options to add:
    - set subject
    - set body
        - read body template from stdin/a file
        - When not read from stdin, supports escape sequences in the format
          string
    - read template for the whole e-mail (headers and all) from a file?

- Variables for subject and body format strings:
    - `rc` — return code
    - `merged` — combined stdout & stderr
        - mutually exclusive with `stdout` and `stderr`
    - `stdout`
    - `stderr`
    - `start` (timestamp)
    - `end` (timestamp)
    - `argv0`
    - `command` (all arguments)
    - `runtime` (`str(timedelta)`)
    - `pid` (of spawned process)

    Should the `{merged}`, `{stdin}`, and `{stderr}` variables automatically
    have trailing newlines (or embedded newlines?) stripped when used in the
    subject?  Or should they not be allowed in the subject in the first place?

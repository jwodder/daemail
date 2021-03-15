from   datetime  import datetime, timezone
from   mimetypes import guess_type
import os
import re
from   shlex     import quote
from   signal    import Signals
import click
from   mailbits  import parse_address

def rc_with_signal(rc):
    if rc < 0:
        try:
            sig = Signals(-rc)
        except ValueError:
            return str(rc)
        else:
            return f'{rc} ({sig.name})'
    return str(rc)

bash_slash = {
    c: fr'\x{c:02x}'
    for c in list(range(0x00, 0x20)) + list(range(0x7F, 0x100))
}
bash_slash.update({
    0x07: r'\a',
    0x08: r'\b',
    0x09: r'\t',
    0x0A: r'\n',
    0x0B: r'\v',
    0x0C: r'\f',
    0x0D: r'\r',
    0x1B: r'\e',
    0x27: r"\'",
    0x5C: r'\\',
})

def show_argv(*argv):
    r"""
    Join — and possibly escape & quote — the elements of ``argv`` into a
    pure-ASCII form suitable for passing directly to a \*nix shell.
    Nonprintable characters are escaped in a format that is Bash-specific but
    should still be understandable to users of other shells.

    The elements of ``argv`` are assumed to have been taken directly from
    `sys.argv` (possibly with a detour through `argparse`); specifically, they
    are assumed to be text strings decoded with `os.fsdecode`.
    """
    # Just using `repr` for this won't work, as the quotes it adds around
    # simple (e.g., alphanumeric) arguments are unnecessary, and the double
    # quotes it puts around strings like `"'$HOME'"` are just plain wrong.
    shown = ''
    assigning = True
    for a in argv:
        a = os.fsencode(a).decode('iso-8859-1')
        if re.search(r'[^\x20-\x7E]', a):
            a = "$'" + a.translate(bash_slash) + "'"
            assigning = False
        else:
            a = quote(a)
            if assigning and re.match(r'^[A-Za-z_]\w*=', a):
                a = "'" + a + "'"
            else:
                assigning = False
        if shown:
            shown += ' '
        shown += a
    return shown

def dtnow():
    return datetime.now(timezone.utc).astimezone()

def dt2stamp(dt, utc=False):
    if utc:
        s = str(dt.astimezone(timezone.utc))
        assert s.endswith('+00:00')
        return s[:-6] + 'Z'
    else:
        return str(dt)

def multiline822(s):
    return re.sub('^', '  ', re.sub('^$', '.', s.strip('\r\n'), flags=re.M),
                  flags=re.M)


class AddressParamType(click.ParamType):
    name = 'address'

    def convert(self, value, param, ctx):
        try:
            return parse_address(value)
        except ValueError:
            self.fail(f'{value!r}: invalid address', param, ctx)


def get_mime_type(filename):
    """
    Like `mimetypes.guess_type()`, except that if the file is compressed, the
    MIME type for the compression is returned.  Also, the default return value
    is now ``'application/octet-stream'`` instead of `None`.
    """
    mtype, encoding = guess_type(filename, False)
    if encoding is None:
        return mtype or 'application/octet-stream'
    elif encoding == 'gzip':
        # application/gzip is defined by RFC 6713
        return 'application/gzip'
        # Note that there is a "+gzip" MIME structured syntax suffix specified
        # in an RFC draft that may one day mean the correct code is:
        #return mtype + '+gzip'
    else:
        return 'application/x-' + encoding
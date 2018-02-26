from   datetime             import datetime
from   email.headerregistry import Address
from   email.utils          import localtime, parseaddr
import os
import re
from   shlex                import quote
import signal
import click

class MailCmdError(Exception):
    # Raised if the sendmail command returned nonzero
    def __init__(self, sendmail, rc, output):
        self.sendmail = sendmail
        self.rc = rc
        self.output = output
        super(MailCmdError, self).__init__(sendmail, rc, output)

    def __str__(self):
        return '{0.sendmail!r}: command exited with return code {0.rc}'\
               .format(self)


def mail_quote(s):
    return ''.join('> ' + line + '\n' for line in (s or '\n').splitlines())

def rc_with_signal(rc):
    if rc < 0:
        # cf. <http://stackoverflow.com/q/2549939/744178>
        signames = [k for k,v in vars(signal).items()
                      if k.startswith('SIG') and v == -rc]
        if signames:
            return '{} ({})'.format(rc, ', '.join(signames))
    return str(rc)

bash_slash = {
    c: r'\x{:02x}'.format(c)
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
    Join -- and possibly escape & quote -- the elements of ``argv`` into a
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
        if isinstance(a, str):
            a = os.fsencode(a)
        a = a.decode('iso-8859-1')
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

def nowstamp(utc=False):
    if utc:
        return str(datetime.utcnow()) + 'Z'
    else:
        return str(localtime())

def multiline822(s):
    return re.sub('^', '  ', re.sub('^$', '.', s.strip('\r\n'), flags=re.M),
                  flags=re.M)

def parse_address(s):
    realname, addr = parseaddr(s)
    if addr == '':
        raise ValueError(s)
    try:
        return Address(realname, addr_spec=addr)
    except ValueError:
        raise ValueError(s)

class AddressParamType(click.ParamType):
    name = 'address'

    def convert(self, value, param, ctx):
        try:
            return parse_address(value)
        except ValueError:
            self.fail('{!r}: invalid address'.format(value), param, ctx)

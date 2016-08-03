from   __future__ import unicode_literals
import os
import re
import signal
import six

def mail_quote(s):
    s = '> ' + re.sub(r'(\r(\n|(?!\n))|\n)(?=.)', '\n> ', s, flags=re.S)
    if not s.endswith("\n"):
        s += "\n"
    return s

def mime_text(msg):
    # Even if you say `decode=True`, get_payload still returns a `bytes` object
    return msg.get_payload(decode=True).decode('utf-8')

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
})

def show_argv(*argv):
    # Assumes that the elements of `argv` have been passed straight from the
    # command line without any modifications (i.e., each one is a bytes string
    # in Python 2 and a text string decoded with `os.fsdecode` in Python 3)

    # Just using `repr` for this isn't the best idea, as the quotes it adds
    # around simple (e.g., alphanumeric) arguments are unnecessary (or, for
    # strings like `"'$HOME'"`, just plain wrong).
    shown = ''
    for a in argv:
        if isinstance(a, six.text_type):
            a = os.fsencode(a)
        a = a.decode('iso-8859-1')
        if not re.match(r'^[-\w:+=.,/]+$', a):
            # `shlex.quote` only ever adds quotes; it doesn't even escape
            # backslashes!  I don't like it, and I'm not using it.
            a = re.sub(r"([\\'])", r'\\\1', a)
            b = a.translate(bash_slash)
            if a != b:
                a = "$'" + b + "'"
            else:
                a = "'" + a + "'"
        if shown:
            shown += ' '
        shown += a
    return shown

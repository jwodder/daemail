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

def show_argv(*argv):
    shown = ''
    for a in argv:
        if isinstance(a, six.text_type):
            a = os.fsencode(a)
        if not re.match(br'^[-\w:+=.,/]+$', a):
            # `shlex.quote` only ever adds quotes; it doesn't even escape
            # backslashes!  I don't like it, and I'm not using it.
            a = re.sub(br"([\\'])", br'\\\1', a)
            a = re.sub(
                br"[\x7F-\xFF]",
                lambda m: r'\x{:02x}'.format(six.byte2int(m.group()))\
                                     .encode('us-ascii'),
                a,
            )
            a = b"'" + a + b"'"
        a = a.decode('us-ascii')
        if shown:
            shown += ' '
        shown += a
    return shown

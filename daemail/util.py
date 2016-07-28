from   __future__ import unicode_literals
import email.charset
import re
import signal

utf8qp = email.charset.Charset('utf-8')
utf8qp.body_encoding = email.charset.QP

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

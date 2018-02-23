import email.charset
from   email.encoders         import encode_base64
from   email.message          import Message
from   email.mime.multipart   import MIMEMultipart
from   email.utils            import formataddr
import platform
from   .                      import __version__
from   .util                  import mail_quote

USER_AGENT = 'daemail {} ({} {})'.format(
    __version__, platform.python_implementation(), platform.python_version()
)

utf8qp = email.charset.Charset('utf-8')
utf8qp.body_encoding = email.charset.QP

class DraftMessage(object):
    def __init__(self, from_addr, to_addrs, subject):
        """
        :type from_addr: ``(realname, email_address)`` pair or `None`
        :type to_addrs: sequence of ``(realname, email_address)`` pairs
        """
        self.headers = {
            "To": ', '.join(map(formataddr, to_addrs)),
            "Subject": subject,
            "User-Agent": USER_AGENT,
        }
        if from_addr is not None:
            self.headers['From'] = formataddr(from_addr)
        self.parts = []  # list of strings and/or attachments

    def addtext(self, txt):
        if self.parts and isinstance(self.parts[-1], str):
            self.parts[-1] += txt
        else:
            self.parts.append(txt)

    def addblobquote(self, blob, encoding, filename):
        try:
            txt = blob.decode(encoding)
        except UnicodeDecodeError:
            self.parts.append(mkattachment(
                blob,
                mime_type='application/octet-stream',
                disposition='inline',
                filename=filename,
            ))
        else:
            self.addtext(mail_quote(txt))

    def addmimeblob(self, blob, mimetype, filename):
        self.parts.append(mkattachment(
            blob,
            mime_type=mimetype,
            disposition='inline',
            filename=filename,
        ))

    def compile(self):
        if not self.parts:
            msg = Message()
        elif len(self.parts) == 1 and isinstance(self.parts[0], str):
            msg = txt2mail(self.parts[0])
        else:
            msg = MIMEMultipart(_subparts=[
                txt2mail(p) if isinstance(p, str) else p for p in self.parts
            ])
        for k,v in self.headers.items():
            msg[k] = v
        return msg.as_bytes(unixfrom=False)


def txt2mail(txt):
    msg = Message()
    msg.set_payload(txt, utf8qp)
    return msg

def mkattachment(blob, mime_type, disposition, filename):
    attach = Message()
    attach['Content-Type'] = mime_type
    attach.add_header('Content-Disposition', disposition, filename=filename)
    attach.set_payload(blob)
    encode_base64(attach)
    return attach

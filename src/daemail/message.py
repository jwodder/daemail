from   email         import policy
from   email.message import EmailMessage
import platform
from   .             import __version__
from   .util         import mail_quote, split_content_type

USER_AGENT = 'daemail {} ({} {})'.format(
    __version__, platform.python_implementation(), platform.python_version()
)

POLICY = policy.default.clone(cte_type='7bit')

class DraftMessage:
    def __init__(self, from_addr, to_addrs, subject):
        """
        :type from_addr: email.headerregistry.Address or None
        :type to_addrs: Iterable[email.headerregistry.Address]
        :type subject: str
        """
        self.headers = {
            "To": list(to_addrs),
            "Subject": subject,
            "User-Agent": USER_AGENT,
        }
        if from_addr is not None:
            self.headers['From'] = from_addr
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
            self.addmimeblob(blob, 'application/octet-stream', filename)
        else:
            self.addtext(mail_quote(txt))

    def addmimeblob(self, blob, mimetype, filename):
        self.parts.append(mkattachment(
            blob,
            mime_type   = mimetype,
            disposition = 'inline',
            filename    = filename,
        ))

    def compile(self):
        if len(self.parts) == 1 and isinstance(self.parts[0], str):
            msg = txt2mail(self.parts[0])
        else:
            msg = EmailMessage(policy=POLICY)
            msg.make_mixed()
            for p in self.parts:
                ### TODO: Call add_attachment() instead?
                msg.attach(txt2mail(p) if isinstance(p, str) else p)
        for k,v in self.headers.items():
            msg[k] = v
        return msg


def txt2mail(txt):
    msg = EmailMessage(policy=POLICY)
    msg.set_content(txt)
    return msg

def mkattachment(blob, mime_type, disposition, filename):
    assert isinstance(blob, bytes)
    maintype, subtype, params = split_content_type(mime_type)
    attach = EmailMessage()
    attach.set_content(
        blob,
        maintype,
        subtype,
        disposition = disposition,
        filename    = filename,
        params      = params,
    )
    return attach

from   __future__             import unicode_literals
import email.charset
from   email.encoders         import encode_base64
from   email.message          import Message
from   email.mime.application import MIMEApplication
from   email.mime.multipart   import MIMEMultipart
from   email.mime.text        import MIMEText
from   six                    import PY2
from   .util                  import mail_quote, mime_text

utf8qp = email.charset.Charset('utf-8')
utf8qp.body_encoding = email.charset.QP

class DraftMessage(object):
    def __init__(self):
        self.headers = {}
        self._attached = []  # list of MIMEBAse objects
        self._trailing = ''

    def addtext(self, txt):
        self._trailing += txt

    def _endtext(self):
        if self._trailing:
            # In case of `addtext, _endtext, addtext, _endtext`:
            if self._attached and isinstance(self._attached[-1], MIMEText):
                last = self._attached[-1]
                last.set_payload(mime_text(last) + self._trailing, utf8qp)
            else:
                msg = MIMEText('', _charset=None)
                # No, `utf8qp` cannot be passed to MIMEText's constructor, as
                # it seems to expect a string (in Python 2.7, at least).
                msg.set_payload(self._trailing, utf8qp)
                self._attached.append(msg)
            self._trailing = ''

    def addblobquote(self, blob, encoding, filename):
        try:
            txt = blob.decode(encoding)
        except UnicodeDecodeError:
            self._endtext()
            attach = MIMEApplication(blob)
            attach.add_header('Content-Disposition', 'inline',
                              filename=filename)
            self._attached.append(attach)
        else:
            self.addtext(mail_quote(txt))

    def addmimeblob(self, blob, mimetype, filename):
        attach = Message()
        attach['Content-Type'] = mimetype
        attach.add_header('Content-Disposition', 'inline', filename=filename)
        attach.set_payload(blob)
        encode_base64(attach)
        self._endtext()
        self._attached.append(attach)

    def compile(self):
        self._endtext()
        if not self._attached:
            msg = MIMEText('', _charset=None)
        elif len(self._attached) == 1 and \
                isinstance(self._attached[0], MIMEText):
            # Copy the payload so that we don't set any headers on the
            # attachment itself, which would cause problems if `compile` is
            # later called again after more attachments have been added
            msg = MIMEText('', _charset=None)
            msg.set_payload(mime_text(self._attached[0]), utf8qp)
        else:
            msg = MIMEMultipart(_subparts=self._attached)
        for k,v in self.headers.items():
            msg[k] = v
        if PY2:
            return msg.as_string(unixfrom=False)
        else:
            return msg.as_bytes(unixfrom=False)

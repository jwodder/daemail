from   email.headerregistry import Address
from   email.message        import EmailMessage
import platform
from   typing               import Iterable, List, Optional, Union
import attr
import eletter
from   eletter              import BytesAttachment, MailItem, TextBody, \
                                        reply_quote
from   .                    import __url__, __version__

USER_AGENT = 'daemail/{} ({}) eletter/{} {}/{}'.format(
    __version__,
    __url__,
    eletter.__version__,
    platform.python_implementation(),
    platform.python_version()
)

def address_list(addrs: Iterable[Address]) -> List[Address]:
    return list(addrs)

@attr.s(auto_attribs=True)
class DraftMessage:
    from_addr: Optional[Address]
    to_addrs: List[Address] = attr.ib(converter=address_list)
    subject: str
    # List of strings and/or attachments:
    parts: List[Union[str, MailItem]] = attr.ib(factory=list, init=False)

    def addtext(self, txt: str) -> None:
        if self.parts and isinstance(self.parts[-1], str):
            self.parts[-1] += txt
        else:
            self.parts.append(txt)

    def addblobquote(self, blob: bytes, encoding: str, filename: str) -> None:
        try:
            txt = blob.decode(encoding)
        except UnicodeDecodeError:
            self.parts.append(BytesAttachment(blob, filename, inline=True))
        else:
            self.addtext(reply_quote(txt))

    def addmimeblob(self, blob, mimetype, filename):
        self.parts.append(BytesAttachment(
            blob,
            filename     = filename,
            content_type = mimetype,
            inline       = True,
        ))

    def compile(self) -> EmailMessage:
        msg: MailItem = TextBody(self.parts[0])
        for p in self.parts[1:]:
            msg &= p
        return msg.compose(
            subject=self.subject,
            from_=self.from_addr,
            to=self.to_addrs,
            headers={"User-Agent": USER_AGENT},
        )

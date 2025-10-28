from __future__ import annotations
from dataclasses import dataclass, field
from email.headerregistry import Address
from email.message import EmailMessage
import platform
import eletter
from eletter import BytesAttachment, MailItem, TextBody, reply_quote
import outgoing
from . import __url__, __version__

USER_AGENT = "daemail/{} ({}) outgoing/{} eletter/{} {}/{}".format(
    __version__,
    __url__,
    outgoing.__version__,
    eletter.__version__,
    platform.python_implementation(),
    platform.python_version(),
)


@dataclass
class DraftMessage:
    from_addr: Address | None
    to_addrs: list[Address]
    subject: str
    # List of strings and/or attachments:
    parts: list[str | MailItem] = field(init=False, default_factory=list)

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

    def addmimeblob(self, blob: bytes, mimetype: str, filename: str) -> None:
        self.parts.append(
            BytesAttachment(
                blob,
                filename=filename,
                content_type=mimetype,
                inline=True,
            )
        )

    def compile(self) -> EmailMessage:  # noqa: A003
        msg: MailItem
        if isinstance(self.parts[0], str):
            msg = TextBody(self.parts[0])
        else:
            msg = self.parts[0]
        for p in self.parts[1:]:
            msg &= p
        return msg.compose(
            subject=self.subject,
            from_=self.from_addr,
            to=self.to_addrs,
            headers={"User-Agent": USER_AGENT},
        )

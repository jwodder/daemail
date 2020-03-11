"""
Classes for testing that an EmailMessage object meets a given specification
"""

from   collections          import namedtuple
from   email.headerregistry import Address
from   email.message        import EmailMessage, Message
import pytest

class TextMessage(namedtuple('TextMessage', 'headers body')):
    def assert_match(self, msg):
        assert isinstance(msg, Message), 'msg is not a Message'
        for k,v in self.headers.items():
            msg_v = msg[k]
            if hasattr(msg_v, 'addresses'):
                msg_v = msg_v.addresses
            assert msg_v == v
        assert msg["Content-Type"].content_type == 'text/plain'
        assert not msg.is_multipart()
        assert msg.get_content() == self.body


class MixedMessage(namedtuple('Message', 'headers parts')):
    def assert_match(self, msg):
        assert isinstance(msg, Message), 'msg is not a Message'
        for k,v in self.headers.items():
            msg_v = msg[k]
            if hasattr(msg_v, 'addresses'):
                msg_v = msg_v.addresses
            assert msg_v == v
        assert msg["Content-Type"].content_type == 'multipart/mixed'
        assert msg.is_multipart()
        parts = list(msg.iter_parts())
        assert len(parts) == len(self.parts)
        for spec, actual in zip(self.parts, parts):
            spec.assert_match(actual)


class Text(namedtuple('Text', 'body')):
    def assert_match(self, msg):
        assert msg["Content-Type"].content_type == 'text/plain'
        assert not msg.is_multipart()
        assert msg.get_content() == self.body


class Attachment(namedtuple('Attachment', 'disposition filename mime_type body')):
    def assert_match(self, msg):
        assert isinstance(msg, Message), 'msg is not a Message'
        assert msg.get_content_disposition() == self.disposition
        assert msg.get_filename() == self.filename
        assert msg["Content-Type"] == self.mime_type
        assert not msg.is_multipart()
        body = msg.get_content()
        if msg["Content-Type"].maintype == 'text':
            # body is a str that must be encoded to bytes (the type of
            # self.body)
            charset = msg.get_content_charset()
            if charset is None:
                charset = 'utf-8'  ### ???
            body = body.encode(charset)
        assert body == self.body

msg1 = EmailMessage()
msg1.set_content('This is test text.')

spec1 = TextMessage({}, 'This is test text.\n')

msg2 = EmailMessage()
msg2.set_content('Look at the fancy headers!')
msg2.set_param('charset', 'utf-8')
msg2["Subject"] = 'This e-mail has headers.'
msg2["From"] = Address('Joe Q. Sender', addr_spec='from@example.nil')
msg2["To"] = [
    Address(addr_spec='to@example.test'),
    Address('Jane Q. Recipient', addr_spec='jane@example.com')
]

spec2 = TextMessage(
    {
        "Content-Type": "text/plain; charset=\"utf-8\"",
        "Subject": 'This e-mail has headers.',
        "From": (Address('Joe Q. Sender', addr_spec='from@example.nil'),),
        "To": (
            Address(addr_spec='to@example.test'),
            Address('Jane Q. Recipient', addr_spec='jane@example.com')
        ),
    },
    'Look at the fancy headers!\n',
)

PNG = bytes.fromhex(
    '89 50 4e 47 0d 0a 1a 0a  00 00 00 0d 49 48 44 52'
    '00 00 00 10 00 00 00 10  08 06 00 00 00 1f f3 ff'
    '61 00 00 00 06 62 4b 47  44 00 ff 00 ff 00 ff a0'
    'bd a7 93 00 00 00 09 70  48 59 73 00 00 00 48 00'
    '00 00 48 00 46 c9 6b 3e  00 00 00 09 76 70 41 67'
    '00 00 00 10 00 00 00 10  00 5c c6 ad c3 00 00 00'
    '5b 49 44 41 54 38 cb c5  92 51 0a c0 30 08 43 7d'
    'b2 fb 5f 39 fb 12 da 61  a9 c3 8e f9 a7 98 98 48'
    '90 64 9d f2 16 da cc ae  b1 01 26 39 92 d8 11 10'
    '16 9e e0 8c 64 dc 89 b9  67 80 ca e5 f3 3f a8 5c'
    'cd 76 52 05 e1 b5 42 ea  1d f0 91 1f b4 09 78 13'
    'e5 52 0e 00 ad 42 f5 bf  85 4f 14 dc 46 b3 32 11'
    '6c b1 43 99 00 00 00 00  49 45 4e 44 ae 42 60 82'
)

submsg3a = EmailMessage()
submsg3a.set_content('This is part 1.\n')

submsg3b = EmailMessage()
submsg3b.set_content(
    PNG,
    'image',
    'png',
    disposition = 'inline',
    filename = 'ternary.png',
)

msg3 = EmailMessage()
msg3["Subject"] = 'Text and an image'
msg3.make_mixed()
msg3.attach(submsg3a)
msg3.attach(submsg3b)

spec3 = MixedMessage(
    {"Subject": "Text and an image"},
    [
        Text('This is part 1.\n'),
        Attachment('inline', 'ternary.png', 'image/png', PNG),
    ],
)

@pytest.mark.parametrize('msg,spec', [
    (msg1, spec1),
    (msg2, spec2),
    (msg3, spec3),
])
def test_assert_match(msg, spec):
    spec.assert_match(msg)

@pytest.mark.parametrize('msg,spec', [
    (msg1, spec2),
    (msg1, spec3),
    (msg2, spec1),
    (msg2, spec3),
])
def test_assert_not_match(msg, spec):
    with pytest.raises(AssertionError):
        spec.assert_match(msg)

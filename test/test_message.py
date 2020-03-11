from   base64                import b64encode
from   email.headerregistry  import Address
import quopri
from   daemail.message       import DraftMessage, USER_AGENT
from   daemail.util          import parse_address
from   test_lib_emailmatcher import Attachment, MixedMessage, Text, TextMessage

TEXT = 'àéîøü\n'
# Something in the email module implicitly adds a newline to the body text if
# one isn't present, so we need to include one here lest the base64 encodings
# not match up.
TEXT_ENC = TEXT.encode('utf-8')

def test_7bit_text():
    msg = DraftMessage(
        from_addr=parse_address('from@example.com'),
        to_addrs=[parse_address('to@example.com')],
        subject='test_7bit_text',
    )
    msg.addtext(TEXT)
    blob = bytes(msg.compile())
    assert isinstance(blob, bytes)
    assert TEXT_ENC not in blob
    assert quopri.encodestring(TEXT_ENC) in blob or b64encode(TEXT_ENC) in blob

def test_7bit_multipart():
    msg = DraftMessage(
        from_addr=parse_address('from@example.com'),
        to_addrs=[parse_address('to@example.com')],
        subject='test_7bit_multipart',
    )
    msg.addtext(TEXT)
    msg.addmimeblob(b'\0\0\0\0', 'application/octet-stream', 'null.dat')
    blob = bytes(msg.compile())
    assert isinstance(blob, bytes)
    assert TEXT_ENC not in blob
    assert quopri.encodestring(TEXT_ENC) in blob or b64encode(TEXT_ENC) in blob

def test_compile_text():
    from_addr = Address('Joe Q. Sender', addr_spec='joe@example.nil')
    to_addrs = (
        Address(addr_spec='me@example.com'),
        Address('Jane Q. Recipient', addr_spec='jane@example.org'),
    )
    draft = DraftMessage(
        from_addr = from_addr,
        to_addrs = to_addrs,
        subject = 'This is a test e-mail.',
    )
    draft.addtext(TEXT)
    spec = TextMessage(
        {
            "Subject": "This is a test e-mail.",
            "From": (from_addr,),
            "To": to_addrs,
            "User-Agent": USER_AGENT,
        },
        TEXT,
    )
    spec.assert_match(draft.compile())

def test_compile_text_no_from():
    to_addrs = (
        Address(addr_spec='me@example.com'),
        Address('Jane Q. Recipient', addr_spec='jane@example.org'),
    )
    draft = DraftMessage(
        from_addr = None,
        to_addrs = to_addrs,
        subject = 'This is a test e-mail.',
    )
    draft.addtext(TEXT)
    spec = TextMessage(
        {
            "Subject": "This is a test e-mail.",
            "To": to_addrs,
            "User-Agent": USER_AGENT,
        },
        TEXT,
    )
    msg = draft.compile()
    spec.assert_match(msg)
    assert 'From' not in msg

def test_compile_multiline_text():
    from_addr = Address('Joe Q. Sender', addr_spec='joe@example.nil')
    to_addrs = (
        Address(addr_spec='me@example.com'),
        Address('Jane Q. Recipient', addr_spec='jane@example.org'),
    )
    draft = DraftMessage(
        from_addr = from_addr,
        to_addrs = to_addrs,
        subject = 'This is a test e-mail.',
    )
    draft.addtext('This is line 1.\n')
    draft.addtext('This is line 2.\n')
    spec = TextMessage(
        {
            "Subject": "This is a test e-mail.",
            "From": (from_addr,),
            "To": to_addrs,
            "User-Agent": USER_AGENT,
        },
        'This is line 1.\nThis is line 2.\n',
    )
    spec.assert_match(draft.compile())

def test_compile_text_blob_text():
    from_addr = Address('Joe Q. Sender', addr_spec='joe@example.nil')
    to_addrs = (
        Address(addr_spec='me@example.com'),
        Address('Jane Q. Recipient', addr_spec='jane@example.org'),
    )
    draft = DraftMessage(
        from_addr = from_addr,
        to_addrs = to_addrs,
        subject = 'This is a test e-mail.',
    )
    draft.addtext('This is line 1.\n')
    draft.addmimeblob(
        b'\xDE\xAD\xBE\xEF',
        'application/octet-stream',
        'deadbeef.dat',
    )
    draft.addtext('This is line 2.\n')
    spec = MixedMessage(
        {
            "Subject": "This is a test e-mail.",
            "From": (from_addr,),
            "To": to_addrs,
            "User-Agent": USER_AGENT,
        },
        [
            Text('This is line 1.\n'),
            Attachment(
                'inline',
                'deadbeef.dat',
                'application/octet-stream',
                b'\xDE\xAD\xBE\xEF',
            ),
            Text('This is line 2.\n'),
        ],
    )
    spec.assert_match(draft.compile())

def test_compile_text_quote():
    from_addr = Address('Joe Q. Sender', addr_spec='joe@example.nil')
    to_addrs = (
        Address(addr_spec='me@example.com'),
        Address('Jane Q. Recipient', addr_spec='jane@example.org'),
    )
    draft = DraftMessage(
        from_addr = from_addr,
        to_addrs = to_addrs,
        subject = 'This is a test e-mail.',
    )
    draft.addtext('This is a quote:\n')
    draft.addblobquote(
        b'\xD0is is i\xF1 L\xE1tin\xB9.\n',
        'iso-8859-1',
        'latin1.txt',
    )
    spec = TextMessage(
        {
            "Subject": "This is a test e-mail.",
            "From": (from_addr,),
            "To": to_addrs,
            "User-Agent": USER_AGENT,
        },
        'This is a quote:\n> \xD0is is i\xF1 L\xE1tin\xB9.\n',
    )
    spec.assert_match(draft.compile())

def test_compile_text_undecodable_quote():
    from_addr = Address('Joe Q. Sender', addr_spec='joe@example.nil')
    to_addrs = (
        Address(addr_spec='me@example.com'),
        Address('Jane Q. Recipient', addr_spec='jane@example.org'),
    )
    draft = DraftMessage(
        from_addr = from_addr,
        to_addrs = to_addrs,
        subject = 'This is a test e-mail.',
    )
    draft.addtext('This is a quote:\n')
    draft.addblobquote(
        b'\xD0is is i\xF1 L\xE1tin\xB9.\n',
        'utf-8',
        'latin1.txt',
    )
    spec = MixedMessage(
        {
            "Subject": "This is a test e-mail.",
            "From": (from_addr,),
            "To": to_addrs,
            "User-Agent": USER_AGENT,
        },
        [
            Text('This is a quote:\n'),
            Attachment(
                'inline',
                'latin1.txt',
                'application/octet-stream',
                b'\xD0is is i\xF1 L\xE1tin\xB9.\n',
            ),
        ],
    )
    spec.assert_match(draft.compile())

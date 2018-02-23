from   base64          import b64encode
import quopri
from   daemail.message import DraftMessage

TEXT = 'àéîøü\n'
# Something in the email module implicitly adds a newline to the body text if
# one isn't present, so we need to include one here lest the base64 encodings
# not match up.
TEXT_ENC = TEXT.encode('utf-8')

def test_7bit_text():
    msg = DraftMessage()
    msg.addtext(TEXT)
    blob = msg.compile()
    assert isinstance(blob, bytes)
    assert TEXT_ENC not in blob
    assert quopri.encodestring(TEXT_ENC) in blob or b64encode(TEXT_ENC) in blob

def test_7bit_multipart():
    msg = DraftMessage()
    msg.addtext(TEXT)
    msg.addmimeblob(b'\0\0\0\0', 'application/octet-stream', 'null.dat')
    blob = msg.compile()
    assert isinstance(blob, bytes)
    assert TEXT_ENC not in blob
    assert quopri.encodestring(TEXT_ENC) in blob or b64encode(TEXT_ENC) in blob

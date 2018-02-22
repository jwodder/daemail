import quopri
from   daemail.message import DraftMessage

TEXT = 'àéîøü'

def test_quopri_text():
    msg = DraftMessage()
    msg.addtext(TEXT)
    blob = msg.compile()
    assert isinstance(blob, bytes)
    assert TEXT.encode('utf-8') not in blob
    assert quopri.encodestring(TEXT.encode('utf-8')) in blob

def test_quopri_multipart():
    msg = DraftMessage()
    msg.addtext(TEXT)
    msg.addmimeblob(r'\0\0\0\0', 'application/octet-stream', 'null.dat')
    blob = msg.compile()
    assert isinstance(blob, bytes)
    assert TEXT.encode('utf-8') not in blob
    assert quopri.encodestring(TEXT.encode('utf-8')) in blob

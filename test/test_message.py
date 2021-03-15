from   email.headerregistry import Address
from   typing               import Dict
from   mailbits             import email2dict
from   daemail.message      import DraftMessage, USER_AGENT

TEXT = 'àéîøü\n'

def addr2dict(addr: Address) -> Dict[str, str]:
    return {
        "display_name": addr.display_name,
        "address": addr.addr_spec,
    }

def test_compile_text() -> None:
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
    assert email2dict(draft.compile()) == {
        "unixfrom": None,
        "headers": {
            "subject": "This is a test e-mail.",
            "from": [addr2dict(from_addr)],
            "to": list(map(addr2dict, to_addrs)),
            "user-agent": [USER_AGENT],
            "content-type": {
                "content_type": "text/plain",
                "params": {},
            },
        },
        "preamble": None,
        "content": TEXT,
        "epilogue": None,
    }

def test_compile_text_no_from() -> None:
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
    assert email2dict(draft.compile()) == {
        "unixfrom": None,
        "headers": {
            "subject": "This is a test e-mail.",
            "to": list(map(addr2dict, to_addrs)),
            "user-agent": [USER_AGENT],
            "content-type": {
                "content_type": "text/plain",
                "params": {},
            },
        },
        "preamble": None,
        "content": TEXT,
        "epilogue": None,
    }

def test_compile_multiline_text() -> None:
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
    assert email2dict(draft.compile()) == {
        "unixfrom": None,
        "headers": {
            "subject": "This is a test e-mail.",
            "from": [addr2dict(from_addr)],
            "to": list(map(addr2dict, to_addrs)),
            "user-agent": [USER_AGENT],
            "content-type": {
                "content_type": "text/plain",
                "params": {},
            },
        },
        "preamble": None,
        "content": 'This is line 1.\nThis is line 2.\n',
        "epilogue": None,
    }

def test_compile_text_blob_text() -> None:
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
    assert email2dict(draft.compile()) == {
        "unixfrom": None,
        "headers": {
            "subject": "This is a test e-mail.",
            "from": [addr2dict(from_addr)],
            "to": list(map(addr2dict, to_addrs)),
            "user-agent": [USER_AGENT],
            "content-type": {
                "content_type": "multipart/mixed",
                "params": {},
            },
        },
        "preamble": None,
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": 'This is line 1.\n',
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "application/octet-stream",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "inline",
                        "params": {"filename": "deadbeef.dat"},
                    },
                },
                "preamble": None,
                "content": b'\xDE\xAD\xBE\xEF',
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": 'This is line 2.\n',
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }

def test_compile_text_quote() -> None:
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
    assert email2dict(draft.compile()) == {
        "unixfrom": None,
        "headers": {
            "subject": "This is a test e-mail.",
            "from": [addr2dict(from_addr)],
            "to": list(map(addr2dict, to_addrs)),
            "user-agent": [USER_AGENT],
            "content-type": {
                "content_type": "text/plain",
                "params": {},
            },
        },
        "preamble": None,
        "content": 'This is a quote:\n> \xD0is is i\xF1 L\xE1tin\xB9.\n',
        "epilogue": None,
    }

def test_compile_text_undecodable_quote() -> None:
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
    assert email2dict(draft.compile()) == {
        "unixfrom": None,
        "headers": {
            "subject": "This is a test e-mail.",
            "from": [addr2dict(from_addr)],
            "to": list(map(addr2dict, to_addrs)),
            "user-agent": [USER_AGENT],
            "content-type": {
                "content_type": "multipart/mixed",
                "params": {},
            },
        },
        "preamble": None,
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": 'This is a quote:\n',
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "application/octet-stream",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "inline",
                        "params": {"filename": "latin1.txt"},
                    },
                },
                "preamble": None,
                "content": b'\xD0is is i\xF1 L\xE1tin\xB9.\n',
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }

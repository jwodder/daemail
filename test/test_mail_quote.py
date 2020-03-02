import pytest
from   daemail.util import mail_quote

@pytest.mark.parametrize('inp,output', [
    ('', '> \n'),
    ('\n', '> \n'),
    ('Insert output here.', '> Insert output here.\n'),
    ('Insert output here.\n', '> Insert output here.\n'),
    (
        'Insert output here.\nOutsert input there.',
        '> Insert output here.\n> Outsert input there.\n',
    ),
    (
        'Insert output here.\nOutsert input there.\n',
        '> Insert output here.\n> Outsert input there.\n',
    ),
    (
        'Insert output here.\r\nOutsert input there.\r\n',
        '> Insert output here.\n> Outsert input there.\n',
    ),
    (
        'Insert output here.\rOutsert input there.\r',
        '> Insert output here.\n> Outsert input there.\n',
    ),
])
def test_mail_quote(inp, output):
    assert mail_quote(inp) == output

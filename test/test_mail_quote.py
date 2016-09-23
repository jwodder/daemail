from   __future__   import unicode_literals
from   daemail.util import mail_quote

def test_mail_quote_nothing():
    assert mail_quote('') == '> \n'

def test_mail_quote_newline():
    assert mail_quote('\n') == '> \n'

def test_mail_quote_no_newline():
    assert mail_quote('Insert output here.') == '> Insert output here.\n'

def test_mail_quote_one_line():
    assert mail_quote('Insert output here.\n') == '> Insert output here.\n'

def test_mail_quote_inner_newline():
    assert mail_quote('Insert output here.\nOutsert input there.') == \
        '> Insert output here.\n> Outsert input there.\n'

def test_mail_quote_two_lines():
    assert mail_quote('Insert output here.\nOutsert input there.\n') == \
        '> Insert output here.\n> Outsert input there.\n'

def test_mail_quote_crlf():
    assert mail_quote('Insert output here.\r\nOutsert input there.\r\n') == \
        '> Insert output here.\n> Outsert input there.\n'

def test_mail_quote_carriage_returns():
    assert mail_quote('Insert output here.\rOutsert input there.\r') == \
        '> Insert output here.\n> Outsert input there.\n'

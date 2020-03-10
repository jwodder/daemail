from   email.headerregistry import Address
import pytest
from   daemail.util         import mail_quote, parse_address, show_argv

@pytest.mark.parametrize('argv,output', [
    ([], ''),
    ([''], "''"),
    (['foo'], 'foo'),
    (['foo', 'bar'], 'foo bar'),
    (["foo\0bar"], r"$'foo\x00bar'"),
    (["foo\abar"], r"$'foo\abar'"),
    (["foo\bbar"], r"$'foo\bbar'"),
    (["foo\tbar"], r"$'foo\tbar'"),
    (["foo\nbar"], r"$'foo\nbar'"),
    (["foo\vbar"], r"$'foo\vbar'"),
    (["foo\fbar"], r"$'foo\fbar'"),
    (["foo\rbar"], r"$'foo\rbar'"),
    (["foo\x1Bbar"], r"$'foo\ebar'"),
    (['foo bar'], "'foo bar'"),
    (["foo!bar"], "'foo!bar'"),
    (["foo\"bar"], "'foo\"bar'"),
    (["foo#bar"], "'foo#bar'"),
    (["foo$bar"], "'foo$bar'"),
    (["foo%bar"], "foo%bar"),
    (["foo&bar"], "'foo&bar'"),
    (["foo'bar"], "'foo'\"'\"'bar'"),
    (["foo(bar"], "'foo(bar'"),
    (["foo)bar"], "'foo)bar'"),
    (["foo*bar"], r"'foo*bar'"),
    (["foo+bar"], "foo+bar"),
    (["foo,bar"], "foo,bar"),
    (["foo-bar"], "foo-bar"),
    (["foo.bar"], "foo.bar"),
    (["foo/bar"], "foo/bar"),
    (["foo:bar"], "foo:bar"),
    (["foo;bar"], "'foo;bar'"),
    (["foo<bar"], "'foo<bar'"),
    (["foo=bar"], r"'foo=bar'"),
    (["foo=bar", "bar=baz"], r"'foo=bar' 'bar=baz'"),
    (["foo=bar", "bar=baz", "quux"], r"'foo=bar' 'bar=baz' quux"),
    (["foo=bar", "quux"], r"'foo=bar' quux"),
    (["foo=bar", "quux", "bar=baz"], r"'foo=bar' quux bar=baz"),
    (["foo", 'bar=baz'], r"foo bar=baz"),
    (['foo=bar=quux', 'glarch'], r"'foo=bar=quux' glarch"),
    (["foo>bar"], "'foo>bar'"),
    (["foo?bar"], "'foo?bar'"),
    (["foo@bar"], "foo@bar"),
    (["foo[bar"], "'foo[bar'"),
    (['foo\\bar'], r"'foo\bar'"),
    (['foo\\'], r"'foo\'"),
    (["foo]bar"], "'foo]bar'"),
    (["foo^bar"], "'foo^bar'"),
    (["foo_bar"], "foo_bar"),
    (["foo`bar"], "'foo`bar'"),
    (["foo{bar"], "'foo{bar'"),
    (["foo|bar"], "'foo|bar'"),
    (["foo}bar"], "'foo}bar'"),
    (["foo~bar"], "'foo~bar'"),
    (['foo\x7Fbar'], r"$'foo\x7fbar'"),
    (['foo\udc80bar'], r"$'foo\x80bar'"),
    ### TODO: This assumes sys.getfilesystemencoding() == 'utf-8':
    (['fooébar'], r"$'foo\xc3\xa9bar'"),
])
def test_show_argv(argv, output):
    assert show_argv(*argv) == output

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

@pytest.mark.parametrize('s,addr', [
    ('person@example.com', Address('', addr_spec='person@example.com')),
    ('<person@example.com>', Address('', addr_spec='person@example.com')),
    (
        'Linus User <person@example.com>',
        Address('Linus User', addr_spec='person@example.com'),
    ),
    (
        '"Linus User" <person@example.com>',
        Address('Linus User', addr_spec='person@example.com'),
    ),
])
def test_parse_address(s, addr):
    assert parse_address(s) == addr

@pytest.mark.parametrize('s', [
    '',
    'person',
    'Me <person>',
    '@example.com',
    '<@example.com>',
    'Me <@example.com>',
    'person@example.com, foo@bar.org',
    'Me',
    'person@example.com foo@bar.org',
])
def test_parse_address_error(s):
    with pytest.raises(ValueError):
        parse_address(s)
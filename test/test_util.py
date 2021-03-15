from   datetime     import datetime, timedelta, timezone
from   typing       import List
import pytest
from   daemail.util import dt2stamp, get_mime_type, multiline822, show_argv

w4 = timezone(timedelta(hours=-4))

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
def test_show_argv(argv: List[str], output: str) -> None:
    assert show_argv(*argv) == output

@pytest.mark.parametrize('dt,slocal,sutc', [
    (
        datetime(2020, 3, 10, 15, 0, 28, 123456, w4),
        '2020-03-10 15:00:28.123456-04:00',
        '2020-03-10 19:00:28.123456Z',
    ),
    (
        datetime(2020, 3, 10, 15, 0, 28, 123456, timezone.utc),
        '2020-03-10 15:00:28.123456+00:00',
        '2020-03-10 15:00:28.123456Z',
    ),
    (
        datetime(2020, 3, 10, 15, 0, 28, tzinfo=w4),
        '2020-03-10 15:00:28-04:00',
        '2020-03-10 19:00:28Z',
    ),
    (
        datetime(2020, 3, 10, 15, 0, 28, tzinfo=timezone.utc),
        '2020-03-10 15:00:28+00:00',
        '2020-03-10 15:00:28Z',
    ),
])
def test_dt2stamp(dt: datetime, slocal: str, sutc: str) -> None:
    assert dt2stamp(dt) == slocal
    assert dt2stamp(dt, utc=False) == slocal
    assert dt2stamp(dt, utc=True) == sutc

@pytest.mark.parametrize('sin,sout', [
    ('', '  .'),
    ('\n', '  .'),
    ('This is test text.', '  This is test text.'),
    ('This is test text.\n', '  This is test text.'),
    (
        'This is test text.\n\nThat was a blank line.',
        '  This is test text.\n  .\n  That was a blank line.',
    ),
])
def test_multiline822(sin: str, sout: str) -> None:
    assert multiline822(sin) == sout

@pytest.mark.parametrize('filename,mtype', [
    ('foo.txt',     'text/plain'),
    ('foo',         'application/octet-stream'),
    ('foo.gz',      'application/gzip'),
    ('foo.tar.gz',  'application/gzip'),
    ('foo.tgz',     'application/gzip'),
    ('foo.taz',     'application/gzip'),
    ('foo.svg.gz',  'application/gzip'),
    ('foo.svgz',    'application/gzip'),
    ('foo.Z',       'application/x-compress'),
    ('foo.tar.Z',   'application/x-compress'),
    ('foo.bz2',     'application/x-bzip2'),
    ('foo.tar.bz2', 'application/x-bzip2'),
    ('foo.tbz2',    'application/x-bzip2'),
    ('foo.xz',      'application/x-xz'),
    ('foo.tar.xz',  'application/x-xz'),
    ('foo.txz',     'application/x-xz'),
])
def test_get_mime_type(filename: str, mtype: str) -> None:
    assert get_mime_type(filename) == mtype

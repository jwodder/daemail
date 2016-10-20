# -*- coding: utf-8 -*-
import sys
import pytest
from   daemail.util import show_argv

def test_show_argv_nothing():
    assert show_argv() == ''

def test_show_argv_empty():
    assert show_argv('') == "''"

def test_show_argv_1simple():
    assert show_argv('foo') == 'foo'

def test_show_argv_2simple():
    assert show_argv('foo', 'bar') == 'foo bar'

def test_show_argv_null():
    assert show_argv("foo\0bar") == r"$'foo\x00bar'"

def test_show_argv_bell():
    assert show_argv("foo\abar") == r"$'foo\abar'"

def test_show_argv_backspace():
    assert show_argv("foo\bbar") == r"$'foo\bbar'"

def test_show_argv_tab():
    assert show_argv("foo\tbar") == r"$'foo\tbar'"

def test_show_argv_linefeed():
    assert show_argv("foo\nbar") == r"$'foo\nbar'"

def test_show_argv_verticaltab():
    assert show_argv("foo\vbar") == r"$'foo\vbar'"

def test_show_argv_formfeed():
    assert show_argv("foo\fbar") == r"$'foo\fbar'"

def test_show_argv_return():
    assert show_argv("foo\rbar") == r"$'foo\rbar'"

def test_show_argv_escape():
    assert show_argv("foo\x1Bbar") == r"$'foo\ebar'"

def test_show_argv_space():
    assert show_argv('foo bar') == "'foo bar'"

def test_show_argv_exclamation():
    assert show_argv("foo!bar") == "'foo!bar'"

def test_show_argv_quote():
    assert show_argv("foo\"bar") == "'foo\"bar'"

def test_show_argv_hash():
    assert show_argv("foo#bar") == "'foo#bar'"

def test_show_argv_dollar():
    assert show_argv("foo$bar") == "'foo$bar'"

def test_show_argv_percent():
    assert show_argv("foo%bar") == "foo%bar"

def test_show_argv_ampersand():
    assert show_argv("foo&bar") == "'foo&bar'"

def test_show_argv_apostrophe():
    assert show_argv("foo'bar") == "'foo'\"'\"'bar'"

def test_show_argv_leftparen():
    assert show_argv("foo(bar") == "'foo(bar'"

def test_show_argv_rightparen():
    assert show_argv("foo)bar") == "'foo)bar'"

def test_show_argv_asterisk():
    assert show_argv("foo*bar") == r"'foo*bar'"

def test_show_argv_plus():
    assert show_argv("foo+bar") == "foo+bar"

def test_show_argv_comma():
    assert show_argv("foo,bar") == "foo,bar"

def test_show_argv_hyphen():
    assert show_argv("foo-bar") == "foo-bar"

def test_show_argv_period():
    assert show_argv("foo.bar") == "foo.bar"

def test_show_argv_slash():
    assert show_argv("foo/bar") == "foo/bar"

def test_show_argv_colon():
    assert show_argv("foo:bar") == "foo:bar"

def test_show_argv_semicolon():
    assert show_argv("foo;bar") == "'foo;bar'"

def test_show_argv_lessthan():
    assert show_argv("foo<bar") == "'foo<bar'"

def test_show_argv_equals():
    assert show_argv("foo=bar") == r"'foo=bar'"

def test_show_argv_2equals():
    assert show_argv("foo=bar", "bar=baz") == r"'foo=bar' 'bar=baz'"

def test_show_argv_2equals_plain():
    assert show_argv("foo=bar", "bar=baz", "quux") == r"'foo=bar' 'bar=baz' quux"

def test_show_argv_equals_plain():
    assert show_argv("foo=bar", "quux") == r"'foo=bar' quux"

def test_show_argv_equals_plain_equals():
    assert show_argv("foo=bar", "quux", "bar=baz") == r"'foo=bar' quux bar=baz"

def test_show_argv_plain_equals():
    assert show_argv("foo", 'bar=baz') == r"foo bar=baz"

def test_show_argv_chained_equals():
    assert show_argv('foo=bar=quux', 'glarch') == r"'foo=bar=quux' glarch"

def test_show_argv_greaterthan():
    assert show_argv("foo>bar") == "'foo>bar'"

def test_show_argv_question():
    assert show_argv("foo?bar") == "'foo?bar'"

def test_show_argv_at():
    assert show_argv("foo@bar") == "foo@bar"

def test_show_argv_leftbracket():
    assert show_argv("foo[bar") == "'foo[bar'"

def test_show_argv_backslash():
    assert show_argv('foo\\bar') == r"'foo\bar'"

def test_show_argv_backslash_end():
    assert show_argv('foo\\') == r"'foo\'"

def test_show_argv_rightbracket():
    assert show_argv("foo]bar") == "'foo]bar'"

def test_show_argv_caret():
    assert show_argv("foo^bar") == "'foo^bar'"

def test_show_argv_underscore():
    assert show_argv("foo_bar") == "foo_bar"

def test_show_argv_backtick():
    assert show_argv("foo`bar") == "'foo`bar'"

def test_show_argv_leftbrace():
    assert show_argv("foo{bar") == "'foo{bar'"

def test_show_argv_vbar():
    assert show_argv("foo|bar") == "'foo|bar'"

def test_show_argv_rightbrace():
    assert show_argv("foo}bar") == "'foo}bar'"

def test_show_argv_tilde():
    assert show_argv("foo~bar") == "'foo~bar'"

def test_show_argv_delete():
    assert show_argv('foo\x7Fbar') == r"$'foo\x7fbar'"

@pytest.mark.skipif(sys.version_info[0]>2, reason='argv is text in Python 3')
def test_show_argv_nbsp():
    assert show_argv('foo\xA0bar') == r"$'foo\xa0bar'"

@pytest.mark.skipif(sys.version_info[0]>2, reason='argv is text in Python 3')
def test_show_argv_8bits():
    assert show_argv('foo\xFFbar') == r"$'foo\xffbar'"

@pytest.mark.skipif(sys.version_info[0]>2, reason='argv is text in Python 3')
def test_show_argv_utf8():
    assert show_argv('foo\xC3\xA9bar') == r"$'foo\xc3\xa9bar'"

@pytest.mark.skipif(sys.version_info[0]<3, reason='argv is bytes in Python 2')
def test_show_argv_surrogateesc():
    assert show_argv('foo\udc80bar') == r"$'foo\x80bar'"

@pytest.mark.skipif(sys.version_info[0]<3, reason='argv is bytes in Python 2')
def test_show_argv_unicode():
    ### TODO: Assumes sys.getfilesystemencoding() == 'utf-8'
    assert show_argv('fooébar') == r"$'foo\xc3\xa9bar'"

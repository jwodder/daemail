# -*- coding: utf-8 -*-
import sys
from   daemail.util import show_argv

def test_show_argv_nothing():
    assert show_argv() == ''

def test_show_argv_empty():
    assert show_argv('') == "''"

def test_show_argv_1simple():
    assert show_argv('foo') == 'foo'

def test_show_argv_2simple():
    assert show_argv('foo', 'bar') == 'foo bar'

def test_show_argv_space():
    assert show_argv('foo bar') == "'foo bar'"

def test_show_argv_backslash():
    assert show_argv('foo\\bar') == r"'foo\\bar'"

def test_show_argv_apostrophe():
    assert show_argv("foo'bar") == r"'foo\'bar'"

def test_show_argv_asterisk():
    assert show_argv("foo*bar") == r"'foo*bar'"

def test_show_argv_null():
    assert show_argv("foo\0bar") == r"$'foo\x00bar'"

def test_show_argv_argv0_equals():
    assert show_argv("foo=bar") == r"'foo=bar'"

def test_show_argv_argv1_equals():
    assert show_argv("foo", 'bar=baz') == r"foo bar=baz"

if sys.version_info[0] >= 3:
    def test_show_argv_surrogateesc():
        assert show_argv('foo\udc80bar') == r"$'foo\x80bar'"

    def test_show_argv_unicode():
        ### TODO: Assumes sys.getfilesystemencoding() == 'utf-8'
        assert show_argv('fooébar') == r"$'foo\xc3\xa9bar'"

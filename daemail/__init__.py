from   __future__ import unicode_literals
import platform

__version__      = '0.3.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'daemail@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/daemail'

USER_AGENT = 'daemail {} ({} {})'.format(
    __version__, platform.python_implementation(), platform.python_version()
)

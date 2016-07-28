from   __future__ import unicode_literals
import platform

__version__ = '0.3.0'

USER_AGENT = 'daemail {} ({} {})'.format(
    __version__, platform.python_implementation(), platform.python_version()
)

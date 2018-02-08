"""In place model adaptation of properties to become Python code compatible."""
import contextlib
import keyword
import logging

from pyecore import ecore

_logger = logging.getLogger(__name__)


def fix_name_clash(value):
    while keyword.iskeyword(value):
        # appending underscores is a typical way of removing name clashes in Python:
        value += '_'
    return value


@contextlib.contextmanager
def pythonic_names():
    original_get_attribute = ecore.ENamedElement.__getattribute__

    def get_attribute(self, name):
        value = original_get_attribute(self, name)

        if name == 'name':
            value = fix_name_clash(value)

        return value

    ecore.ENamedElement.__getattribute__ = get_attribute
    yield
    ecore.ENamedElement.__getattribute__ = original_get_attribute

"""Mixins to be implemented by user.

Implemented for test code in test_templates.py. Search for "user_provided" in test code.
"""

from unittest import mock


class MyClassMixin:
    """User defined mixin class for MyClass."""

    @property
    def any(self):
        return self._any

    @any.setter
    def any(self, value):
        self._any = value

    def __init__(self, *, any=None, **kwargs):
        super().__init__()

    do_it = mock.MagicMock()


class MyOtherClassMixin:
    """User defined mixin class for MyOtherClass."""

    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, value):
        self.mock_other(value)
        self._other = value

    def __init__(self, *, other=None, **kwargs):
        super().__init__(**kwargs)
        self.mock_other = mock.MagicMock()

"""Helper for tests of user_module feature."""


class MyClassMixin:
    """Mixin class, actual implementations set in test cases via mock.patch."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

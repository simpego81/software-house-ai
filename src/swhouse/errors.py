class SwhouseError(Exception):
    """Expected user-facing runtime error."""


class InvalidStateError(SwhouseError):
    """The instance or cycle state violates a runtime invariant."""

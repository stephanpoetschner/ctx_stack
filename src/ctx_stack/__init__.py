import copy
import logging
from collections import deque
from contextlib import contextmanager

__all__ = ['ContextStack', 'update', 'dumps', 'reset', 'save_context', 'restore_context']


class ContextStack:
    """
    A class to handle the logging context.

    Usage:
    >>> import logging
    >>> import logfmter
    >>> logging.basicConfig(level=logging.INFO, format=logfmter.Logfmter())
    >>> logger = logging.getLogger("sample_logger")
    # Create a new logging context
    >>> import ctx_stack as logging_ctx
    >>> with logging_ctx.update(**{"message_id": "123"}):
    ...     logger.info("Hello world.", extra=logging_ctx.dumps(**{"user": "John Doe"}))
    at=INFO msg="Hello world." message_id=123 user="John Doe"
    """

    def __init__(self):
        self._attributes = deque([{}])

    def __str__(self):
        return str(self._attributes)

    def push(self, **new_context_vars):
        old_context = self._attributes[-1]
        new_context = old_context | copy.deepcopy(new_context_vars)
        self._attributes.append(new_context)

    def pop(self):
        import logging  # Ensuring we use the standard logging module
        if len(self._attributes) <= 1:
            logging.getLogger(__name__).warning("Attempt to pop the base context prevented; retaining base context.")
            return self._attributes[0]  # Return base context without modifying
        return self._attributes.pop()

    def dumps(self, **kwargs):
        return {} | self._attributes[-1] | kwargs

    def reset(self):
        """Reset the context stack to its initial state with just the base context."""
        self._attributes.clear()
        self._attributes.append({})

    def save(self):
        """Save the current context stack for later restoration."""
        return copy.deepcopy(list(self._attributes))

    def restore(self, saved_context):
        """Restore a previously saved context stack."""
        if not saved_context:
            self.reset()
            return
        self._attributes = deque(copy.deepcopy(saved_context))
        # Ensure there's at least the base context
        if not self._attributes:
            self._attributes.append({})


_context_stack = ContextStack()


def _replace_reserved_extra_kwargs(kwargs):
    # Replace reserved keys from logging.message extra keys
    for key in (
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "message", "module",
            "msecs", "msg", "name", "pathname", "process", "processName",
            "relativeCreated", "stack_info", "thread", "threadName",
    ):
        if key in kwargs:
            kwargs[f"ctx_{key}"] = kwargs.pop(key)
    return kwargs


@contextmanager
def update(**kwargs):
    """
    Update the logging context with the given key-value pairs.

    Usage:
    >>> with ctx_stack.update(**{"message_id": "123"}):
    ...     print(ctx_stack.dumps())
    {'message_id': '123'}
    """
    kwargs = _replace_reserved_extra_kwargs(kwargs)
    _context_stack.push(**kwargs)
    try:
        yield _context_stack.dumps()
    finally:
        _context_stack.pop()


def dumps(**kwargs):
    """
    Return the current logging context as a dictionary.

    Usage:
    >>> with ctx_stack.update(**{"message_id": "123"}):
    ...     print(ctx_stack.dumps(**{"user": "John Doe"}))
    {'message_id': '123', 'user': 'John Doe'}
    """
    kwargs = _replace_reserved_extra_kwargs(kwargs)
    return _context_stack.dumps(**kwargs)


def reset():
    """Reset the context stack to its initial state."""
    _context_stack.reset()


def save_context():
    """Save the current context stack for later restoration."""
    return _context_stack.save()


def restore_context(saved_context):
    """Restore a previously saved context stack."""
    _context_stack.restore(saved_context)

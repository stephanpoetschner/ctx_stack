# ctx_stack

A lightweight, structured logging context manager for Python applications. This library makes it easy to add consistent context to your log messages throughout the execution flow of your application.

## Overview

`ctx_stack` is designed to augment Python's standard logging with structured context data. It allows you to:

- Maintain a context stack that persists through function calls
- Add request IDs, user information, and other metadata to all your logs
- Seamlessly integrate with structured logging formatters like `logfmter`
- Temporarily add or override context within specific code blocks
- Deeply nested context management with proper cleanup
- Save and restore context states across different execution environments

## Installation

```bash
pip install ctx_stack
```

## Basic Usage

```python
import logging
import logfmter
from ctx_stack import update, dumps

# Configure your logger
logging.basicConfig(level=logging.INFO, format=logfmter.Logfmter())
logger = logging.getLogger("app")

# Add context to a specific scope
with update(request_id="12345", operation="data_export"):
    # All log messages in this block (and any functions called from here)
    # will include the request_id and operation
    logger.info("Starting operation", extra=dumps())
    
    # You can add additional context for specific log messages 
    logger.info("Processing user data", extra=dumps(user_id="user123"))
    
    # Nested contexts merge with the parent context
    with update(step="validation"):
        # This log will have request_id, operation, and step
        logger.info("Validating input data", extra=dumps())
```

## API Reference

### `update(**kwargs)`

Context manager that temporarily adds context variables to the stack.

```python
with update(request_id="12345"):
    # context available here
    # automatically removed when exiting the block
```

### `dumps(**kwargs)`

Returns the current context as a dictionary, optionally merged with additional values.

```python
# Get current context plus some additional fields
logger.info("Processing item", extra=dumps(item_id="item456"))
```

### `reset()`

Resets the context stack to its initial state with only the base context.

```python
# Clear all context and revert to base state
reset()
```

### `save_context()`

Creates a deep copy of the current context stack and returns it for later restoration.

```python
# Save the current state
saved_state = save_context()
```

### `restore_context(saved_context)`

Restores a previously saved context stack.

```python
# Restore a previously saved state
restore_context(saved_state)
```

### `ContextStack`

The underlying class that manages the context stack. Most users won't need to interact with this directly.

## Integration with Logging

### Using with logfmter

```python
import logging
import logfmter
from ctx_stack import update, dumps

# Configure logging with logfmter
handler = logging.StreamHandler()
handler.setFormatter(logfmter.Logfmter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("app")

# Add context
with update(service="auth-api", environment="production"):
    # Log with context
    logger.info("User authenticated", extra=dumps(user="john_doe"))
    # Outputs: service=auth-api environment=production msg="User authenticated" user=john_doe
```

### In Django Applications

You can easily add context in a Django middleware:

```python
import uuid
from ctx_stack import update

class RequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Add context for the entire request lifecycle
        with update(request_id=request_id, 
                   path=request.path,
                   method=request.method):
            # Process the request
            response = self.get_response(request)
            return response
```

### With Celery Tasks

The library provides tools to isolate and manage context across Celery tasks:

```python
from celery import signals
import ctx_stack as logging_ctx

# Context storage for Celery tasks
_saved_contexts = {}

@signals.task_prerun.connect
def adds_logging_context(task_id, task, *args, **kwargs):
    """Add celery_information to logging context"""
    # Save the current context
    _saved_contexts[task_id] = logging_ctx.save_context()
    
    # Reset the context stack for this task
    logging_ctx.reset()

    # Add task-specific context
    ctx = {
        "celery_task_id": task_id,
        "celery_task_name": task.__name__,
    }
    
    with logging_ctx.update(**ctx):
        logger.info("Starting celery task.")

@signals.task_postrun.connect
def cleanup_logging_context(task_id, *args, **kwargs):
    """Restore the previous context when the task completes"""
    if task_id in _saved_contexts:
        logging_ctx.restore_context(_saved_contexts.pop(task_id))
```

## Features

- **Safe Context Management**: Always preserves the base context
- **Deep Copy**: Prevents side effects when using nested contexts
- **Reserved Key Protection**: Automatically prefixes keys that would collide with standard logging fields
- **Exception Safe**: Properly cleans up context even when exceptions occur
- **No Dependencies**: Pure Python implementation with no external dependencies
- **Context State Management**: Save and restore context across execution boundaries

## Implementation Details

- Uses Python's `collections.deque` to maintain the context stack
- The stack always contains at least one element (the base context)
- The `update()` context manager ensures proper cleanup with `try/finally`
- Reserved logging keys are automatically prefixed with `ctx_` to prevent collisions
- Context state can be saved and restored for cross-boundary operations (like Celery tasks)

## Thread Safety

The current implementation uses a global context stack that is shared across threads. In multi-threaded applications, consider using thread-local storage or adapting the implementation for your specific needs.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

[![Python Package](https://github.com/yourusername/ctx_stack/actions/workflows/python-package.yml/badge.svg)](https://github.com/yourusername/ctx_stack/actions/workflows/python-package.yml)
[![PyPI version](https://badge.fury.io/py/ctx-stack.svg)](https://badge.fury.io/py/ctx-stack)
[![Python Versions](https://img.shields.io/pypi/pyversions/ctx-stack.svg)](https://pypi.org/project/ctx-stack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

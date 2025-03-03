# ctx_stack

A lightweight, structured logging context manager for Python applications. This library makes it easy to add consistent context to your log messages throughout the execution flow of your application.

## Overview

`ctx_stack` is designed to augment Python's standard logging with structured context data. It allows you to:

- Maintain a context stack that persists through function calls
- Add request IDs, user information, and other metadata to all your logs
- Seamlessly integrate with structured logging formatters like `logfmter`
- Temporarily add or override context within specific code blocks
- Deeply nested context management with proper cleanup

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

### `ContextStack`

The underlying class that manages the context stack. Most users won't need to interact with this directly.

## Integration with Logging

### Using with logfmter

```python
import logging
import logfmter
from ctx_stack import update, dumps

# Configure logging with logfmter
logging.basicConfig(
    level=logging.INFO,
    format=logfmter.Logfmter()
)
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

## Features

- **Safe Context Management**: Always preserves the base context
- **Deep Copy**: Prevents side effects when using nested contexts
- **Reserved Key Protection**: Automatically prefixes keys that would collide with standard logging fields
- **Exception Safe**: Properly cleans up context even when exceptions occur
- **No Dependencies**: Pure Python implementation with no external dependencies

## Implementation Details

- Uses Python's `collections.deque` to maintain the context stack
- The stack always contains at least one element (the base context)
- The `update()` context manager ensures proper cleanup with `try/finally`
- Reserved logging keys are automatically prefixed with `ctx_` to prevent collisions

## Thread Safety

The current implementation uses a global context stack that is shared across threads. In multi-threaded applications, consider using thread-local storage or adapting the implementation for your specific needs.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

import logging
import pytest

import ctx_stack


@pytest.fixture(autouse=True)
def reset_context_stack():
    """
    Fixture to reset the context stack before each test.
    Use the new reset() method to clean up between tests.
    """
    ctx_stack.reset()
    yield


def test_push_pop_normal():
    # Test simple push/pop
    ctx_stack._context_stack.push(user="Alice")
    assert ctx_stack._context_stack.dumps() == {"user": "Alice"}
    ctx_stack._context_stack.pop()
    assert ctx_stack._context_stack.dumps() == {}


def test_nested_update_context_manager():
    # Test nested contexts with update()
    with ctx_stack.update(request_id="req-123") as ctx:
        assert ctx == {"request_id": "req-123"}
        with ctx_stack.update(user="Alice") as nested_ctx:
            expected = {"request_id": "req-123", "user": "Alice"}
            assert nested_ctx == expected
        # After exiting the nested block, context returns to outer block
        assert ctx_stack._context_stack.dumps() == {"request_id": "req-123"}
    # After outer context is closed, context should be base
    assert ctx_stack._context_stack.dumps() == {}


def test_dumps_merging():
    ctx_stack._context_stack.push(session="abc")
    result = ctx_stack.dumps(token="xyz")
    expected = {"session": "abc", "token": "xyz"}
    assert result == expected
    ctx_stack._context_stack.pop()


def test_reserved_key_remapping():
    # Test that reserved keys are remapped
    reserved_key = "args"
    value = 123
    modified = ctx_stack._replace_reserved_extra_kwargs({reserved_key: value})
    assert f"ctx_{reserved_key}" in modified
    assert reserved_key not in modified


def test_pop_base_context_logs_warning(caplog):
    # Ensure that popping the base context logs a warning and returns the base context.
    # Make sure the stack has only base context.
    # caplog records logging events.
    caplog.set_level(logging.WARNING)
    base_context = ctx_stack._context_stack.dumps()
    returned_context = ctx_stack._context_stack.pop()
    # Check if a warning was logged
    assert any("Attempt to pop the base context prevented" in record.message for record in caplog.records)
    # Ensure the returned context is identical to the base context
    assert returned_context == base_context


def test_update_with_exception():
    # Test that even if an exception occurs, the context is correctly popped.
    try:
        with ctx_stack.update(task="running"):
            raise ValueError("Simulated error")
    except ValueError:
        pass
    # After exception, the context should be back to base (empty)
    assert ctx_stack._context_stack.dumps() == {}


def test_reset():
    # Test that reset() properly clears the stack and leaves only the base context
    ctx_stack._context_stack.push(user="Alice")
    ctx_stack._context_stack.push(token="123")
    assert ctx_stack._context_stack.dumps() == {"user": "Alice", "token": "123"}

    ctx_stack.reset()

    # After reset, should have only base context
    assert ctx_stack._context_stack.dumps() == {}
    # Internal stack should have length 1 (just the base context)
    assert len(ctx_stack._context_stack._attributes) == 1


def test_save_and_restore_context():
    # Test saving and restoring context
    ctx_stack._context_stack.push(user="Alice")
    ctx_stack._context_stack.push(session="abc")
    assert ctx_stack._context_stack.dumps() == {"user": "Alice", "session": "abc"}

    # Save the current state
    saved_context = ctx_stack.save_context()

    # Modify the context
    ctx_stack.reset()
    ctx_stack._context_stack.push(task="running")
    assert ctx_stack._context_stack.dumps() == {"task": "running"}

    # Restore the saved context
    ctx_stack.restore_context(saved_context)

    # Verify it's back to the previous state
    assert ctx_stack._context_stack.dumps() == {"user": "Alice", "session": "abc"}


def test_restore_empty_context():
    # Test restoring with None or empty list
    ctx_stack._context_stack.push(user="Alice")
    assert ctx_stack._context_stack.dumps() == {"user": "Alice"}

    # Restore with None
    ctx_stack.restore_context(None)
    assert ctx_stack._context_stack.dumps() == {}

    # Restore with empty list
    ctx_stack._context_stack.push(user="Bob")
    ctx_stack.restore_context([])
    assert ctx_stack._context_stack.dumps() == {}


def test_celery_task_simulation():
    # Simulate a Celery task scenario

    # Setup initial context that might exist in a web request
    with ctx_stack.update(request_id="req-123", user="Alice"):
        assert ctx_stack.dumps() == {"request_id": "req-123", "user": "Alice"}

        # When a Celery task starts, save the current context
        task_id = "task-456"
        saved_context = ctx_stack.save_context()

        # Reset for the new task
        ctx_stack.reset()

        # Add Celery task context
        with ctx_stack.update(celery_task_id=task_id, celery_task_name="process_data"):
            # Task does its work with clean context
            assert ctx_stack.dumps() == {
                "celery_task_id": task_id,
                "celery_task_name": "process_data"
            }

            # Task finishes
            pass

        # After task finishes, restore original context
        ctx_stack.restore_context(saved_context)

        # Original context should be intact
        assert ctx_stack.dumps() == {"request_id": "req-123", "user": "Alice"}

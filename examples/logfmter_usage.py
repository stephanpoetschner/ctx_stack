import logging
import logfmter
from ctx_stack import update, dumps

handler = logging.StreamHandler()
handler.setFormatter(logfmter.Logfmter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

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

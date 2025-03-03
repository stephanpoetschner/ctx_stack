import logging
import sys
from ctx_stack import update, dumps

# Configure a simple logger
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(message)s %(levelname)s [%(name)s] - %(asctime)s'))
logger = logging.getLogger("example")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# Example showing nested context usage
def process_item(item_id):
    with update(item_id=item_id):
        logger.info("Processing item", extra=dumps())
        if item_id == "special":
            with update(priority="high"):
                logger.info("Special handling required", extra=dumps())
        return True


# Main execution
with update(request_id="12345", component="processor"):
    logger.info("Starting batch processing", extra=dumps())

    for item in ["item1", "special", "item3"]:
        process_item(item)

    logger.info("Batch processing complete", extra=dumps())

import os

# `src.handler` reads SQS_QUEUE_URL at import time (module-level), so it must be
# set before pytest imports any test module that imports the handler -- hence a
# module-level assignment here rather than inside a fixture.
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-1")
os.environ.setdefault(
    "SQS_QUEUE_URL", "https://sqs.eu-west-1.amazonaws.com/123456789012/test-queue"
)

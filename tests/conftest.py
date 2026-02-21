"""Global test configuration and fixtures."""

from pydantic_ai import models

# Disable model requests globally for all tests
models.ALLOW_MODEL_REQUESTS = False

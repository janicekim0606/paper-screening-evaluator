class EvaluatorError(Exception):
    """Base exception for expected evaluator failures."""


class ConfigurationError(EvaluatorError):
    """Raised when required configuration is missing or invalid."""


class ExternalServiceError(EvaluatorError):
    """Raised when an external API cannot provide a trustworthy result."""


class InvalidResponseError(EvaluatorError):
    """Raised when an API response is empty or malformed."""


class InputValidationError(EvaluatorError):
    """Raised when user-provided input does not match the expected schema."""

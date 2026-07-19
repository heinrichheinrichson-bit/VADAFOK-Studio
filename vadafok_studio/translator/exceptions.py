class TranslatorError(Exception):
    """Base exception for translator providers."""


class TranslatorConfigurationError(TranslatorError):
    """The provider configuration is missing or invalid."""


class TranslatorAuthenticationError(TranslatorError):
    """The provider rejected the supplied credentials."""


class TranslatorTimeoutError(TranslatorError):
    """The provider did not answer within the configured timeout."""


class TranslatorRateLimitError(TranslatorError):
    """The provider temporarily rejected the request due to rate limiting."""


class TranslatorQuotaError(TranslatorError):
    """The provider quota has been exhausted."""


class TranslatorProviderError(TranslatorError):
    """The provider returned an invalid or unexpected response."""

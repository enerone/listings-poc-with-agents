from typing import Any, Dict, Optional


class ListingsError(Exception):
    """Base exception for all listings-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ListingsError):
    """Raised when input validation fails."""
    pass


class FileValidationError(ValidationError):
    """Raised when file validation fails."""
    pass


class AIGenerationError(ListingsError):
    """Raised when AI generation fails."""
    pass


class CompetitorResearchError(ListingsError):
    """Raised when competitor research fails."""
    pass


class ImageProcessingError(ListingsError):
    """Raised when image processing fails."""
    pass


class DatabaseError(ListingsError):
    """Raised when database operations fail."""
    pass


class ExternalAPIError(ListingsError):
    """Raised when external API calls fail."""
    pass


class ConfigurationError(ListingsError):
    """Raised when configuration is invalid."""
    pass


class AuthenticationError(ListingsError):
    """Raised when authentication fails."""
    pass


class RateLimitError(ListingsError):
    """Raised when rate limits are exceeded."""
    pass
import logging
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger instance for this class."""
        return get_logger(self.__class__.__name__)
    
    def log_operation_start(self, operation: str, **kwargs: Any) -> None:
        """Log the start of an operation."""
        self.logger.info(f"Starting {operation}", operation=operation, **kwargs)
    
    def log_operation_success(self, operation: str, **kwargs: Any) -> None:
        """Log successful completion of an operation."""
        self.logger.info(f"Completed {operation}", operation=operation, **kwargs)
    
    def log_operation_error(self, operation: str, error: Exception, **kwargs: Any) -> None:
        """Log an error during an operation."""
        self.logger.error(
            f"Failed {operation}",
            operation=operation,
            error=str(error),
            error_type=type(error).__name__,
            **kwargs
        )
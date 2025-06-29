import time
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import ListingsError
from app.core.logger import get_logger

logger = get_logger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling and logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log successful requests
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time=round(process_time, 4)
            )
            
            return response
            
        except ListingsError as e:
            # Handle our custom exceptions
            process_time = time.time() - start_time
            logger.error(
                "Custom error occurred",
                method=request.method,
                path=request.url.path,
                error_type=type(e).__name__,
                error_message=str(e),
                error_code=getattr(e, 'error_code', None),
                process_time=round(process_time, 4)
            )
            
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e),
                        "code": getattr(e, 'error_code', None),
                        "details": getattr(e, 'details', {})
                    }
                }
            )
            
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            process_time = time.time() - start_time
            logger.warning(
                "HTTP exception occurred",
                method=request.method,
                path=request.url.path,
                status_code=e.status_code,
                detail=e.detail,
                process_time=round(process_time, 4)
            )
            
            return JSONResponse(
                status_code=e.status_code,
                content={"error": {"message": e.detail, "type": "HTTPException"}}
            )
            
        except Exception as e:
            # Handle unexpected errors
            process_time = time.time() - start_time
            logger.error(
                "Unexpected error occurred",
                method=request.method,
                path=request.url.path,
                error_type=type(e).__name__,
                error_message=str(e),
                process_time=round(process_time, 4),
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": "Internal server error",
                        "type": "InternalServerError"
                    }
                }
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log incoming request
        logger.info(
            "Incoming request",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        response = await call_next(request)
        return response
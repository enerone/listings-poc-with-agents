import io
import magic
from typing import BinaryIO
from PIL import Image
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.core.exceptions import FileValidationError
from app.core.logger import get_logger

logger = get_logger(__name__)


class FileValidator:
    """Secure file validation utilities."""
    
    @staticmethod
    async def validate_image_file(file: UploadFile) -> bytes:
        """
        Perform comprehensive validation of uploaded image files.
        
        Args:
            file: The uploaded file to validate
            
        Returns:
            bytes: The validated file content
            
        Raises:
            FileValidationError: If validation fails
        """
        try:
            # Read file content
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Check file size
            if len(file_content) > settings.max_file_size:
                raise FileValidationError(
                    f"File size {len(file_content)} exceeds maximum allowed size {settings.max_file_size}",
                    error_code="FILE_TOO_LARGE"
                )
            
            # Validate file extension
            if not file.filename:
                raise FileValidationError("Filename is required", error_code="NO_FILENAME")
            
            file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            if file_extension not in settings.allowed_extensions:
                raise FileValidationError(
                    f"File extension '{file_extension}' not allowed. Allowed: {settings.allowed_extensions}",
                    error_code="INVALID_EXTENSION"
                )
            
            # Validate MIME type using python-magic
            file_mime_type = magic.from_buffer(file_content, mime=True)
            if file_mime_type not in settings.allowed_mime_types:
                raise FileValidationError(
                    f"MIME type '{file_mime_type}' not allowed. Allowed: {settings.allowed_mime_types}",
                    error_code="INVALID_MIME_TYPE"
                )
            
            # Validate that file is actually an image using PIL
            try:
                with Image.open(io.BytesIO(file_content)) as img:
                    # Verify the image
                    img.verify()
                    
                    # Reset and get image info
                    img_copy = Image.open(io.BytesIO(file_content))
                    width, height = img_copy.size
                    
                    # Basic dimension validation
                    if width < 100 or height < 100:
                        raise FileValidationError(
                            f"Image dimensions {width}x{height} too small. Minimum 100x100",
                            error_code="IMAGE_TOO_SMALL"
                        )
                    
                    if width > 4096 or height > 4096:
                        raise FileValidationError(
                            f"Image dimensions {width}x{height} too large. Maximum 4096x4096",
                            error_code="IMAGE_TOO_LARGE"
                        )
                    
                    logger.info(
                        "File validation successful",
                        filename=file.filename,
                        size=len(file_content),
                        mime_type=file_mime_type,
                        dimensions=f"{width}x{height}"
                    )
                    
            except Exception as e:
                raise FileValidationError(
                    f"Invalid image file: {str(e)}",
                    error_code="INVALID_IMAGE"
                )
            
            return file_content
            
        except FileValidationError:
            raise
        except Exception as e:
            logger.error("Unexpected error during file validation", error=str(e), filename=file.filename)
            raise FileValidationError(
                f"File validation failed: {str(e)}",
                error_code="VALIDATION_ERROR"
            )
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks.
        
        Args:
            filename: The original filename
            
        Returns:
            str: The sanitized filename
        """
        import os
        import re
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading dots and spaces
        filename = filename.lstrip('. ')
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed_file"
        
        # Limit filename length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:251-len(ext)] + ext
        
        return filename


class SecurityUtils:
    """General security utilities."""
    
    @staticmethod
    def validate_input_length(text: str, max_length: int = 10000) -> None:
        """Validate input text length to prevent DoS attacks."""
        if len(text) > max_length:
            raise FileValidationError(
                f"Input text length {len(text)} exceeds maximum {max_length}",
                error_code="INPUT_TOO_LONG"
            )
    
    @staticmethod
    def sanitize_html_input(text: str) -> str:
        """Basic HTML sanitization for user inputs."""
        import html
        return html.escape(text.strip())
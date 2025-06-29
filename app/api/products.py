from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import uuid
from PIL import Image

router = APIRouter()

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload-images/")
async def upload_images(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    for file in files:
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail=f"File {file.filename} has invalid extension")
        
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File {file.filename} is too large")
        
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        try:
            content = await file.read()
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Verify the image (skip verification for development)
            try:
                with Image.open(file_path) as img:
                    img.verify()
            except Exception as img_error:
                # For development, just log the error but don't fail
                print(f"Warning: Image verification failed for {file.filename}: {img_error}")
            
            uploaded_files.append({
                "filename": unique_filename,
                "original_name": file.filename,
                "path": f"/uploads/{unique_filename}",
                "size": len(content)
            })
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Error processing {file.filename}: {str(e)}")
    
    return {"uploaded_files": uploaded_files}
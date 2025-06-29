from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import get_db
from app.models.listing import Listing as ListingModel
from app.schemas.listing import Listing, ListingCreate, ListingUpdate, AgentRequest, AgentResponse
from app.agents.analyzer import AnalyzerAgent
from app.agents.image_finder import ImageFinder
from app.agents.optimizer import OptimizerAgent
from app.core.logger import get_logger
from app.core.exceptions import ValidationError, AIGenerationError, DatabaseError
from app.core.security import SecurityUtils

logger = get_logger(__name__)
router = APIRouter()

@router.post("/", response_model=Listing)
def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    logger.info("Creating new listing", title=listing.original_title[:50])
    
    try:
        # Validate and sanitize inputs
        SecurityUtils.validate_input_length(listing.original_title, 1000)
        SecurityUtils.validate_input_length(listing.original_description, 10000)
        
        sanitized_data = listing.model_dump()
        sanitized_data["original_title"] = SecurityUtils.sanitize_html_input(sanitized_data["original_title"])
        sanitized_data["original_description"] = SecurityUtils.sanitize_html_input(sanitized_data["original_description"])
        
        db_listing = ListingModel(**sanitized_data)
        db.add(db_listing)
        db.commit()
        db.refresh(db_listing)
        
        logger.info("Listing created successfully", listing_id=db_listing.id)
        return db_listing
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to create listing", error=str(e), title=listing.original_title[:50])
        raise DatabaseError(f"Failed to create listing: {str(e)}")

@router.get("/", response_model=List[Listing])
def read_listings(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get listings with pagination and optional filtering."""
    logger.info("Fetching listings", skip=skip, limit=limit, status=status)
    
    # Validate pagination parameters
    if skip < 0:
        raise HTTPException(status_code=400, detail="Skip cannot be negative")
    if limit <= 0 or limit > 1000:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
    
    query = db.query(ListingModel)
    
    # Apply status filter if provided
    if status:
        query = query.filter(ListingModel.status == status)
    
    # Add ordering for consistent pagination
    query = query.order_by(ListingModel.created_at.desc())
    
    # Apply pagination
    listings = query.offset(skip).limit(limit).all()
    
    logger.info("Listings fetched successfully", count=len(listings))
    return listings

@router.get("/{listing_id}", response_model=Listing)
def read_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(ListingModel).filter(ListingModel.id == listing_id).first()
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@router.put("/{listing_id}", response_model=Listing)
def update_listing(listing_id: int, listing: ListingUpdate, db: Session = Depends(get_db)):
    db_listing = db.query(ListingModel).filter(ListingModel.id == listing_id).first()
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    update_data = listing.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_listing, field, value)
    
    db.commit()
    db.refresh(db_listing)
    return db_listing

@router.delete("/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(ListingModel).filter(ListingModel.id == listing_id).first()
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    db.delete(listing)
    db.commit()
    return {"message": "Listing deleted successfully"}

@router.post("/{listing_id}/analyze", response_model=AgentResponse)
async def analyze_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(ListingModel).filter(ListingModel.id == listing_id).first()
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    analyzer = AnalyzerAgent()
    result = await analyzer.analyze(listing.original_title, listing.original_description)
    
    if result["success"]:
        listing.generated_title = result["data"]["title"]
        listing.generated_description = result["data"]["description"]
        listing.generated_bullets = result["data"]["bullets"]
        listing.keywords = result["data"]["keywords"]
        listing.status = "analyzed"
        db.commit()
    
    return AgentResponse(**result)

@router.post("/{listing_id}/find-images", response_model=AgentResponse)
async def find_images(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(ListingModel).filter(ListingModel.id == listing_id).first()
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    image_finder = ImageFinder()
    
    # Check if listing has uploaded images to use as reference
    reference_image = None
    if listing.images and len(listing.images) > 0:
        # Use the first uploaded image as reference
        reference_image = listing.images[0]
        print(f"🖼️ Using reference image: {reference_image}")
    
    result = await image_finder.find_similar_images(
        listing.original_title,
        listing.original_description,
        listing.images or [],
        reference_image
    )
    
    if result["success"] and result["data"]:
        # Store found images in additional_images field
        data = result["data"]
        if "all_images" in data:
            # New format with detailed image info
            all_images = data.get("all_images", [])
            image_urls = [img["url"] for img in all_images if isinstance(img, dict)]
        else:
            # Legacy format with simple URLs
            image_urls = data.get("images", [])
        
        listing.additional_images = image_urls
        db.commit()
    
    return AgentResponse(**result)

@router.post("/{listing_id}/optimize", response_model=AgentResponse)
async def optimize_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(ListingModel).filter(ListingModel.id == listing_id).first()
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    optimizer = OptimizerAgent()
    result = await optimizer.optimize(
        listing.generated_title or listing.original_title,
        listing.generated_description or listing.original_description,
        listing.generated_bullets or [],
        listing.keywords or []
    )
    
    if result["success"]:
        listing.optimized_title = result["data"]["title"]
        listing.optimized_description = result["data"]["description"]
        listing.optimized_bullets = result["data"]["bullets"]
        listing.status = "optimized"
        db.commit()
    
    return AgentResponse(**result)
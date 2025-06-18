from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.api.deps import get_current_user, get_optional_current_user
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorService
from app.schemas.vendor import (
    VendorCreate, VendorUpdate, VendorResponse,
    VendorServiceCreate, VendorServiceUpdate, VendorServiceResponse
)
from app.core.exceptions import ForbiddenException

router = APIRouter()


@router.post("/", response_model=VendorResponse)
def create_vendor_profile(
    vendor_data: VendorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create vendor profile"""
    # Check if user already has a vendor profile
    existing_vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if existing_vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a vendor profile"
        )
    
    # Create vendor profile
    db_vendor = Vendor(
        **vendor_data.dict(exclude={"service_areas", "portfolio_images"}),
        user_id=current_user.id,
        service_areas=",".join(vendor_data.service_areas) if vendor_data.service_areas else None,
        portfolio_images=",".join(vendor_data.portfolio_images) if vendor_data.portfolio_images else None
    )
    
    db.add(db_vendor)
    
    # Update user role to vendor
    current_user.role = UserRole.VENDOR
    
    db.commit()
    db.refresh(db_vendor)
    
    return db_vendor


@router.get("/", response_model=List[VendorResponse])
def get_vendors(
    skip: int = 0,
    limit: int = 100,
    business_type: Optional[str] = None,
    search: Optional[str] = None,
    verified_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all vendors with optional filtering"""
    query = db.query(Vendor).filter(Vendor.is_active == True)
    
    if business_type:
        query = query.filter(Vendor.business_type == business_type)
    
    if search:
        query = query.filter(
            or_(
                Vendor.business_name.ilike(f"%{search}%"),
                Vendor.description.ilike(f"%{search}%"),
                Vendor.business_type.ilike(f"%{search}%")
            )
        )
    
    if verified_only:
        query = query.filter(Vendor.is_verified == True)
    
    vendors = query.offset(skip).limit(limit).all()
    return vendors


@router.get("/me", response_model=VendorResponse)
def get_my_vendor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's vendor profile"""
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    return vendor


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    """Get vendor by ID"""
    vendor = db.query(Vendor).filter(
        and_(Vendor.id == vendor_id, Vendor.is_active == True)
    ).first()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    return vendor


@router.put("/me", response_model=VendorResponse)
def update_my_vendor_profile(
    vendor_update: VendorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's vendor profile"""
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Update vendor
    update_data = vendor_update.dict(exclude_unset=True)
    if "service_areas" in update_data:
        update_data["service_areas"] = ",".join(update_data["service_areas"]) if update_data["service_areas"] else None
    if "portfolio_images" in update_data:
        update_data["portfolio_images"] = ",".join(update_data["portfolio_images"]) if update_data["portfolio_images"] else None
    
    for field, value in update_data.items():
        setattr(vendor, field, value)
    
    db.commit()
    db.refresh(vendor)
    
    return vendor


@router.delete("/me")
def delete_my_vendor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's vendor profile"""
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Soft delete
    vendor.is_active = False
    
    # Revert user role
    current_user.role = UserRole.USER
    
    db.commit()
    
    return {"message": "Vendor profile deleted successfully"}


# Vendor Services endpoints
@router.post("/me/services", response_model=VendorServiceResponse)
def create_vendor_service(
    service_data: VendorServiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new vendor service"""
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    db_service = VendorService(
        **service_data.dict(exclude={"includes"}),
        vendor_id=vendor.id,
        includes=",".join(service_data.includes) if service_data.includes else None
    )
    
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    
    return db_service


@router.get("/me/services", response_model=List[VendorServiceResponse])
def get_my_vendor_services(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current vendor's services"""
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    services = db.query(VendorService).filter(VendorService.vendor_id == vendor.id).all()
    return services


@router.get("/{vendor_id}/services", response_model=List[VendorServiceResponse])
def get_vendor_services(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    """Get vendor's services"""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    services = db.query(VendorService).filter(
        and_(VendorService.vendor_id == vendor_id, VendorService.is_available == True)
    ).all()
    return services


@router.put("/me/services/{service_id}", response_model=VendorServiceResponse)
def update_vendor_service(
    service_id: int,
    service_update: VendorServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update vendor service"""
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    service = db.query(VendorService).filter(
        and_(VendorService.id == service_id, VendorService.vendor_id == vendor.id)
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Update service
    update_data = service_update.dict(exclude_unset=True)
    if "includes" in update_data:
        update_data["includes"] = ",".join(update_data["includes"]) if update_data["includes"] else None
    
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    
    return service


@router.delete("/me/services/{service_id}")
def delete_vendor_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete vendor service"""
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    service = db.query(VendorService).filter(
        and_(VendorService.id == service_id, VendorService.vendor_id == vendor.id)
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    db.delete(service)
    db.commit()
    
    return {"message": "Service deleted successfully"}
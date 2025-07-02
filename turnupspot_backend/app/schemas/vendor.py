from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime


class VendorServiceBase(BaseModel):
    name: str
    description: str
    category: str
    base_price: Optional[float] = None
    price_unit: Optional[str] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    duration: Optional[str] = None
    includes: Optional[List[str]] = []
    requirements: Optional[str] = None


class VendorServiceCreate(VendorServiceBase):
    pass


class VendorServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[float] = None
    price_unit: Optional[str] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    duration: Optional[str] = None
    includes: Optional[List[str]] = None
    requirements: Optional[str] = None
    is_available: Optional[bool] = None


class VendorServiceResponse(VendorServiceBase):
    id: int
    vendor_id: int
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VendorBase(BaseModel):
    business_name: str
    business_type: str
    description: str
    business_phone: Optional[str] = None
    business_email: Optional[EmailStr] = None
    website_url: Optional[str] = None
    business_address: Optional[str] = None
    service_areas: Optional[List[str]] = []
    years_in_business: Optional[int] = None
    license_number: Optional[str] = None


class VendorCreate(VendorBase):
    logo_url: Optional[str] = None
    portfolio_images: Optional[List[str]] = []


class VendorUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    description: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[EmailStr] = None
    website_url: Optional[str] = None
    business_address: Optional[str] = None
    service_areas: Optional[List[str]] = None
    years_in_business: Optional[int] = None
    license_number: Optional[str] = None
    logo_url: Optional[str] = None
    portfolio_images: Optional[List[str]] = None


class VendorResponse(VendorBase):
    id: int
    user_id: int
    logo_url: Optional[str] = None
    portfolio_images: Optional[List[str]] = []
    average_rating: float
    total_reviews: int
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    services: Optional[List[VendorServiceResponse]] = []

    class Config:
        from_attributes = True
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String, nullable=False, index=True)
    business_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Contact info
    business_phone = Column(String, nullable=True)
    business_email = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    
    # Location
    business_address = Column(String, nullable=True)
    service_areas = Column(Text, nullable=True)  # JSON string of areas
    
    # Business details
    years_in_business = Column(Integer, nullable=True)
    license_number = Column(String, nullable=True)
    insurance_verified = Column(Boolean, default=False)
    
    # Media
    logo_url = Column(String, nullable=True)
    portfolio_images = Column(Text, nullable=True)  # JSON string of image URLs
    
    # Ratings and reviews
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="vendor_profile")
    services = relationship("VendorService", back_populates="vendor")

    def __repr__(self):
        return f"<Vendor(id={self.id}, business_name='{self.business_name}', type='{self.business_type}')>"


class VendorService(Base):
    __tablename__ = "vendor_services"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    
    # Pricing
    base_price = Column(Float, nullable=True)
    price_unit = Column(String, nullable=True)  # per hour, per event, etc.
    price_range_min = Column(Float, nullable=True)
    price_range_max = Column(Float, nullable=True)
    
    # Service details
    duration = Column(String, nullable=True)
    includes = Column(Text, nullable=True)  # JSON string of what's included
    requirements = Column(Text, nullable=True)
    
    # Availability
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    vendor = relationship("Vendor", back_populates="services")

    def __repr__(self):
        return f"<VendorService(id={self.id}, name='{self.name}', vendor_id={self.vendor_id})>"
# src/data/models.py (continued)

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class Hotel(Base):
    """Hotel information"""
    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    country = Column(String(100))
    stars = Column(Integer)
    total_rooms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    rooms = relationship("Room", back_populates="hotel")
    competitors = relationship("Competitor", back_populates="hotel")
    prices = relationship("RoomPrice", back_populates="hotel")
    bookings = relationship("Booking", back_populates="hotel")
    occupancy = relationship("Occupancy", back_populates="hotel")
    revenue = relationship("Revenue", back_populates="hotel")

class Room(Base):
    """Room type information"""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_type = Column(String(50), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    min_price = Column(Numeric(10, 2), nullable=False)
    max_price = Column(Numeric(10, 2), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    amenities = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    hotel = relationship("Hotel", back_populates="rooms")
    prices = relationship("RoomPrice", back_populates="room")
    bookings = relationship("Booking", back_populates="room")

class Competitor(Base):
    """Competitor hotel information"""
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    name = Column(String(200), nullable=False)
    source = Column(String(50))  # booking.com, expedia, etc.
    source_id = Column(String(100))  # External ID from the source
    base_price = Column(Numeric(10, 2))
    distance_km = Column(Float)
    stars = Column(Integer)
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    hotel = relationship("Hotel", back_populates="competitors")
    prices = relationship("CompetitorPrice", back_populates="competitor")

class RoomPrice(Base):
    """Room price information"""
    __tablename__ = "room_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_type = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    is_auto_pricing = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    hotel = relationship("Hotel", back_populates="prices")
    room = relationship("Room", back_populates="prices", 
                       primaryjoin="and_(Room.hotel_id==RoomPrice.hotel_id, Room.room_type==RoomPrice.room_type)",
                       viewonly=True)

class CompetitorPrice(Base):
    """Competitor price information"""
    __tablename__ = "competitor_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=False)
    date = Column(Date, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    room_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    competitor = relationship("Competitor", back_populates="prices")

class Booking(Base):
    """Booking information"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_type = Column(String(50), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    room_rate = Column(Numeric(10, 2), nullable=False)
    guest_name = Column(String(200))
    guest_email = Column(String(200))
    status = Column(String(20), default="confirmed")  # confirmed, cancelled, no-show, checked-out
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    hotel = relationship("Hotel", back_populates="bookings")
    room = relationship("Room", back_populates="bookings",
                       primaryjoin="and_(Room.hotel_id==Booking.hotel_id, Room.room_type==Booking.room_type)",
                       viewonly=True)

class Occupancy(Base):
    """Daily occupancy information"""
    __tablename__ = "occupancy"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    date = Column(Date, nullable=False)
    total_rooms = Column(Integer, nullable=False)
    occupied_rooms = Column(Integer, nullable=False)
    occupancy_rate = Column(Float, nullable=False)
    adr = Column(Numeric(10, 2))  # Average Daily Rate
    revpar = Column(Numeric(10, 2))  # Revenue Per Available Room
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    hotel = relationship("Hotel", back_populates="occupancy")

class Revenue(Base):
    """Daily revenue information"""
    __tablename__ = "revenue"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    date = Column(Date, nullable=False)
    room_revenue = Column(Numeric(12, 2), default=0)
    food_beverage_revenue = Column(Numeric(12, 2), default=0)
    other_revenue = Column(Numeric(12, 2), default=0)
    total_revenue = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    hotel = relationship("Hotel", back_populates="revenue")
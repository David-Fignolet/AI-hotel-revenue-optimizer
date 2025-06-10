# src/data/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Hotel(Base):
    """Hotel information"""
    __tablename__ = 'hotels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    country = Column(String(100))
    stars = Column(Integer)
    total_rooms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rooms = relationship("Room", back_populates="hotel")
    competitors = relationship("Competitor", back_populates="hotel")
    prices = relationship("PriceHistory", back_populates="hotel")
    forecasts = relationship("DemandForecast", back_populates="hotel")

class Room(Base):
    """Room types and configurations"""
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    room_type = Column(String(50), nullable=False)
    base_price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    total_quantity = Column(Integer, nullable=False)
    amenities = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hotel = relationship("Hotel", back_populates="rooms")
    prices = relationship("PriceHistory", back_populates="room")
    forecasts = relationship("DemandForecast", back_populates="room")

class Competitor(Base):
    """Competitor hotels"""
    __tablename__ = 'competitors'
    
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    name = Column(String(200), nullable=False)
    external_id = Column(String(100))  # ID from external systems
    source = Column(String(50))  # booking.com, expedia, etc.
    base_price = Column(Float)
    last_updated = Column(DateTime)
    data = Column(JSON)  # Additional competitor data
    
    # Relationships
    hotel = relationship("Hotel", back_populates="competitors")
    prices = relationship("CompetitorPrice", back_populates="competitor")

class PriceHistory(Base):
    """Historical price data"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    occupancy = Column(Float)  # Occupancy rate
    revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hotel = relationship("Hotel", back_populates="prices")
    room = relationship("Room", back_populates="prices")

class DemandForecast(Base):
    """Demand forecasts"""
    __tablename__ = 'demand_forecasts'
    
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    forecast_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime, nullable=False)
    predicted_occupancy = Column(Float, nullable=False)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    confidence = Column(Float)
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hotel = relationship("Hotel", back_populates="forecasts")
    room = relationship("Room", back_populates="forecasts")

class CompetitorPrice(Base):
    """Competitor price data"""
    __tablename__ = 'competitor_prices'
    
    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey('competitors.id'))
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default='EUR')
    room_type = Column(String(50))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON)  # Raw data from source
    
    # Relationships
    competitor = relationship("Competitor", back_populates="prices")
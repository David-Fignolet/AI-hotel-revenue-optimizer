# src/api/endpoint.py
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date, datetime, timedelta
from typing import List, Optional
import logging

from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..data.database import get_db
from ..data import models
from ..services.competitor import CompetitorAnalyzer
from ..core.forecasting import DemandForecaster
from ..core.pricing import RevenueManager, DynamicPricingStrategy

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
competitor_analyzer = CompetitorAnalyzer()
demand_forecaster = DemandForecaster()
revenue_manager = RevenueManager()

# Request/Response Models
class PriceRecommendationRequest(BaseModel):
    hotel_id: int
    room_type: str
    check_in: date
    check_out: date
    strategy: str = "dynamic"

class PriceRecommendationResponse(BaseModel):
    hotel_id: int
    room_type: str
    recommended_price: float
    min_price: float
    max_price: float
    confidence: float
    predicted_occupancy: float
    competitor_analysis: dict

class CompetitorPriceResponse(BaseModel):
    competitor_id: int
    competitor_name: str
    price: float
    currency: str
    check_in: date
    check_out: date
    room_type: str
    timestamp: datetime

# Endpoints
@router.post("/recommendations", response_model=PriceRecommendationResponse)
async def get_price_recommendation(
    request: PriceRecommendationRequest,
    db: Session = Depends(get_db)
):
    """Get price recommendation for a specific room type and date range"""
    try:
        # Get hotel and room details
        hotel = db.query(models.Hotel).filter(models.Hotel.id == request.hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
            
        room = db.query(models.Room).filter(
            models.Room.hotel_id == request.hotel_id,
            models.Room.room_type == request.room_type
        ).first()
        
        if not room:
            raise HTTPException(status_code=404, detail="Room type not found")
        
        # Get competitor prices
        competitor_prices = await competitor_analyzer.get_competitor_prices(
            hotel_id=request.hotel_id,
            check_in=request.check_in,
            check_out=request.check_out,
            room_type=request.room_type
        )
        
        # Get demand forecast
        forecast = demand_forecaster.predict(
            hotel_id=request.hotel_id,
            check_in=request.check_in,
            check_out=request.check_out
        )
        
        # Get price recommendation
        recommendation = revenue_manager.get_price_recommendation(
            room_type=request.room_type,
            base_price=room.base_price,
            min_price=room.min_price,
            max_price=room.max_price,
            predicted_demand=forecast['predicted_occupancy'].mean(),
            competitor_prices=[p.price for p in competitor_prices]
        )
        
        # Analyze competition
        competition = competitor_analyzer.analyze_competition(
            our_price=recommendation['recommended_price'],
            competitor_prices=competitor_prices
        )
        
        return {
            "hotel_id": request.hotel_id,
            "room_type": request.room_type,
            "recommended_price": recommendation['recommended_price'],
            "min_price": room.min_price,
            "max_price": room.max_price,
            "confidence": 0.9,  # Would come from the model
            "predicted_occupancy": forecast['predicted_occupancy'].mean(),
            "competitor_analysis": competition
        }
        
    except Exception as e:
        logger.error(f"Error in get_price_recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/competitor-prices", response_model=List[CompetitorPriceResponse])
async def get_competitor_prices(
    hotel_id: int,
    check_in: date,
    check_out: date,
    room_type: str,
    db: Session = Depends(get_db)
):
    """Get competitor prices for a specific hotel and date range"""
    try:
        # Get competitor prices
        competitor_prices = await competitor_analyzer.get_competitor_prices(
            hotel_id=hotel_id,
            check_in=check_in,
            check_out=check_out,
            room_type=room_type
        )
        
        return competitor_prices
        
    except Exception as e:
        logger.error(f"Error in get_competitor_prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demand-forecast")
async def get_demand_forecast(
    hotel_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Get demand forecast for a date range"""
    try:
        forecast = demand_forecaster.predict(
            hotel_id=hotel_id,
            check_in=start_date,
            check_out=end_date
        )
        
        return forecast.to_dict(orient="records")
        
    except Exception as e:
        logger.error(f"Error in get_demand_forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
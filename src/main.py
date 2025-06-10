# src/main.py
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from src.api.endpoints import router as api_router
from .utils.config import settings
from .data.database import init_db, engine
from .data import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log")
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting application...")
    
    # Create database tables
    logger.info("Initializing database...")
    models.Base.metadata.create_all(bind=engine)
    
    # Create default data
    await create_initial_data()
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    # Create the FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered hotel revenue management system",
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create static directory if it doesn't exist
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Include API routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": "development" if settings.DEBUG else "production"
        }
    
    return app

async def create_initial_data():
    """Create initial data if database is empty"""
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime, timedelta
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we already have data
        if db.query(models.Hotel).count() == 0:
            logger.info("Creating initial data...")
            
            # Create a sample hotel
            hotel = models.Hotel(
                name="Grand Hotel Paris",
                address="123 Champs-Élysées",
                city="Paris",
                country="France",
                stars=5,
                total_rooms=150,
                amenities=["pool", "spa", "restaurant", "bar", "gym", "wifi"]
            )
            db.add(hotel)
            db.commit()
            db.refresh(hotel)
            
            # Create room types
            room_types = [
                models.Room(
                    hotel_id=hotel.id,
                    room_type="standard",
                    base_price=200.0,
                    min_price=150.0,
                    max_price=300.0,
                    total_quantity=100,
                    available_quantity=100,
                    amenities=["wifi", "tv", "ac", "minibar"]
                ),
                models.Room(
                    hotel_id=hotel.id,
                    room_type="deluxe",
                    base_price=300.0,
                    min_price=250.0,
                    max_price=450.0,
                    total_quantity=40,
                    available_quantity=40,
                    amenities=["wifi", "tv", "ac", "minibar", "balcony", "sea_view"]
                ),
                models.Room(
                    hotel_id=hotel.id,
                    room_type="suite",
                    base_price=500.0,
                    min_price=400.0,
                    max_price=800.0,
                    total_quantity=10,
                    available_quantity=10,
                    amenities=["wifi", "tv", "ac", "minibar", "balcony", "sea_view", "jacuzzi"]
                )
            ]
            db.add_all(room_types)
            db.commit()
            
            logger.info("Initial data created successfully")
            
    except Exception as e:
        logger.error(f"Error creating initial data: {str(e)}")
        db.rollback()
    finally:
        db.close()

# Run the application
if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Run the FastAPI application
    uvicorn.run(
        "src.main:create_app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1,
        factory=True
    )
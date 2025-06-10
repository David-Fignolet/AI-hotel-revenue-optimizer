import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import asyncio

# Ajouter le répertoire racine au PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Fixtures communes
@pytest.fixture
def sample_hotel_data():
    return {
        "name": "Hôtel de Test",
        "stars": 4,
        "total_rooms": 100,
        "occupancy_rate": 0.75,
        "current_price": 200.0
    }

@pytest.fixture
def sample_market_data():
    return {
        "competitor_prices": [180, 190, 200, 210, 205],
        "events": ["Conférence Test"],
        "weather": "Ensoleillé"
    }

@pytest.fixture
def sample_historical_data():
    return pd.DataFrame({
        'date': pd.date_range(end=datetime.now(), periods=30),
        'price': [200 + (i % 10) for i in range(30)],
        'occupancy': [0.7 + (i % 10 * 0.01) for i in range(30)]
    })

# Configuration pour les tests asynchrones
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

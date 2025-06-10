# src/services/competitor.py
from typing import List, Dict, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import logging
from ..utils.cache import cache_manager

logger = logging.getLogger(__name__)

@dataclass
class CompetitorPrice:
    competitor_id: str
    competitor_name: str
    price: float
    currency: str
    check_in: str
    check_out: str
    room_type: str
    timestamp: datetime = None

class CompetitorAnalyzer:
    """Analyzes competitor pricing and availability"""
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
    async def fetch_competitor_prices(self, 
                                    hotel_ids: List[str],
                                    check_in: str,
                                    check_out: str,
                                    room_type: str = "standard") -> List[CompetitorPrice]:
        """Fetch prices from multiple competitor hotels asynchronously"""
        tasks = []
        for hotel_id in hotel_ids:
            cache_key = f"competitor_{hotel_id}_{check_in}_{check_out}_{room_type}"
            cached = await cache_manager.get(cache_key)
            if cached:
                logger.info(f"Using cached data for {hotel_id}")
                tasks.append(cached)
                continue
                
            task = asyncio.create_task(
                self._scrape_competitor_price(hotel_id, check_in, check_out, room_type)
            )
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, CompetitorPrice)]
    
    async def _scrape_competitor_price(self, 
                                     hotel_id: str,
                                     check_in: str,
                                     check_out: str,
                                     room_type: str) -> Optional[CompetitorPrice]:
        """Scrape price for a single competitor"""
        url = f"https://www.booking.com/hotel/{hotel_id}.html"
        params = {
            'checkin': check_in,
            'checkout': check_out,
            'group_adults': 2,
            'no_rooms': 1,
            'selected_currency': 'EUR'
        }
        
        headers = {
            'User-Agent': self.user_agent,
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch {url}: {response.status}")
                        return None
                        
                    html = await response.text()
                    price = self._parse_booking_page(html)
                    
                    if price:
                        result = CompetitorPrice(
                            competitor_id=hotel_id,
                            competitor_name="",  # Would extract from HTML
                            price=price,
                            currency='EUR',
                            check_in=check_in,
                            check_out=check_out,
                            room_type=room_type,
                            timestamp=datetime.utcnow()
                        )
                        
                        # Cache the result
                        cache_key = f"competitor_{hotel_id}_{check_in}_{check_out}_{room_type}"
                        await cache_manager.set(cache_key, result, self.cache_ttl)
                        
                        return result
                        
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            
        return None
        
    def _parse_booking_page(self, html: str) -> Optional[float]:
        """Parse price from booking.com HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            price_element = soup.find('span', {'data-testid': 'price-and-discounted-price'})
            if price_element:
                price_text = price_element.text
                # Extract numeric price
                price = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
                return price
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
        return None
        
    def analyze_competition(self, 
                          our_price: float,
                          competitor_prices: List[CompetitorPrice]) -> Dict:
        """Analyze competitive position"""
        if not competitor_prices:
            return {}
            
        prices = [p.price for p in competitor_prices if p.price is not None]
        
        if not prices:
            return {}
            
        stats = {
            'our_price': our_price,
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': np.mean(prices),
            'median_price': np.median(prices),
            'price_rank': sorted(prices + [our_price]).index(our_price) + 1,
            'total_competitors': len(prices)
        }
        
        stats['price_difference'] = our_price - stats['avg_price']
        stats['price_ratio'] = our_price / stats['avg_price'] if stats['avg_price'] > 0 else 1.0
        stats['price_position'] = 'Above' if stats['price_ratio'] > 1.0 else 'Below'
        
        return stats
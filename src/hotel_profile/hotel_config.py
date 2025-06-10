from pathlib import Path
import yaml

class HotelProfileManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(Path(__file__).parent.parent.parent / "config" / "config.yaml")
        self._config = self._load_config()
    
    def _load_config(self):
        """Charge la configuration depuis le fichier YAML"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_hotel_info(self):
        """Récupère les informations de l'hôtel"""
        return self._config.get('hotel', {})
    
    def update_hotel_info(self, hotel_data: dict):
        """Met à jour les informations de l'hôtel"""
        if 'hotel' not in self._config:
            self._config['hotel'] = {}
        
        self._config['hotel'].update(hotel_data)
        self._save_config()
    
    def _save_config(self):
        """Sauvegarde la configuration dans le fichier"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, allow_unicode=True)
    
    @property
    def hotel_name(self) -> str:
        return self._config.get('hotel', {}).get('name', 'Hôtel Sans Nom')
    
    @property
    def total_rooms(self) -> int:
        return self._config.get('hotel', {}).get('total_rooms', 0)
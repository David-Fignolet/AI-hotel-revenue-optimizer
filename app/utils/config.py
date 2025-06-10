from pathlib import Path
import yaml
from typing import Dict, Any

class Config:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(Path(__file__).parent.parent.parent / "config" / "config.yaml")
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default=None) -> Any:
        return self._config.get(key, default)
    
    @property
    def llm_config(self) -> Dict[str, Any]:
        return self._config.get('llm', {})
    
    @property
    def hotel_config(self) -> Dict[str, Any]:
        return self._config.get('hotel', {})
    
    def save(self):
        """Sauvegarde la configuration actuelle dans le fichier"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, allow_unicode=True)
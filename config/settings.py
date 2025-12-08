import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
BASE_DIR = Path(__file__).parent.parent
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

class Settings:
    # Telegram
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "tu_token_de_telegram_aqui")
    
    # Odoo APIs
    odoo_api_base_url: str = os.getenv("ODOO_API_BASE_URL", "https://testapi.fiberlux.pe")
    odoo_api_token_servicios: str = os.getenv("ODOO_API_TOKEN_SERVICIOS", "fd90bcba71d83ae05d337f440807357b93ee2b0d2fecc267d61c008720e33eb9")
    odoo_api_token_contratos: str = os.getenv("ODOO_API_TOKEN_CONTRATOS", "3e61666f0d60694fc166b05a23dae2dea45c9851de5e3106717cfd16d3b8a3ea")
    
    # Banco APIs
    bcp_api_url: str = os.getenv("BCP_API_URL", "https://api.fiberlux.pe/bcp/api/v1")
    bbva_api_url: str = os.getenv("BBVA_API_URL", "https://apibco.fiberlux.pe/ce/bbva/v1")
    
    # App
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    timezone: str = os.getenv("TIMEZONE", "America/Lima")
    
    # Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    logs_dir: Path = BASE_DIR / "logs"
    audio_dir: Path = BASE_DIR / "audio"
    
    def __init__(self):
        # Crear directorios
        for directory in [self.data_dir, self.logs_dir, self.audio_dir]:
            directory.mkdir(exist_ok=True, parents=True)

# Instancia global
settings = Settings()

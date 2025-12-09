#!/usr/bin/env python3
"""
RAG-Odoo Bot - Punto de entrada principal
Versión 1.0 - Funcionalidades básicas
"""
import asyncio
import logging
import sys
from pathlib import Path

# Configurar logging básico
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Agregar directorio actual al path para imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

logger = logging.getLogger(__name__)

async def main():
    """Función principal"""
    logger.info("🚀 Iniciando RAG-Odoo Bot v1.0...")
    logger.info(f"📁 Directorio: {current_dir}")
    
    try:
        # Importar y ejecutar bot
        from handlers.telegram_bot import TelegramBot
        bot = TelegramBot()
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Bot detenido por usuario (Ctrl+C)")
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        print(f"\n💡 Posibles soluciones:")
        print("1. Verifica que todos los archivos .py existan")
        print("2. Ejecuta desde el directorio correcto: /home/raguser/rag-odoo")
        print("3. Verifica los imports en los archivos")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

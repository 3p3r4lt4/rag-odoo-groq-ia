import logging
import re
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Configurar logging
logger = logging.getLogger(__name__)

class TelegramBot:
    """Bot de Telegram simplificado para empezar"""
    
    def __init__(self):
        self.application = None
        from services.odoo_client import OdooClient
        self.odoo_client = OdooClient()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /start"""
        welcome = """
🤖 *Bienvenido al Asistente Odoo v1.0*

Conectado a las APIs de Fiberlux. Puedo ayudarte con:

📋 *Consultar servicios* por ID
📄 *Listar contratos* por RUC/DNI
💰 *Consultar deudas* en BCP/BBVA

*Comandos:*
`/start` - Este mensaje
`/help` - Ayuda detallada
`/servicio <ID>` - Consultar servicio
`/contrato <RUC/DNI>` - Listar contratos
`/deuda_bcp <RUC/DNI>` - Deuda BCP

*Ejemplos:*
`/servicio 8812`
`/contrato 20607724050`
`/deuda_bcp 20514326062`

También puedes escribir: "consulta servicio 8812"
"""
        await update.message.reply_text(welcome, parse_mode='Markdown')
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /help"""
        help_text = """
📚 *Comandos disponibles:*

`/start` - Mensaje de bienvenida
`/help` - Esta ayuda
`/servicio <ID> [empresa]` - Consultar servicio
`/contrato <RUC/DNI> [empresa]` - Listar contratos
`/deuda_bcp <RUC/DNI> [PEN/USD]` - Deuda BCP

*Parámetros:*
- `<ID>`: Número de servicio
- `<RUC/DNI>`: 8-11 dígitos
- `[empresa]`: ID empresa (default: 5)
- `[PEN/USD]`: Moneda (default: PEN)

*Formas de usar:*
1. Comandos directos: `/servicio 8812`
2. Texto natural: "consulta el servicio 8812"
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def servicio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Consulta servicio específico"""
        if not context.args:
            await update.message.reply_text("❌ Uso: `/servicio <ID> [empresa_id]`\nEjemplo: `/servicio 8812 5`", parse_mode='Markdown')
            return
            
        service_id = context.args[0]
        company_id = context.args[1] if len(context.args) > 1 else "5"
        
        await update.message.reply_text(f"🔍 Consultando servicio {service_id}...")
        
        try:
            result = await self.odoo_client.consultar_servicios(company_id, service_id)
            formatted = self.odoo_client.format_response(result, "servicio")
            await update.message.reply_text(formatted, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error en servicio_command: {e}")
            await update.message.reply_text(f"❌ Error consultando servicio: {str(e)[:100]}")
    
    async def contrato_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lista contratos de cliente"""
        if not context.args:
            await update.message.reply_text("❌ Uso: `/contrato <RUC/DNI> [empresa_id]`\nEjemplo: `/contrato 20607724050 5`", parse_mode='Markdown')
            return
            
        documento = context.args[0]
        company_id = context.args[1] if len(context.args) > 1 else "5"
        
        await update.message.reply_text(f"📄 Buscando contratos para {documento}...")
        
        try:
            result = await self.odoo_client.listar_contratos(company_id, documento)
            formatted = self.odoo_client.format_response(result, "contrato")
            await update.message.reply_text(formatted, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error en contrato_command: {e}")
            await update.message.reply_text(f"❌ Error buscando contratos: {str(e)[:100]}")
    
    async def deuda_bcp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Consulta deuda BCP"""
        if not context.args:
            await update.message.reply_text("❌ Uso: `/deuda_bcp <RUC/DNI> [PEN/USD]`\nEjemplo: `/deuda_bcp 20514326062 PEN`", parse_mode='Markdown')
            return
            
        documento = context.args[0]
        moneda = context.args[1].upper() if len(context.args) > 1 else "PEN"
        
        if moneda not in ["PEN", "USD"]:
            await update.message.reply_text("❌ Moneda debe ser PEN o USD")
            return
            
        await update.message.reply_text(f"💰 Consultando deuda BCP para {documento} ({moneda})...")
        
        try:
            result = await self.odoo_client.consultar_deuda_bcp(documento, moneda)
            formatted = self.odoo_client.format_response(result, "deuda")
            await update.message.reply_text(formatted, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error en deuda_bcp_command: {e}")
            await update.message.reply_text(f"❌ Error consultando deuda: {str(e)[:100]}")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensajes de texto generales"""
        text = update.message.text
        
        # Convertir a minúsculas para búsqueda
        text_lower = text.lower()
        
        logger.info(f"Mensaje recibido: {text}")
        
        # Detectar patrones simples
        if "servicio" in text_lower:
            # Extraer número de servicio
            numbers = re.findall(r'\d+', text)
            if numbers:
                service_id = numbers[0]
                await update.message.reply_text(f"🔍 Detecté servicio {service_id}. Consultando...")
                
                try:
                    result = await self.odoo_client.consultar_servicios("5", service_id)
                    formatted = self.odoo_client.format_response(result, "servicio")
                    await update.message.reply_text(formatted, parse_mode='Markdown')
                except Exception as e:
                    await update.message.reply_text(f"❌ Error: {str(e)[:100]}")
            else:
                await update.message.reply_text("❌ Necesito el ID del servicio. Ejemplo: 'servicio 8812' o '/servicio 8812'")
                
        elif "contrato" in text_lower or "contratos" in text_lower:
            # Extraer RUC/DNI
            numbers = re.findall(r'\d{8,11}', text)
            if numbers:
                documento = numbers[0]
                await update.message.reply_text(f"📄 Buscando contratos para {documento}...")
                
                try:
                    result = await self.odoo_client.listar_contratos("5", documento)
                    formatted = self.odoo_client.format_response(result, "contrato")
                    await update.message.reply_text(formatted, parse_mode='Markdown')
                except Exception as e:
                    await update.message.reply_text(f"❌ Error: {str(e)[:100]}")
            else:
                await update.message.reply_text("❌ Necesito el RUC o DNI. Ejemplo: 'contratos de 20607724050'")
                
        elif "deuda" in text_lower and "bcp" in text_lower:
            numbers = re.findall(r'\d{8,11}', text)
            if numbers:
                documento = numbers[0]
                moneda = "USD" if "dolar" in text_lower or "usd" in text_lower else "PEN"
                await update.message.reply_text(f"💰 Consultando deuda BCP para {documento}...")
                
                try:
                    result = await self.odoo_client.consultar_deuda_bcp(documento, moneda)
                    formatted = self.odoo_client.format_response(result, "deuda")
                    await update.message.reply_text(formatted, parse_mode='Markdown')
                except Exception as e:
                    await update.message.reply_text(f"❌ Error: {str(e)[:100]}")
            else:
                await update.message.reply_text("❌ Necesito el RUC o DNI. Ejemplo: 'deuda bcp 20514326062'")
                
        else:
            await update.message.reply_text(
                "🤔 Puedo ayudarte con:\n\n"
                "• Consultas de servicios\n"
                "• Listado de contratos\n"
                "• Consultas de deudas BCP\n\n"
                "Escribe algo como:\n"
                "'Consulta el servicio 8812'\n"
                "'Ver contratos de 20607724050'\n"
                "'Deuda BCP 20514326062'\n\n"
                "O usa los comandos: /servicio, /contrato, /deuda_bcp"
            )
    
    async def setup_commands(self):
        """Configurar comandos del bot"""
        commands = [
            BotCommand("start", "Iniciar bot"),
            BotCommand("help", "Ayuda"),
            BotCommand("servicio", "Consultar servicio"),
            BotCommand("contrato", "Listar contratos"),
            BotCommand("deuda_bcp", "Consultar deuda BCP"),
        ]
        try:
            await self.application.bot.set_my_commands(commands)
            logger.info("✅ Comandos configurados en Telegram")
        except Exception as e:
            logger.error(f"Error configurando comandos: {e}")
    
    async def run(self):
        """Ejecutar el bot"""
        from config.settings import settings
        
        logger.info("🤖 Iniciando Telegram Bot...")
        
        if not settings.telegram_token or settings.telegram_token == "tu_token_de_telegram_aqui":
            logger.error("❌ TELEGRAM_TOKEN no configurado en .env")
            print("ERROR: Configura TELEGRAM_TOKEN en el archivo .env")
            print("Edita .env y cambia: TELEGRAM_TOKEN=tu_token_de_telegram_aqui")
            print("por: TELEGRAM_TOKEN=8282995398:AAGt-v0c6e6mXuqPv8YeqrwqDtlJJ0EwV0w")
            return
            
        try:
            self.application = Application.builder().token(settings.telegram_token).build()
            logger.info("✅ Aplicación Telegram creada")
            
            # Handlers de comandos
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("servicio", self.servicio_command))
            self.application.add_handler(CommandHandler("contrato", self.contrato_command))
            self.application.add_handler(CommandHandler("deuda_bcp", self.deuda_bcp_command))
            
            # Handler de mensajes de texto
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
            
            # Configurar comandos en UI
            await self.setup_commands()
            
            logger.info("✅ Bot configurado. Iniciando polling...")
            print("🤖 Bot iniciado. Presiona Ctrl+C para detener.")
            
            # Iniciar
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Mantener bot corriendo
            import asyncio
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"❌ Error iniciando bot: {e}")
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

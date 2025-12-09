from telegram import Update
from telegram.ext import ContextTypes
from services.whisper_service import WhisperService
import logging

logger = logging.getLogger(__name__)

class VoiceHandler:
    def __init__(self, whisper_service: WhisperService):
        self.whisper = whisper_service
    
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar mensajes de voz de Telegram"""
        voice = update.message.voice
        
        # Descargar audio
        voice_file = await voice.get_file()
        audio_bytes = await voice_file.download_as_bytearray()
        
        # Transcribir
        text = self.whisper.transcribe_bytes(audio_bytes)
        
        # Procesar texto con RAG
        # ... tu lógica de RAG aquí ...
        
        await update.message.reply_text(f"Transcripción: {text}")
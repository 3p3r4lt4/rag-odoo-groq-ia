import whisper
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)
        
    def transcribe_audio(self, audio_path: Path) -> str:
        """Transcribe audio file to text"""
        try:
            result = self.model.transcribe(str(audio_path))
            return result["text"]
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""
    
    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = Path(tmp.name)
        
        text = self.transcribe_audio(tmp_path)
        tmp_path.unlink()  # Cleanup
        return text
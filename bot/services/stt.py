import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None

    def load_model(self):
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info(f"Loading Whisper model: {self.model_size}")
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8"
                )
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise

    def transcribe(self, audio_path: str) -> str:
        self.load_model()

        try:
            segments, info = self.model.transcribe(
                audio_path,
                language="es",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            result = " ".join(text_parts)
            logger.info(f"Transcribed: {result[:100]}...")
            return result

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""

    def transcribe_with_info(self, audio_path: str) -> dict:
        self.load_model()

        try:
            segments, info = self.model.transcribe(
                audio_path,
                language="es",
                vad_filter=True
            )

            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            return {
                "text": " ".join(text_parts),
                "language": info.language,
                "language_probability": info.language_probability
            }

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {"text": "", "language": "es", "language_probability": 0}


stt_service = STTService(model_size="base")


def transcribe_local(audio_path: str) -> str:
    return stt_service.transcribe(audio_path)


def transcribe_with_timestamps(audio_path: str) -> dict:
    return stt_service.transcribe_with_info(audio_path)
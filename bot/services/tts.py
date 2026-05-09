import asyncio
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self, voice: str = "es-ES-ElenaNeural"):
        self.voice = voice

    async def synthesize(self, text: str, output_path: str) -> str:
        try:
            import edge_tts
            text = text.strip()
            logger.info(f"TTS input text: '{text[:50]}...' length: {len(text)}")
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            logger.info(f"TTS saved to: {output_path}, size: {file_size} bytes")
            return output_path
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return ""

    async def synthesize_and_convert(self, text: str, output_dir: str) -> str:
        mp3_path = os.path.join(output_dir, "response.mp3")
        opus_path = os.path.join(output_dir, "response.opus")

        await self.synthesize(text, mp3_path)

        if os.path.exists(mp3_path):
            mp3_size = os.path.getsize(mp3_path)
            logger.info(f"MP3 file size: {mp3_size} bytes")
            if mp3_size == 0:
                logger.error("MP3 file is empty, cannot convert")
                return ""
            try:
                import subprocess
                result = subprocess.run(
                    ["ffmpeg", "-y", "-i", mp3_path, "-ac", "libopus", "-b:a", "128k", opus_path],
                    check=True,
                    capture_output=True
                )
                os.remove(mp3_path)
                opus_size = os.path.getsize(opus_path) if os.path.exists(opus_path) else 0
                logger.info(f"Converted to Opus: {opus_path}, size: {opus_size} bytes")
                return opus_path
            except Exception as e:
                logger.warning(f"FFmpeg conversion failed: {e}, returning MP3")
                return mp3_path

        return ""


tts_service = TTSService(voice="es-MX-DaliaNeural")


async def synthesize(text: str, output_path: str) -> str:
    return await tts_service.synthesize(text, output_path)


async def synthesize_to_opus(text: str, output_dir: str) -> str:
    return await tts_service.synthesize_and_convert(text, output_dir)
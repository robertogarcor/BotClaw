import os
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


async def download_voice(bot, file_id: str, output_dir: str = None) -> str:
    if output_dir is None:
        output_dir = tempfile.gettempdir()

    os.makedirs(output_dir, exist_ok=True)

    try:
        file = await bot.get_file(file_id)
        file_path = os.path.join(output_dir, f"voice_{file_id}.ogg")
        await file.download_to_drive(file_path)
        logger.info(f"Voice downloaded to: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to download voice: {e}")
        return ""


async def download_audio(bot, file_id: str, output_dir: str = None) -> str:
    if output_dir is None:
        output_dir = tempfile.gettempdir()

    os.makedirs(output_dir, exist_ok=True)

    try:
        file = await bot.get_file(file_id)
        ext = Path(file.file_path).suffix or ".mp3"
        file_path = os.path.join(output_dir, f"audio_{file_id}{ext}")
        await file.download_to_drive(file_path)
        logger.info(f"Audio downloaded to: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to download audio: {e}")
        return ""


def convert_to_opus(input_path: str, output_path: str = None) -> str:
    if output_path is None:
        output_path = input_path.replace(Path(input_path).suffix, ".opus")

    try:
        import subprocess
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ac", "libopus", "-b:a", "128k", output_path],
            check=True,
            capture_output=True
        )
        logger.info(f"Converted to Opus: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return input_path


def cleanup_temp_files(*files):
    for file_path in files:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")
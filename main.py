from fastapi import FastAPI
import os
import asyncio
import edge_tts
import langdetect
from pydub import AudioSegment
import simpleaudio as sa
import pygame
from pydantic import BaseModel

app = FastAPI()
# Voice mapping for different languages
VOICE_MAPPING = {
    "en": "en-US-JennyNeural",  # English
    "hi": "hi-IN-MadhurNeural",  # Hindi
    "de": "de-DE-KatjaNeural",  # German
    "es": "es-ES-ElviraNeural",  # Spanish
    "fr": "fr-FR-DeniseNeural",   # French
    "gu": "gu-IN-DhwaniNeural", # Gujarati
    "mr": "mr-IN-AarohiNeural", # Marathi
    "ta": "ta-IN-PallaviNeural", # Tamil
    "ar": "ar-DZ-AminaNeural", # Arabic (Algeria)
    "ja": "ja-JP-KeitaNeural", # Japanese
    "ko": "ko-KR-SunHiNeural", # Korean
    "ru": "ru-RU-SvetlanaNeural", # Russian
    "pt": "pt-BR-FranciscaNeural", # Portuguese
    "it": "it-IT-ElsaNeural", # Italian
    "tr": "tr-TR-EmelNeural", # Turkish
    "nl": "nl-NL-ColetteNeural", # Dutch
    "pl": "pl-PL-AgnieszkaNeural", # Polish
    "sv": "sv-SE-HilleviNeural", # Swedish
    "da": "da-DK-ChristelNeural", # Danish
    "no": "nb-NO-IselinNeural", # Norwegian
    "fi": "fi-FI-SelmaNeural", # Finnish
    "hu": "hu-HU-NoemiNeural", # Hungarian
    "cs": "cs-CZ-VlastaNeural", # Czech
    "sk": "sk-SK-LukasNeural", # Slovak
    "el": "el-GR-AthinaNeural", # Greek
    "id": "id-ID-AndikaNeural", # Indonesian
    # "zh": "zh-CN-XiaoxiaoNeural", # Chinese (Simplified)
    # "kn": "kn-IN-SumanNeural", # Kannada
    # "ml": "ml-IN-AshaNeural", # Malayalam
    # "te": "te-IN-VimalaNeural", # Telugu
    # "bn": "bn-IN-ApuNeural", # Bengali
    # "pa": "pa-IN-KaranNeural", # Punjabi
    # "or": "or-IN-UpendraNeural", # Odia

}


class TextInput(BaseModel):
    text: str

# Detect language
def detect_language(text):
    try:
        return langdetect.detect(text)
    except:
        return "en"

# Convert text to speech and save as an audio file
async def text_to_speech(text):
    lang = detect_language(text)
    voice = VOICE_MAPPING.get(lang, "en-US-JennyNeural")

    file_path = "speech.mp3"

    # Ensure old file is deleted before creating a new one
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except PermissionError:
            pass  # File might be in use; let pygame handle it properly

    communicate = edge_tts.Communicate(text, voice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

    return file_path

# Play audio safely
def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Ensure pygame releases the file
    pygame.mixer.music.stop()
    pygame.mixer.quit()

    # Now it's safe to delete the file if needed
    if os.path.exists(file_path):
        os.remove(file_path)


@app.post("/speak/")
async def speak(data: TextInput):
    text = data.text
    audio_file = await text_to_speech(text)
    play_audio(audio_file)
    return {"message": "Speaking..."}


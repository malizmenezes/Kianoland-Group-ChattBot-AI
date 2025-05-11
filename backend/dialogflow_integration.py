from google.cloud import dialogflow
import os
from dotenv import load_dotenv

load_dotenv()

def detect_intent(text, project_id=None, session_id="default", language_code="id"):
    project_id = project_id or os.getenv("DIALOGFLOW_PROJECT_ID")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    # Format response berdasarkan platform
    raw_response = response.query_result.fulfillment_text
    return {
        'raw': raw_response,
        'discord': format_for_discord(raw_response),
        'telegram': format_for_telegram(raw_response),
        'web': format_for_web(raw_response)
    }

def clean_special_chars(text):
    """Bersihkan karakter khusus dari Dialogflow"""
    special_chars = {
        '\b_': '• ',
        '\\n': '\n',
        '\\"': '"',
        # Tambahkan karakter lain yang perlu dibersihkan
    }
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    return text

def format_for_discord(text):
    """Format untuk Discord (menggunakan Markdown)"""
    # Bersihkan karakter khusus terlebih dahulu
    text = clean_special_chars(text)
    
    # Ganti placeholder dengan markdown bold
    text = text.replace('bold_start', '**').replace('bold_end', '**')
    
    # Pastikan newlines bekerja dengan benar
    text = text.replace('\\n', '\n')
    
    return text

def format_for_telegram(text):
    """Format untuk Telegram (menggunakan HTML)"""
    # Ganti **teks** dengan <b>teks</b>
    return text.replace('**', '').replace('bold_start', '<b>').replace('bold_end', '</b>')

def format_for_web(text):
    """Format untuk Web (menggunakan HTML)"""
    # Ganti **teks** dengan <strong>teks</strong>
    return text.replace('**', '').replace('bold_start', '<strong>').replace('bold_end', '</strong>')
import os
from models.speech_to_text import transcribe_audio
from models.summarizer import summarize_text

def process_audio(file_path):
    """
    Process the uploaded audio file: transcribe and summarize.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        tuple: Transcription and summary of the audio.
    """
    try:
        # Transcribe the audio file
        transcription = transcribe_audio(file_path)

        # Summarize the transcription
        summary = summarize_text(transcription)

        return transcription, summary
    except Exception as e:
        print(f"An error occurred during audio processing: {e}")
        return None, None

def save_uploaded_file(uploaded_file, upload_folder='uploads'):
    """
    Save the uploaded audio file to the specified folder.

    Args:
        uploaded_file: The uploaded file object.
        upload_folder (str): The folder where the file will be saved.

    Returns:
        str: The path of the saved file.
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_path = os.path.join(upload_folder, uploaded_file.filename)
    uploaded_file.save(file_path)
    return file_path

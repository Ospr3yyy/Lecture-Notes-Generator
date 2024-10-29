from transformers import pipeline
import torch
import sys

# Initialize the Speech-to-Text pipeline
# If using GPU, check if a CUDA device is available
device = 0 if torch.cuda.is_available() else -1
speech_to_text_pipeline = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-large-960h", device=device)

def transcribe_audio(file_path):
    """
    Transcribes audio file to text.
    
    Args:
        file_path (str): Path to the audio file (.wav format recommended).
        
    Returns:
        str: Transcribed text.
    """
    with open(file_path, 'rb') as audio_file:
        transcription = speech_to_text_pipeline(audio_file)
    return transcription['text']

if __name__ == "__main__":
    # Example usage: python speech_to_text.py path/to/audiofile.wav
    if len(sys.argv) < 2:
        print("Usage: python speech_to_text.py path/to/audiofile.wav")
        sys.exit(1)
    
    audio_file_path = sys.argv[1]
    try:
        transcribed_text = transcribe_audio(audio_file_path)
        print("Transcription:\n", transcribed_text)
    except Exception as e:
        print(f"An error occurred: {e}")

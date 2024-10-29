import re
import string

def clean_text(text):
    """
    Clean the input text by removing unwanted characters and formatting.

    Args:
        text (str): The text to clean.

    Returns:
        str: Cleaned text.
    """
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def tokenize_text(text):
    """
    Tokenize the cleaned text into words.

    Args:
        text (str): The cleaned text.

    Returns:
        list: List of words (tokens).
    """
    return text.split()

def process_text(text):
    """
    Process the input text: clean and tokenize.

    Args:
        text (str): The input text to process.

    Returns:
        list: List of cleaned and tokenized words.
    """
    cleaned_text = clean_text(text)
    tokens = tokenize_text(cleaned_text)
    return tokens

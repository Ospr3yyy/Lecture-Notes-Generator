from transformers import pipeline
import sys

# Initialize the Summarization pipeline
summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    """
    Summarizes the input text.
    
    Args:
        text (str): Text to be summarized.
        
    Returns:
        str: Summarized text.
    """
    summary = summarization_pipeline(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

if __name__ == "__main__":
    # Example usage: python summarizer.py "Your lengthy text here."
    if len(sys.argv) < 2:
        print("Usage: python summarizer.py 'Your lengthy text here.'")
        sys.exit(1)

    # Join all arguments to handle spaces in input text
    input_text = ' '.join(sys.argv[1:])
    
    try:
        summarized_text = summarize_text(input_text)
        print("Summary:\n", summarized_text)
    except Exception as e:
        print(f"An error occurred: {e}")

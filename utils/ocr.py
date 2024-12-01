import pytesseract
from PIL import Image
from transformers import pipeline

# Configure Tesseract path if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load Hugging Face text classifier
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

# Expense categories
categories = ['groceries', 'utilities', 'entertainment', 'transportation', 'restaurants', 'healthcare', 'others']

def extract_and_classify_expense(image_file):
    try:
        img = Image.open(image_file)
        extracted_text = pytesseract.image_to_string(img)
        classification = classifier(extracted_text, candidate_labels=categories)
        predicted_category = classification['labels'][0]
        return extracted_text, predicted_category
    except Exception as e:
        return f"Error occurred: {str(e)}", None

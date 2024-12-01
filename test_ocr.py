from utils.ocr import extract_text_from_image

# Path to the test image
image_path = 'uploads/bi2.webp'  # Replace with the correct path

# Extract the text and display the extracted fields
result = extract_text_from_image(image_path)
print("OCR Extracted Data:")
print(f"Amount: {result['amount']}")
print(f"Description: {result['description']}")
print(f"Date: {result['date']}")

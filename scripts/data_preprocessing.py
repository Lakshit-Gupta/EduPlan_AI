import fitz
import re
import json
import os

def extract_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = []
        for page in doc:
            page_text = page.get_text()
            if not page_text.strip():
                print(f"Warning: Page {page.number + 1} in {pdf_path} is empty or has no extractable text.")
            text.append(page_text)
        doc.close()
        full_text = "\n".join(text)
        if not full_text.strip():
            print(f"Warning: Entire document {pdf_path} has no extractable text.")
        return full_text
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return ""

# (Keep other functions the same)

def convert_pdf_to_json(pdf_path):
    text = extract_text(pdf_path)
    if not text:
        return []  # No text to process

    chapters = split_chapters(text)
    structured = []
    for i, ch_text in enumerate(chapters[1:], 1):
        ch = {
            'chapter_number': i,
            'activities': extract_activities(ch_text),
            'questions': extract_questions(ch_text),
            'raw_text_snippet': ch_text[:200]
        }
        structured.append(ch)
    return structured

# Rest of your code...

# This will help you identify which PDFs or pages have no text and avoid empty output.

# If your PDFs are scanned images, consider running OCR (with Tesseract or equivalent) before extraction.

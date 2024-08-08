import fitz

def extract_text_from_pdf(pdf_file_path):
    try:
        doc = fitz.open(pdf_file_path)
        pdf_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pdf_text += page.get_text("text")
        doc.close()
        return pdf_text
    except Exception as e:
        return f"Error extracting text: {e}"
    
pdf_path = "Landon-Hotel.pdf"
extracted_text = extract_text_from_pdf(pdf_path)

file = open("pdf_text", "w", encoding='utf-8')
file.write(extracted_text)

import pymupdf

def extract_pdf_text(upload_file):
    pdf_bytes = upload_file.read()
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    text = ""

    # Iterating through each page of the resume and extracting the text
    for page in doc:
        text += page.get_text()
    doc.close()
    return text
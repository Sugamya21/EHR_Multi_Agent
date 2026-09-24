import sys
from pypdf import PdfReader


def extract_text(pdf_path):

    reader = PdfReader(pdf_path)

    extracted_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text += text + "\n"

    return extracted_text


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("python scripts/extract_pdf.py <path-to-pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    text = extract_text(pdf_path)

    print("\n========== EXTRACTED PDF TEXT ==========\n")
    print(text)
    print("\n=========================================\n")
from docx import Document
import os

# Folders
INPUT_DIR = "data/input"
OUTPUT_DIR = "data/processed"

# Ensure output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_text_from_docx(file_path):
    """Extract text from a .docx file"""
    doc = Document(file_path)
    text_parts = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text.strip())

    return "\n".join(text_parts)


def process_documents():
    """Process all DOCX files in input folder"""
    files = os.listdir(INPUT_DIR)

    if not files:
        print("No files found in data/input/")
        return

    for file_name in files:
        if file_name.endswith(".docx"):
            input_path = os.path.join(INPUT_DIR, file_name)

            print(f"Processing: {file_name}")

            text = extract_text_from_docx(input_path)

            output_file = file_name.replace(".docx", ".txt")
            output_path = os.path.join(OUTPUT_DIR, output_file)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"Saved: {output_path}")


if __name__ == "__main__":
    process_documents()
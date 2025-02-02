# services.py
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from docx import Document
import io
from io import BytesIO
import google.generativeai as genai
import os

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB in bytes
ALLOWED_CODE_EXTENSIONS = [".java"]  # Change to Java
ALLOWED_NON_CODE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".pdf", ".docx", ".txt"]

# Configure Gemini model
os.environ["API_KEY"] = "AIzaSyARlq_4JmeSD4FVt3xEYzo1s40Bck7o8XY"
genai.configure(api_key=os.environ["API_KEY"])
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def process_input(file_content: bytes = None, filename: str = None, code_snippet: str = None) -> dict:
    if not file_content and not code_snippet:
        raise ValueError("No input provided. Please upload a file or paste a code snippet.")

    all_text = ""

    if file_content and filename:
        file_extension = os.path.splitext(filename)[1].lower()  # Handle file extension case
        if file_extension in ALLOWED_CODE_EXTENSIONS:
            all_text += handle_code_file(file_content, filename)
        elif file_extension in ALLOWED_NON_CODE_EXTENSIONS:
            all_text += handle_non_code_file(file_content, file_extension)
        else:
            raise ValueError(f"Unsupported file type: {filename}")

    if code_snippet:
        all_text += code_snippet.strip()

    refined_text = filter_text_with_gemini(all_text)
    return {"refined_text": refined_text}

def handle_code_file(file_content: bytes, filename: str) -> str:
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(f"File {filename} exceeds the maximum size of 5 MB")

    file_content = file_content.decode('utf-8', errors='ignore')
    validation_result = check_file_empty_or_invalid_code(file_content, filename)
    if "empty" in validation_result or "invalid" in validation_result:
        raise ValueError(f"{filename}: {validation_result}")

    return file_content

def handle_non_code_file(file_content: bytes, file_extension: str) -> str:
    if file_extension == ".pdf":
        return extract_text_from_pdf(BytesIO(file_content))
    elif file_extension == ".docx":
        return extract_text_from_docx(BytesIO(file_content))
    elif file_extension in [".png", ".jpg", ".jpeg", ".gif"]:
        image = Image.open(BytesIO(file_content))
        return extract_text_from_image(image)
    return ""

def extract_text_from_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    text = ""
    pdf_document = fitz.open(stream=pdf_file, filetype="pdf")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(BytesIO(image_bytes))
            text += extract_text_from_image(image)
    return text

def extract_text_from_docx(docx_file: BytesIO) -> str:
    text = ""
    doc = Document(docx_file)
    for para in doc.paragraphs:
        text += para.text + "\n"
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_stream = io.BytesIO(rel.target_part.blob)
            image = Image.open(image_stream)
            text += extract_text_from_image(image)
    return text

def check_file_empty_or_invalid_code(file_content: str, file_type: str) -> str:
    if not file_content.strip():
        return "The file is empty."

    prompt = (
        f"You are an assistant designed to validate code files. Please check the following file:\n\n"
        f"File Type: {file_type}\n"
        f"Content:\n{file_content}\n\n"
        "If the code is invalid or does not match the file type, respond with 'The code is invalid for this file type.'\n"
        "Otherwise, respond with 'The code is valid.'"
    )

    response = gemini_model.generate_content(prompt)
    return response.text.strip()

def filter_text_with_gemini(text: str) -> str:
    try:
        # Simple pre-filtering to check for common Java patterns
        if not any(keyword in text for keyword in ["class", "public", "private", "void", "static", "import"]):
            return "No Java code snippets were found in the provided text."

        analysis_prompt = (
            "You are a specialized assistant designed to extract code snippets written in Java Programming Language from mixed content. "
            "Given the following text which may include explanations, documentation, and code snippets, extract only the code snippets written in Java. "
            "Please ignore any non-Java content. The text may include other programming languages or non-code text.\n\n"
            f"{text}\n\n"
            "Extract only the Java code snippets, ensuring the output is clean and well-formatted. If no Java code is found, respond with 'No Java code snippets found.'"
        )

        response = gemini_model.generate_content(analysis_prompt)
        if response and response.text:
            extracted_code = response.text.strip()
            if "No Java code snippets found." in extracted_code:
                return "No Java code snippets were found in the provided text."
            if not extracted_code:
                return "No code snippets were found in the provided text."
            return extracted_code
        return "An error occurred while extracting code. Please try again."
    except Exception as e:
        return f"An error occurred while filtering code: {str(e)}"

